from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import Float
from .database import Base
import enum

class EventType(enum.Enum):
    WORKSHOP = "Workshop"
    HACKATHON = "Hackathon"
    SEMINAR = "Seminar"
    FEST = "Fest"

class College(Base):
    __tablename__ = "colleges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    students = relationship("Student", back_populates="college", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="college", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id"), index=True, nullable=False)
    roll_number: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    college = relationship("College", back_populates="students")
    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("college_id", "roll_number", name="uq_student_roll_per_college"),)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)  # store EventType.value
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    college = relationship("College", back_populates="events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="event", cascade="all, delete-orphan")

class Registration(Base):
    __tablename__ = "registrations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="registrations")
    student = relationship("Student", back_populates="registrations")

    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_unique_registration"),)

class Attendance(Base):
    __tablename__ = "attendances"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="present")  # present/absent (we only insert 'present')
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="attendances")

    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_unique_attendance"),)

class Feedback(Base):
    __tablename__ = "feedbacks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="feedbacks")
    student = relationship("Student", back_populates="feedbacks")
    __table_args__ = (UniqueConstraint("event_id", "student_id", name="uq_unique_feedback"),)
