Barbing Salon Appointment Backend

This is a Flask-based RESTful API for managing an online barbing salon booking system. It includes user authentication, appointment management, and admin features using JWT for secure access.


Project Structure

barbing-backend/
│
├── app.py               # Main Flask application and API endpoints
├── models.py            # Database models for Users and Appointments
├── requirements.txt     # Python dependencies
└── barbing.db           # SQLite database file (auto-created) (inside instance folder)
	•	app.py contains all routes for user authentication, appointment management, and admin features.
	•	models.py defines the database models (User and Appointment) using SQLAlchemy.
	•	requirements.txt lists all dependencies needed for the project.
	•	barbing.db is automatically created when the app runs for the first time.



Setup and Installation
1.	Clone the repository:

git clone <repo-url>
cd barbing-backend
	
2.	Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3.	Install dependencies:

pip install -r requirements.txt

4.	Run the application:

python app.py

The server will start on http://localhost:5000 by default.



Environment Variables
	•	PORT – Optional, default is 5000.
	•	JWT_SECRET_KEY – Secret key for JWT token generation. Default in code: “super-secret-key”.
	•	SQLALCHEMY_DATABASE_URI – Database URI. Default in code: sqlite:///barbing.db.


Database

The backend uses SQLite (barbing.db).

User Model:
	•	id – Primary key
	•	name – User’s name
	•	email – Unique, required
	•	password – Hashed password
	•	role – Either user or admin, default is user

Appointment Model:
	•	id – Primary key
	•	user_id – Foreign key referencing the user
	•	service – Type of barbing service
	•	start_time – Appointment start time
	•	end_time – Appointment end time
	•	status – Either pending, approved, or cancelled
	•	created_at – Timestamp when the appointment was created

Setting a User as Admin 
By default, all users are created with the role "user". To access admin-only endpoints, a user must have the role "admin". You can set a user as admin using one of the following methods:

Option 1: Manually update the SQLite database
1.	Open barbing.db using SQLite CLI or a GUI like DB Browser for SQLite.
2.  Run the following SQL command, replacing the email with the user you want to promote:

UPDATE user
SET role = 'admin'
WHERE email = 'admin@example.com';

3.	Save changes. That user now has admin access.

Option 2: Update role using Python
1.	Open a Python shell in your project folder:

2.	Run the following code:

from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(email="admin@example.com").first()
    user.role = "admin"
    db.session.commit()

The selected user now has admin privileges.


API Endpoints

Authentication:
	•	POST /register – Register a new user. Body: {"name": "...", "email": "...", "password": "..."}
	•	POST /login – User login. Body: {"email": "...", "password": "..."}
	•	POST /forgot-password – Reset password. Body: {"email": "...", "new_password": "..."}

User Appointments:
	•	POST /appointments – Create a new appointment. Body: {"service": "...", "start_time": "YYYY-MM-DD HH:MM", "duration": 30}
	•	GET /appointments – Get all appointments of the logged-in user.
	•	PUT /appointments/<id>/cancel – Cancel a specific appointment.

Admin Appointments:
	•	GET /admin/appointments – View all appointments (admin only).
	•	PUT /admin/appointments/<id> – Update appointment status. Body: {"status": "approved"} or {"status": "cancelled"}

Authentication Requirement:
All /appointments and /admin/appointments endpoints require a valid JWT token in the header:

Authorization: Bearer <access_token>


⸻

Testing the API
	•	Use an API client like Postman
	1.	Register a user with POST /register.
	2.	Login with POST /login to get a JWT token.
	3.	Book an appointment with POST /appointments.
	4.	View appointments with GET /appointments.
	5.	Admin can view all appointments with GET /admin/appointments and update statuses with PUT /admin/appointments

Make sure the backend is running on localhost:5000 or your deployed URL.
