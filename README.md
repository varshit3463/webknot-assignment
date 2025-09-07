Campus Event Reporting Prototype

This is a small-scale implementation done through FastAPI and SQLite to show how the colleges can manage events and tracking of student participation. It’s part of the assignment and involves mostly clean implementation of APIs, database models and basic reporting functionality.

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