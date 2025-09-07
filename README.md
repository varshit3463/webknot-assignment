Campus Event Reporting Prototype Project
This is a small scale implemantation done through FastApi and SQLite to show how collages can mannage events and tracking of student participation.Tis a part of tha assignment and involves mostely clean implementation od API's database models and basic reportiong functionalities.
Features
Colleges – Add and manage colleges.
Students – Register students under a college.
Events – Organize and plan events.

Event Actions
Register students for events
mark attendance
Collect feedback (ratings + comments)

Reports
Event statistics (registrations, attendance %, avg feedback)
Event popularity by registrations
Student participation and top active students


Tech Stack
Backend: FastAPI
Database: SQLite using SQLAlchemy ORM
Validation: Pydantic schemas
UI: Swagger UI  for testing.

Procedute to run this project in powershell
1.Install dependencies:
pip install -r requirements.txt

2.Initialise Database:
python scripts/init_db.py

3.Run the FastAPI server:
uvicorn app.main:app --reload

4.test in in local server:
http://127.0.0.1:8000/docs
