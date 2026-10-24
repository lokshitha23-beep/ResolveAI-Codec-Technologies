# ResolveAI — Support Ticket Management & Triage System

## Overview
ResolveAI is a support operations web application designed to help teams create, organize, prioritize, and track customer support tickets.

The application uses transparent keyword-based rules to suggest ticket categories and priorities. It also identifies potentially similar tickets to help support teams review recurring issues.

This project was developed as an educational portfolio MVP using Python, FastAPI, SQLite, HTML, CSS, and JavaScript.

## Key Features
- **Ticket Creation:** Create and record support tickets.
- **Ticket Search:** Search existing tickets.
- **Category Suggestions:** Suggest ticket categories using keyword-based rules.
- **Priority Suggestions:** Recommend ticket priorities based on ticket content.
- **Similar Ticket Detection:** Find potentially related tickets using text similarity.
- **Status Management:** Update ticket statuses.
- **Assignee Management:** Assign tickets to team members.
- **SLA Tracking:** Display ticket deadlines and overdue indicators.
- **Dashboard:** View support ticket summary metrics.
- **Data Persistence:** Save ticket records in SQLite.
- **REST API:** Access documented backend endpoints.

## Technology Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: SQLite
- API Documentation: FastAPI Swagger UI

## Installation and Setup

### Prerequisites
- Python 3.10 or later
- pip

### Run on Windows
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Access the Application
- Web application: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

## Project Structure
```text
ResolveAI-Original/
├── app/
│   ├── main.py
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── requirements.txt
├── .gitignore
└── README.md
```

## Use Case
ResolveAI demonstrates how a support team can organize customer issues, identify urgent requests, track ticket progress, and find potentially related issues from a single dashboard.

## Limitations
This is an educational MVP. Ticket classification uses local keyword-based heuristics rather than a trained machine-learning model. Authentication, email delivery, and production-grade access controls are not implemented. SLA deadlines do not currently account for configurable business calendars. Use fictional sample data for demonstrations.

## Future Enhancements
- Secure login and role-based access
- Email notifications and ticket updates
- Configurable SLA policies
- Advanced text classification
- Team performance reports
- Integration with external help-desk platforms
