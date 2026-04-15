from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class Admin(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    email: str
    password: str

class AdminCreate(BaseModel):
    username: str
    email: str
    password: str

class SyllabusItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    department: str
    semester: int
    subject_name: str
    subject_code: str
    credits: int
    topics: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SyllabusCreate(BaseModel):
    department: str
    semester: int
    subject_name: str
    subject_code: str
    credits: int
    topics: List[str]

class Faculty(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    designation: str
    department: str
    qualification: str
    email: str
    phone: str
    image_url: str
    experience_years: int
    specialization: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FacultyCreate(BaseModel):
    name: str
    designation: str
    department: str
    qualification: str
    email: str
    phone: str
    image_url: str
    experience_years: int
    specialization: str

class SeatAvailability(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    department: str
    total_seats: int
    filled_seats: int
    available_seats: int
    cap_round: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SeatUpdate(BaseModel):
    department: str
    total_seats: int
    filled_seats: int
    cap_round: str

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Auth Routes
@api_router.post("/auth/login")
async def login(credentials: AdminLogin):
    admin = await db.admins.find_one({"email": credentials.email}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(credentials.password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "admin": {"id": admin['id'], "username": admin['username'], "email": admin['email']}}

@api_router.post("/auth/register", response_model=Admin)
async def register(admin_data: AdminCreate):
    existing = await db.admins.find_one({"email": admin_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = bcrypt.hashpw(admin_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin = Admin(username=admin_data.username, email=admin_data.email)
    doc = admin.model_dump()
    doc['password_hash'] = password_hash
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.admins.insert_one(doc)
    return admin

# Syllabus Routes
@api_router.get("/syllabus", response_model=List[SyllabusItem])
async def get_syllabus(department: Optional[str] = None, semester: Optional[int] = None):
    query = {}
    if department:
        query['department'] = department
    if semester:
        query['semester'] = semester
    
    items = await db.syllabus.find(query, {"_id": 0}).to_list(1000)
    for item in items:
        if isinstance(item['created_at'], str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
    return items

@api_router.post("/syllabus", response_model=SyllabusItem)
async def create_syllabus(item: SyllabusCreate):
    syllabus = SyllabusItem(**item.model_dump())
    doc = syllabus.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.syllabus.insert_one(doc)
    return syllabus

@api_router.put("/syllabus/{item_id}", response_model=SyllabusItem)
async def update_syllabus(item_id: str, item: SyllabusCreate):
    result = await db.syllabus.find_one({"id": item_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Syllabus item not found")
    
    update_data = item.model_dump()
    await db.syllabus.update_one({"id": item_id}, {"$set": update_data})
    
    updated = await db.syllabus.find_one({"id": item_id}, {"_id": 0})
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return SyllabusItem(**updated)

@api_router.delete("/syllabus/{item_id}")
async def delete_syllabus(item_id: str):
    result = await db.syllabus.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Syllabus item not found")
    return {"message": "Syllabus item deleted"}

# Faculty Routes
@api_router.get("/faculty", response_model=List[Faculty])
async def get_faculty(department: Optional[str] = None):
    query = {}
    if department:
        query['department'] = department
    
    faculty = await db.faculty.find(query, {"_id": 0}).to_list(1000)
    for f in faculty:
        if isinstance(f['created_at'], str):
            f['created_at'] = datetime.fromisoformat(f['created_at'])
    return faculty

@api_router.post("/faculty", response_model=Faculty)
async def create_faculty(faculty_data: FacultyCreate):
    faculty = Faculty(**faculty_data.model_dump())
    doc = faculty.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.faculty.insert_one(doc)
    return faculty

@api_router.put("/faculty/{faculty_id}", response_model=Faculty)
async def update_faculty(faculty_id: str, faculty_data: FacultyCreate):
    result = await db.faculty.find_one({"id": faculty_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    update_data = faculty_data.model_dump()
    await db.faculty.update_one({"id": faculty_id}, {"$set": update_data})
    
    updated = await db.faculty.find_one({"id": faculty_id}, {"_id": 0})
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return Faculty(**updated)

@api_router.delete("/faculty/{faculty_id}")
async def delete_faculty(faculty_id: str):
    result = await db.faculty.delete_one({"id": faculty_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"message": "Faculty deleted"}

# Seat Availability Routes
@api_router.get("/seats", response_model=List[SeatAvailability])
async def get_seats():
    seats = await db.seats.find({}, {"_id": 0}).to_list(1000)
    for seat in seats:
        if isinstance(seat['updated_at'], str):
            seat['updated_at'] = datetime.fromisoformat(seat['updated_at'])
    return seats

@api_router.post("/seats", response_model=SeatAvailability)
async def update_seats(seat_data: SeatUpdate):
    existing = await db.seats.find_one({"department": seat_data.department, "cap_round": seat_data.cap_round}, {"_id": 0})
    
    available = seat_data.total_seats - seat_data.filled_seats
    seat = SeatAvailability(
        department=seat_data.department,
        total_seats=seat_data.total_seats,
        filled_seats=seat_data.filled_seats,
        available_seats=available,
        cap_round=seat_data.cap_round
    )
    
    if existing:
        await db.seats.update_one(
            {"department": seat_data.department, "cap_round": seat_data.cap_round},
            {"$set": seat.model_dump()}
        )
    else:
        doc = seat.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.seats.insert_one(doc)
    
    return seat

# Chat Routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_jarvis(request: ChatRequest):
    # Get context from database
    syllabus = await db.syllabus.find({}, {"_id": 0}).to_list(100)
    faculty = await db.faculty.find({}, {"_id": 0}).to_list(100)
    seats = await db.seats.find({}, {"_id": 0}).to_list(100)
    
    # Build context for AI
    context = f"""You are Jarvis, an AI assistant for PLITMS (Polytechnic Institute). 
    You help students with information about diploma admissions, syllabus, and faculty.
    
    Available Departments and Syllabus:
    {syllabus}
    
    Faculty Information:
    {faculty}
    
    CAP Admission Seat Availability:
    {seats}
    
    Answer the student's question helpfully and accurately based on this information.
    """
    
    # Create LLM chat
    chat = LlmChat(
        api_key=os.environ.get('EMERGENT_LLM_KEY'),
        session_id=request.session_id,
        system_message=context
    ).with_model("openai", "gpt-5.2")
    
    # Send message
    user_message = UserMessage(text=request.message)
    ai_response = await chat.send_message(user_message)
    
    # Save to database
    chat_msg = ChatMessage(
        session_id=request.session_id,
        user_message=request.message,
        ai_response=ai_response
    )
    doc = chat_msg.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.chat_messages.insert_one(doc)
    
    return ChatResponse(response=ai_response, session_id=request.session_id)

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    messages = await db.chat_messages.find({"session_id": session_id}, {"_id": 0}).sort("timestamp", 1).to_list(1000)
    for msg in messages:
        if isinstance(msg['timestamp'], str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    return messages

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
