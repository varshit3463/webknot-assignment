from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import SessionLocal, Base, engine
from . import models

def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Colleges
        ru = models.College(name="Reva University")
        cu = models.College(name="City College")
        db.add_all([ru, cu]); db.flush()

        # Students (Reva)
        s1 = models.Student(college_id=ru.id, roll_number="REVA001", name="Asha", email="asha@example.com")
        s2 = models.Student(college_id=ru.id, roll_number="REVA002", name="Ravi", email="ravi@example.com")
        s3 = models.Student(college_id=ru.id, roll_number="REVA003", name="Meera", email="meera@example.com")

        # Events (Reva)
        e1 = models.Event(college_id=ru.id, title="AI Workshop", event_type="Workshop")
        e2 = models.Event(college_id=ru.id, title="Hackathon 24h", event_type="Hackathon")
        e3 = models.Event(college_id=ru.id, title="Tech Seminar", event_type="Seminar")

        db.add_all([s1, s2, s3, e1, e2, e3]); db.flush()

        # Registrations
        regs = [
            models.Registration(event_id=e1.id, student_id=s1.id),
            models.Registration(event_id=e1.id, student_id=s2.id),
            models.Registration(event_id=e2.id, student_id=s1.id),
            models.Registration(event_id=e2.id, student_id=s3.id),
            models.Registration(event_id=e3.id, student_id=s2.id),
        ]
        db.add_all(regs); db.flush()

        # Attendance (mark some present)
        atts = [
            models.Attendance(event_id=e1.id, student_id=s1.id, status="present"),
            models.Attendance(event_id=e1.id, student_id=s2.id, status="present"),
            models.Attendance(event_id=e2.id, student_id=s3.id, status="present"),
        ]
        db.add_all(atts); db.flush()

        # Feedbacks
        fbs = [
            models.Feedback(event_id=e1.id, student_id=s1.id, rating=5, comment="Loved it"),
            models.Feedback(event_id=e1.id, student_id=s2.id, rating=4, comment="Good"),
            models.Feedback(event_id=e2.id, student_id=s3.id, rating=3, comment="Okay"),
        ]
        db.add_all(fbs)

        db.commit()
        print("Seeded sample data.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
