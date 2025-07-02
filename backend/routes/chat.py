import uuid
import re
import json
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from backend.models import ChatRequest
from backend.db import get_conversation_history, add_to_history, get_db_pool
from backend.services.user_profile import UserProfileManager
from backend.services.recommendation import RecommendationService
from backend.services.email import send_email_confirmation
from backend.services.conversation import get_next_question
from backend.utils import convert_decimals
from backend.config import settings
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader, select_autoescape
import google.api_core.exceptions

router = APIRouter()

# Gemini API setup
if not settings.GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Jinja2 environment for prompt templates
prompt_env = Environment(
    loader=FileSystemLoader("prompts"),
    autoescape=select_autoescape()
)

def parse_budget(budget):
    if not budget:
        return None
    match = re.search(r"([\d,.]+)\s*([kKmM]?)", str(budget))
    if match:
        num = float(match.group(1).replace(",", ""))
        mult = {'k': 1_000, 'm': 1_000_000}.get(match.group(2).lower(), 1)
        return num * mult
    return None

async def extract_user_info(model, prompt, session_id):
    logging.info(f"LLM info extraction input (session_id={session_id}): {prompt[:500]}...")
    try:
        info_response = model.generate_content(contents=[{"parts": [{"text": prompt}]}])
        info_text = info_response.text.strip()
        if "```json" in info_text:
            info_text = info_text.split("```json")[1]
        if "```" in info_text:
            info_text = info_text.split("```", 1)[0]
        info_text = info_text.strip()
        logging.info(f"LLM info extraction output (session_id={session_id}): {info_text[:500]}...")
        return json.loads(info_text)
    except Exception as e:
        logging.error(f"LLM info extraction error (session_id={session_id}): {e}")
        return {}

def build_history_context(history):
    recent = history[-20:] if len(history) > 2 else history
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])

def build_info_extraction_prompt(history_context, user_message, user_profile):
    return (
        f"You are Mousa3id, a smart, multilingual car recommendation assistant. "
        f"Detect the language used by the user and always respond in that language. "
        f"Analyze the entire conversation and extract all user information you can infer so far.\n\n"
        f"Conversation so far:\n{history_context}\n\n"
        f"Latest customer message: {user_message}\n"
        f"Current user profile:\n{json.dumps(convert_decimals(user_profile), indent=2)}\n"
        f"Extract and return a JSON object with the following fields, using null for anything you cannot infer:\n"
        f"1. Name\n"
        f"2. Location\n"
        f"3. Age\n"
        f"4. Budget (in numbers)\n"
        f"5. Usage needs\n"
        f"6. Preferences\n"
        f"7. Requirements\n"
        f"8. Test drive agreement\n"
        f"9. Phone number\n"
        f"10. Email\n"
        f"11. Test drive date\n"
    )

def build_recommended_cars_text(recommended_cars):
    if not recommended_cars:
        return "No cars found yet"
    return "\n\n".join([
        f"- **Product (car) Name: {car.name}**\n"
        f"description: {car.description}\n"
        f"price: ${car.price:.2f}\n"
        f"colors available: {car.color or 'N/A'}\n"
        f"max_speed: {car.max_speed or 'N/A'} km/h\n"
        f"consumption: {car.consumption or 'N/A'} L/100km"
        for car in recommended_cars
    ])

def build_response_prompt(history_context, user_message, user_profile, recommended_cars_text, greet_instruction, next_question, perfect_car_found, user_language=None):
    language_instruction = (
        f"Always respond in {user_language}." if user_language else
        "Detect the language used by the user in the latest message and always respond in that language."
    )
    return (
        f"You are a salesman named Mousaid, a warm, friendly, and knowledgeable assistant who helps users choose the right products by asking smart questions and offering relevant suggestions.\n"
        f"{language_instruction}\n"
        f"Previous conversation:\n{history_context}\n"
        f"Latest customer message: {user_message}\n"
        f"Current user profile:\n{json.dumps(convert_decimals(user_profile), indent=2)}\n"
        f"Available cars in our Shop:\n{recommended_cars_text}\n"
        f"Based on the above, please provide a response that:\n"
        f"1. If user message not English, ONLY respond with detected user language.\n"
        f"2. Only translate and include: '{greet_instruction}' or '{next_question}' if they haven't been shown before.\n"
        f"3. Translate {greet_instruction}, {next_question} to the user's detected language.\n"
        f"4. Do NOT repeat or summarize user's previous answers.\n"
        f"5. If user has mentioned any preferred cars ({user_profile['preferred_cars']}), check if they exist in the database. If yes, explain how they match. If not, inform user. Suggest close alternatives if needed.\n"
        f"6. ONLY if perfect car is found ({user_profile['perfect_car_found']}), ask for a test drive if not yet agreed.\n"
        f"7. ONLY if test drive not agreed yet ({not user_profile['has_agreed_to_test_drive']}) AND perfect car is found, ask \"{next_question}\".\n"
        f"8. Be respectful and conversational. Use emojis 🎉😊.\n"
        f"9. If user's budget ({user_profile['budget']} {user_profile['currency']}) is lower than database car prices, suggest close alternatives and explain why.\n"
        f"10. Detect user input currency and convert car price from database to  user currency if needed to match results.\n"
        f"11. Show empathy and understanding.\n"
        f"12. Ask if user needs more details on any car. Do not mention insurance or monetizing.\n"
        f"13. If user already provided budget, preferred cars, or color/speed/etc., do not ask again. Use existing profile data.\n"
        f"14. Keep response concise but informative."
    )

