# FastAPI Job Portal

A **Job Portal API** built with **FastAPI**, **SQLAlchemy**, and **WebSockets**.  
This project allows **users, recruiters, and admins** to register, post jobs, apply for jobs, and receive real-time notifications.

---

## Features

### User
- Register and login
- View their profile
- Apply for jobs
- See list of their applications

### Recruiter
- Post jobs
- View their posted jobs
- Receive notifications when a user applies for a job

### Admin
- View all users
- Deactivate users
- Access protected admin routes

### Common
- JWT-based authentication
- Role-based access control
- Pagination support for list endpoints
- Real-time notifications using WebSockets

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite (can switch to PostgreSQL)
- **ORM:** SQLAlchemy
- **Authentication:** JWT (PyJWT / python-jose)
- **Password Hashing:** Argon2
- **WebSockets:** FastAPI WebSocket
- **Environment Variables:** python-dotenv

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/fastapi-job-portal.git
cd fastapi-job-portal

2. create and activate a virtual environment

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Create a .env file having below given variables

SECRET_KEY=
ALGORITHM=
DATABASE_URL=
ACCESS_TOKEN_EXPIRE_MINUTES=

5. Run the project

uvicorn main:app --reload
 http://127.0.0.1:8000/docs

API Endpoints:

1. User

POST /register – Register a new user
POST /login – Login and get JWT token
GET /profile/user – Get user profile
GET /profile/user/applications – Get applied jobs

2. Recruiter

POST /postjob – Post a new job
GET /profile/recruiter – Get recruiter profile
GET /profile/recruiter/posts – Get all jobs posted

3. Admin
GET /profile/admin – Get admin profile
GET /admin/users – List all users
PATCH /admin/user/deactivate – Deactivate a user

4. Applications

POST /apply/{job_id} – Apply for a job

5. WebSocket
WS /ws?token=<JWT> – Real-time notifications


Notes

1.JWT token must be provided for all protected routes.
2.Passwords are hashed using Argon2 and limited to 72 characters.
3.Pagination is available for endpoints returning lists (skip & limit).
4.  .env values are never uploaded to GitHub.

License
MIT License