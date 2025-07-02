from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None
    language: Optional[str] = None  # This is the language selector from frontend

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    color: Optional[str]
    max_speed: Optional[float]
    consumption: Optional[float] 