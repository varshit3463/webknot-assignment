from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select, text
from typing import List, Optional
from .database import Base, engine, get_db
from . import models, schemas


app = FastAPI(title="Campus Event Reporting Prototype", version="1.0.0")

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["health"])
def health():
    return {"ok": True}

# ---------- CRUD: Colleges, Students, Events ----------

@app.post("/colleges", response_model=schemas.CollegeOut, tags=["colleges"])
def create_college(payload: schemas.CollegeCreate, db: Session = Depends(get_db)):
    c = models.College(name=payload.name)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.post("/students", response_model=schemas.StudentOut, tags=["students"])
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    # enforce unique roll per college
    exists = db.execute(select(models.Student).where(
        models.Student.college_id==payload.college_id,
        models.Student.roll_number==payload.roll_number
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Duplicate roll_number for this college")
    s = models.Student(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@app.post("/events", response_model=schemas.EventOut, tags=["events"])
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    e = models.Event(**payload.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

# ---------- Actions: register, attendance, feedback ----------

@app.post("/events/{event_id}/register", tags=["actions"])
def register(event_id: int, req: schemas.RegisterRequest, db: Session = Depends(get_db)):
    # ensure event and student belong to same college
    event = db.get(models.Event, event_id)
    student = db.get(models.Student, req.student_id)
    if not event or not student:
        raise HTTPException(404, "Event or Student not found")
    if student.college_id != event.college_id:
        raise HTTPException(400, "Student and Event are from different colleges")
    # unique registration
    exists = db.execute(select(models.Registration).where(
        models.Registration.event_id==event_id,
        models.Registration.student_id==req.student_id
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "Student already registered for this event")
    r = models.Registration(event_id=event_id, student_id=req.student_id)
    db.add(r)
    db.commit()
    return {"ok": True, "message": "Registered"}

@app.post("/events/{event_id}/attendance", tags=["actions"])
def mark_attendance(event_id: int, req: schemas.AttendanceRequest, db: Session = Depends(get_db)):
    # ensure registration exists
    reg = db.execute(select(models.Registration).where(
        models.Registration.event_id==event_id,
        models.Registration.student_id==req.student_id
    )).scalar_one_or_none()
    if not reg:
        raise HTTPException(400, "Student is not registered for the event")
    # unique attendance
    exists = db.execute(select(models.Attendance).where(
        models.Attendance.event_id==event_id,
        models.Attendance.student_id==req.student_id
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "Attendance already marked")
    a = models.Attendance(event_id=event_id, student_id=req.student_id, status=req.status)
    db.add(a)
    db.commit()
    return {"ok": True, "message": "Attendance marked"}

@app.post("/events/{event_id}/feedback", tags=["actions"])
def submit_feedback(event_id: int, req: schemas.FeedbackRequest, db: Session = Depends(get_db)):
    # ensure registration exists
    reg = db.execute(select(models.Registration).where(
        models.Registration.event_id==event_id,
        models.Registration.student_id==req.student_id
    )).scalar_one_or_none()
    if not reg:
        raise HTTPException(400, "Student is not registered for the event")
    # unique feedback
    exists = db.execute(select(models.Feedback).where(
        models.Feedback.event_id==event_id,
        models.Feedback.student_id==req.student_id
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "Feedback already submitted")
    f = models.Feedback(event_id=event_id, student_id=req.student_id,
                        rating=req.rating, comment=req.comment)
    db.add(f)
    db.commit()
    return {"ok": True, "message": "Feedback recorded"}

# ---------- Reports ----------

@app.get("/reports/event/{event_id}/stats", response_model=schemas.EventStats, tags=["reports"])
def event_stats(event_id: int, db: Session = Depends(get_db)):
    regs = db.execute(select(func.count(models.Registration.id)).where(
        models.Registration.event_id==event_id)).scalar_one()
    attends = db.execute(select(func.count(models.Attendance.id)).where(
        models.Attendance.event_id==event_id)).scalar_one()
    avg_fb = db.execute(select(func.avg(models.Feedback.rating)).where(
        models.Feedback.event_id==event_id)).scalar_one()
    attendance_pct = float(attends) / regs * 100 if regs else 0.0
    return {
        "event_id": event_id,
        "registrations": int(regs or 0),
        "attendance_count": int(attends or 0),
        "attendance_percentage": round(attendance_pct, 2),
        "average_feedback": float(avg_fb) if avg_fb is not None else None
    }

@app.get("/reports/event-popularity", tags=["reports"])
def event_popularity(college_id: int, event_type: Optional[str] = None, db: Session = Depends(get_db)):
    # registrations per event, sorted desc
    stmt = select(
        models.Event.id,
        models.Event.title,
        models.Event.event_type,
        func.count(models.Registration.id).label("registrations")
    ).join(models.Registration, models.Event.id==models.Registration.event_id, isouter=True)     .where(models.Event.college_id==college_id)     .group_by(models.Event.id)     .order_by(text("registrations DESC"))
    if event_type:
        stmt = stmt.where(models.Event.event_type==event_type)
    rows = db.execute(stmt).all()
    return [{"event_id": r.id, "title": r.title, "event_type": r.event_type, "registrations": int(r.registrations or 0)} for r in rows]

@app.get("/reports/student-participation", response_model=List[schemas.StudentParticipation], tags=["reports"])
def student_participation(college_id: int, db: Session = Depends(get_db)):
    # count attendance (present) per student
    stmt = select(
        models.Student.id,
        models.Student.name,
        func.count(models.Attendance.id).label("events_attended")
    ).join(models.Attendance, models.Student.id==models.Attendance.student_id, isouter=True)     .where(models.Student.college_id==college_id)     .group_by(models.Student.id)     .order_by(text("events_attended DESC"))
    rows = db.execute(stmt).all()
    return [{"student_id": r.id, "name": r.name, "events_attended": int(r.events_attended or 0)} for r in rows]

@app.get("/reports/top-active-students", tags=["reports"])
def top_active_students(college_id: int, limit: int = 3, db: Session = Depends(get_db)):
    stmt = select(
        models.Student.id,
        models.Student.name,
        func.count(models.Attendance.id).label("events_attended")
    ).join(models.Attendance, models.Student.id==models.Attendance.student_id, isouter=False)     .where(models.Student.college_id==college_id)     .group_by(models.Student.id)     .order_by(text("events_attended DESC"))     .limit(limit)
    rows = db.execute(stmt).all()
    return [{"student_id": r.id, "name": r.name, "events_attended": int(r.events_attended)} for r in rows]
