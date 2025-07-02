# import aiohttp  # Remove this line until a real API call is implemented

class ConversationFlowManager:
    def __init__(self):
        pass

    def get_next_action(self, user_profile, user_message, recommended_cars):
        missing = [k for k in ["location", "age", "budget", "usage"] if not user_profile.get(k)]
        if missing:
            return {"action": "ask_missing_info", "data": {"missing": missing}}
        if user_profile.get("test_drive_agreed") and not user_profile.get("phone_number"):
            return {"action": "ask_contact_info", "data": {"type": "phone_number"}}
        if user_profile.get("phone_number") and not user_profile.get("email"):
            return {"action": "ask_contact_info", "data": {"type": "email"}}
        if user_profile.get("email") and not user_profile.get("name"):
            return {"action": "ask_contact_info", "data": {"type": "name"}}
        if user_profile.get("name") and not user_profile.get("test_drive_date"):
            return {"action": "ask_contact_info", "data": {"type": "test_drive_date"}}
        if user_profile.get("name") and user_profile.get("test_drive_date") and not user_profile.get("confirmation_sent"):
            return {"action": "ask_confirmation", "data": {}}
        if all(user_profile.get(k) is not None for k in ['location', 'budget', 'usage']) and bool(recommended_cars):
            return {"action": "provide_recommendation", "data": {}}
        return {"action": "end", "data": {}}

conversation_flow_manager = ConversationFlowManager()

def get_next_question(user_profile, perfect_car_found=True):
    missing = [k for k in ["location", "age", "budget", "usage"] if not user_profile.get(k)]
    if missing:
        return "Could you please tell me your: <br>" + "<br> ".join([f"<strong>*{item}</strong>" for item in missing]) + "?"
    if user_profile.get("test_drive_agreed") and not user_profile.get("phone_number"):
        return "Fantastic! Could you please provide your <strong>phone number</strong> so we can arrange the test drive?"
    if user_profile.get("phone_number") and not user_profile.get("email"):
        return "And your <strong>Email</strong> address, please?"
    if user_profile.get("email") and not user_profile.get("name"):
        return "Fantastic! Could you please provide your <strong>Name</strong> so we can arrange the test drive?"
    if user_profile.get("name") and not user_profile.get("test_drive_date"):
        return "Cool, when do you want me to book a <strong>Test drive</strong> for you?"
    if user_profile.get("name") and user_profile.get("test_drive_date") and not user_profile.get("confirmation_sent"):
        return f"""Please confirm your information:\n
        Name: {user_profile.get('name', 'N/A')}\n
        Location: {user_profile.get('location', 'N/A')}\n
        Age: {user_profile.get('age', 'N/A')}\n
        Budget: {user_profile.get('budget', 'N/A')}\n
        Usage: {user_profile.get('usage', 'N/A')}\n
        Phone: {user_profile.get('phone_number', 'N/A')}\n
        Email: {user_profile.get('email', 'N/A')}\n
        Test drive status:{user_profile.get('test_drive_status', 'N/A')}\n
        Test drive date:{user_profile.get('test_drive_date', 'N/A')}\n
        Is this information correct? (Yes/No) If not, please tell me what needs to be changed."""
    return None 

