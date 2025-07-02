from fastapi import APIRouter

router = APIRouter()

@router.get("/api/greeting")
async def greeting():
    """summary: Get a greeting message.
description: Returns a friendly greeting from the car assistant."""
    return {"message": "👋 Hello! My name is **Mousa3id**, your car recommendation assistant. How can I help you find your perfect car today? "} 