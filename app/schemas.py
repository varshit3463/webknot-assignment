from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class CollegeCreate(BaseModel):
    name: str

class CollegeOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    college_id: int
    roll_number: str
    name: str
    email: EmailStr

class StudentOut(BaseModel):
    id: int
    college_id: int
    roll_number: str
    name: str
    email: EmailStr
    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    college_id: int
    title: str
    event_type: str  # Workshop/Hackathon/Seminar/Fest
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class EventOut(BaseModel):
    id: int
    college_id: int
    title: str
    event_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    student_id: int

class AttendanceRequest(BaseModel):
    student_id: int
    status: str = "present"

class FeedbackRequest(BaseModel):
    student_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class EventStats(BaseModel):
    event_id: int
    registrations: int
    attendance_count: int
    attendance_percentage: float
    average_feedback: Optional[float]

class StudentParticipation(BaseModel):
    student_id: int
    name: str
    events_attended: int