@router.post("/chat")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
):
    db_pool = get_db_pool()
    user_profile_manager = UserProfileManager(db_pool)
    recommendation_service = RecommendationService(db_pool)
    session_id = request.session_id or str(uuid.uuid4())
    try:
        history = await get_conversation_history(session_id)
        user_profile = await user_profile_manager.get_user_profile(session_id)
    except Exception as e:
        logging.error(f"DB error (session_id={session_id}): {e}")
        raise HTTPException(status_code=500, detail="Database error")

    if not request.messages:
        return JSONResponse(content={"response": "", "session_id": session_id})

    user_message = request.messages[-1].content
    await add_to_history(session_id, "user", user_message)
    logging.info(f"User message (session_id={session_id}): {user_message}")

    user_language = request.language if request.language else None
    history_context = build_history_context(history)
    info_extraction_prompt = build_info_extraction_prompt(history_context, user_message, user_profile)
    new_info = await extract_user_info(model, info_extraction_prompt, session_id)
    if 'budget' in new_info:
        new_info['budget'] = parse_budget(new_info['budget'])
    # Only keep keys that are valid DB columns
    valid_columns = {
        "name", "location", "age", "budget", "usage", "preferences", "requirements",
        "test_drive_agreed", "phone_number", "email", "confirmation_sent",
        "test_drive_status", "test_drive_date", "perfect_car_found", "has_agreed_to_test_drive"
    }
    # Map 'needs' to 'usage' if present
    if 'needs' in new_info and 'usage' not in new_info:
        new_info['usage'] = new_info.pop('needs')
    # Remove any keys not in valid_columns
    new_info = {k: v for k, v in new_info.items() if k in valid_columns}
    await user_profile_manager.update_user_profile(session_id, new_info)
    user_profile = await user_profile_manager.get_user_profile(session_id)

    # --- State-aware logic: ensure all keys exist and are up to date ---
    # Set default values for keys if missing
    for k, v in {
        'preferred_cars': [],
        'budget': None,
        'currency': 'USD',
        'perfect_car_found': False,
        'has_agreed_to_test_drive': False
    }.items():
        if k not in user_profile:
            user_profile[k] = v
    # perfect_car_found: True if all required fields and recommendations exist
    recommended_cars = await recommendation_service.get_car_recommendations(user_profile)
    user_profile['perfect_car_found'] = all(user_profile.get(k) is not None for k in ['location', 'budget', 'usage']) and bool(recommended_cars)
    # has_agreed_to_test_drive: True if test_drive_agreed or test_drive_status is True
    user_profile['has_agreed_to_test_drive'] = bool(user_profile.get('test_drive_agreed') or user_profile.get('test_drive_status'))
    # Save these fields to DB for future state
    await user_profile_manager.update_user_profile(session_id, {
        'perfect_car_found': user_profile['perfect_car_found'],
        'has_agreed_to_test_drive': user_profile['has_agreed_to_test_drive']
    })

    if user_profile.get("phone_number") and user_profile.get("email") and not user_profile.get("confirmation_sent"):
        if "yes" in user_message.lower():
            await user_profile_manager.update_user_profile(session_id, {"confirmation_sent": True})
            latest_profile = await user_profile_manager.get_user_profile(session_id)
            logging.info(f"Attempting to send confirmation email to {latest_profile.get('email')} (session_id={session_id})")
            background_tasks.add_task(send_email_confirmation, latest_profile)
            response_text = "Thank you for confirming! I have sent your test drive schedule confirmation to your email. Is there anything else I can help you with?"
            await add_to_history(session_id, "assistant", response_text)
            return JSONResponse(content={"response": response_text, "session_id": session_id})
        elif "no" in user_message.lower():
            await user_profile_manager.update_user_profile(session_id, {"phone_number": None, "email": None})
            response_text = "Can you please give me your email and phone number?"
            await add_to_history(session_id, "assistant", response_text)
            return JSONResponse(content={"response": response_text, "session_id": session_id})

    # If the LLM extracts test_drive_agreed as True, handle accordingly
    if new_info.get('test_drive_agreed') is True:
        await user_profile_manager.update_user_profile(session_id, {'test_drive_agreed': True})
        user_profile = await user_profile_manager.get_user_profile(session_id)
        response_text = (
            "Thank you for agreeing to a test drive! We will send you an email with the details shortly. "
            "Would you also like to provide your phone number and email to confirm your booking?"
        )
        await add_to_history(session_id, "assistant", response_text)
        return JSONResponse(content={"response": response_text, "session_id": session_id})

    next_question = get_next_question(user_profile, user_profile['perfect_car_found'])
    recommended_cars_text = build_recommended_cars_text(recommended_cars)
    greet_instruction = "If this is the first message, greet the user." if not history_context.strip() else ""
    response_prompt = build_response_prompt(
        history_context, user_message, user_profile, recommended_cars_text, greet_instruction, next_question, user_profile['perfect_car_found'], user_language
    )
    try:
        response = model.generate_content(
            contents=[{"parts": [{"text": response_prompt}]}]
        )
        response_text = response.text.strip()
        await add_to_history(session_id, "assistant", response_text)
        return JSONResponse(content={"response": response_text, "session_id": session_id})
    except google.api_core.exceptions.ResourceExhausted as e:
        logging.error(f"Gemini API quota exceeded: {e}")
        return JSONResponse(
            status_code=429,
            content={"response": "Sorry, the AI assistant has reached its usage limit for now. Please try again later.", "session_id": session_id}
        )
    except Exception as e:
        import traceback
        logging.error("Unhandled exception in /chat: %s", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"response": "Internal server error. Please try again later.", "session_id": session_id}
        ) 