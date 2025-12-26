Barbing Salon Booking System API
This is a RESTful backend API for a barbing salon booking system built with Flask and SQLite. It supports customers and barbers, handling registrations, logins, bookings, services, and team members. No JWT or admin authentication is required.

Features
-Barber
Register and login
Setup shop profile: shop name, description, address, phone, email, operating hours
Add/update/remove services: name, price, duration, description
Add/update/remove team members: name, specialization
View pending, approved bookings
Approve or reject bookings

-Customer
Register and login
View list of approved barbers
View barber details: services, team members, shop info
Book appointments for services
View bookings and booking status
Cancel bookings (with 2-hour prior restriction)

-Common
Forgot password for both barber and customer
Logout functionality
Live data updates reflected in dashboards

Authentication & User Management
POST /register → Register as barber or customer
POST /login → Login for barber or customer
POST /forgot-password → Reset password for barber or customer
POST /logout → Logout

Barber Endpoints
POST /barber/setup → Set up barber shop profile
POST /barber/service → Add a service
PATCH /barber/service/<service_id> → Update a service
DELETE /barber/service/<service_id> → Remove a service
POST /barber/team-member → Add a team member
PATCH /barber/team-member/<member_id> → Update a team member
DELETE /barber/team-member/<member_id> → Remove a team member
GET /barber/bookings → List all bookings for barber
PATCH /barber/booking/<booking_id> → Approve/reject a booking

Customer Endpoints
GET /barbers → List all approved barbers
GET /barber/<barber_id> → Get barber details (services, team, shop info)
POST /book → Book an appointment
GET /my-bookings → View customer's bookings
DELETE /cancel/<booking_id> → Cancel a booking

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






