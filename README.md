Barbing Booking Systems API

This is a Flask-based backend API for a barber booking platform.  
It supports authentication, barber profile management, services, team members, and appointment bookings.


Features
- JWT authentication
- Role-based access (customer and barber)
- Barber profile and operating hours
- Services and team management
- Booking creation and management
- CORS enabled for frontend integration


Tech Stack
- Python
- Flask
- SQLAlchemy
- JWT
- SQLite / PostgreSQL
- Flask-CORS


Authentication

Authentication uses JWT tokens.
Include this header for protected routes:
Authorization: Bearer <token>


Roles
customer  
barber  

Only barbers can:
- Create barber profile
- Manage services
- Manage team members
- View and update bookings assigned to them


Notes

- Tokens expire after 7 days
- No refresh token implementation
- No payment gateway integration

Project Structure
/barbing-api
├─ app.py               
├─ models.py            
├─ database.py          
├─ config.py
├─ requirements.txt     


Setup Instructions

-Clone the repository:
git clone <repo_url>
cd <repo_folder>

-Create a virtual environment:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

-Install dependencies:
pip install -r requirements.txt

-Run the app:
python app.py

The API will be available at http://127.0.0.1:5000






