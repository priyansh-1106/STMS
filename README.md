# TaskFlow – Smart Task Management System

TaskFlow is a modern Flask-based task management web application that allows users to create, manage, and track daily tasks with real-time updates and analytics.

The project uses Flask for the backend, PostgreSQL for database management, Flask-SocketIO for live synchronization, and Pandas + NumPy for analytics.

---

# Features

- User Registration & Login System
- Session-based Authentication
- Create, Update, Delete Tasks
- Task Priority Management
- Task Status Tracking
- Real-time Task Updates using WebSockets
- Analytics Dashboard using Pandas & NumPy
- Responsive Dark Blue Gradient UI
- PostgreSQL Database Integration

---


# Project Structure

```bash
task_manager/
│
├── app.py
├── requirements.txt
├── schema.sql
├── README.md
│
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── login.html
    └── register.html
```

---

# Installation & Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd task_manager
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Setup PostgreSQL Database

Open PostgreSQL terminal:

```sql
CREATE DATABASE task_manager_db;
```

Run the schema file:

```bash
psql -U postgres -d task_manager_db -f schema.sql
```

---

## 5. Configure Database Connection

Open `app.py` and update the database credentials:

```python
DB = "host=localhost dbname=task_manager_db user=postgres password=postgres port=5432"
```

---

## 6. Run the Application

```bash
python app.py
```

Server will start at:

```bash
http://127.0.0.1:5000
```

---

# API Endpoints

## Authentication Routes

| Method | Endpoint | Description |
|---|---|---|
| GET | `/login` | Login page |
| POST | `/login` | Authenticate user |
| GET | `/register` | Registration page |
| POST | `/register` | Create account |
| GET | `/logout` | Logout user |

---

## Task APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks` | Fetch all tasks |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task |
| GET | `/api/analytics` | Fetch analytics |

---

# Task Object Example

```json
{
  "title": "Complete project",
  "description": "Finish Flask dashboard",
  "priority": "high",
  "status": "in_progress"
}
```

---

# Analytics Included

The dashboard calculates:

- Total Tasks
- Completed Tasks
- Pending Tasks
- In Progress Tasks
- Completion Percentage

---

# Real-Time Updates

TaskFlow uses Flask-SocketIO to provide live updates.

Whenever a task is:

- Added
- Updated
- Deleted

All connected users instantly receive updates without refreshing the page.

---

# Security Notes

Recommended improvements:

- Password hashing
- CSRF protection
- Environment variables for secrets
- JWT Authentication
- Role-based access control

---

# Future Improvements

- Drag & Drop Task Board
- Email Notifications
- Task Categories
- Due Dates & Reminders
- Search & Filtering
- Docker Deployment
- Admin Dashboard
- Charts & Graph Analytics

---

# Requirements

```txt
flask==3.0.3
flask-socketio==5.3.6
psycopg2-binary==2.9.9
pandas==2.2.2
numpy==1.26.4
eventlet==0.36.1
```

---

