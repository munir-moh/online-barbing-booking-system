Barbing Salon API Documentation

Endpoints, Payloads, and Responses
1.	Register (Barber or Customer)
POST /register
Payload:
{
  "name": "John Doe",
  "phone": "08012345678",
  "email": "john@example.com",
  "password": "password123",
  "role": "barber" // or "customer"
}

Response:
{ "msg": "Registration successful" }

2.	Login
POST /login
Payload:
{
  "email": "john@example.com",
  "password": "password123"
}

Response (Barber):
{ "msg": "Login successful", "role": "barber" }

Response (Customer):
{ "msg": "Login successful", "role": "customer" }

3.	Forgot Password
POST /forgot-password
Payload:
{
  "email": "john@example.com",
  "new_password": "newpassword123"
}

Response:
{ "msg": "Password updated" }

4.	Setup Barber Shop Profile
POST /barber/setup
Payload:
{
  "shop_name": "Barber Kings",
  "description": "Luxury haircuts and grooming",
  "address": "123 Barber Street",
  "phone": "08012345678",
  "email": "barber@example.com"
}

Response:
{ "msg": "Barber profile created" }

5.	Add Service
POST /barber/services
Payload:
{
  "name": "Haircut",
  "price": 1500,
  "duration": 60,
  "description": "Standard haircut"
}

Response:
{ "msg": "Service added" }

6.	View Services (Barber)
GET /barber/services
Response:
[
  {
    "id": 1,
    "name": "Haircut",
    "price": 1500,
    "duration": 60,
    "description": "Standard haircut"
  }
]

7. Delete Service
DELETE /barber/services/<service_id>
Response:
{ "msg": "Service removed" }

8.	Add Team Member
POST /barber/team
Payload:
{
  "name": "Mike",
  "specialty": "Haircut"
}

Response:
{ "msg": "Team member added" }

9.	View Team Members (Barber)
GET /barber/team
Response:
[
  {
    "id": 1,
    "name": "Mike",
    "specialty": "Haircut"
  }
]

10.	Remove Team Member
DELETE /barber/team/<member_id>
Response:
{ "msg": "Team member removed" }

11.	Set Operating Hours
POST /barber/operating-hours
Payload:
{
  "hours": [
    { "day": "Monday", "open_time": "09:00", "close_time": "18:00" },
    { "day": "Sunday", "closed": true }
  ]
}

Response:
{ "msg": "Operating hours saved" }

12.	View Operating Hours
GET /barber/operating-hours
Response:
[
  { "day": "Monday", "open_time": "09:00", "close_time": "18:00", "closed": false },
  { "day": "Sunday", "open_time": null, "close_time": null, "closed": true }
]

13.	View Barbers (Customer/Public)
GET /barbers
Response:
[
  {
    "id": 1,
    "shop_name": "Barber Kings",
    "address": "123 Barber Street",
    "phone": "08012345678",
    "email": "barber@example.com"
  }
]

14.	View Barber Services (Customer/Public)
GET /barbers/<barber_id>/services
Response:
[
  {
    "id": 1,
    "name": "Haircut",
    "price": 1500,
    "duration": 60,
    "description": "Standard haircut"
  }
]

15.	View Barber Team (Customer/Public)
GET /barbers/<barber_id>/team
Response:
[
  {
    "id": 1,
    "name": "Mike",
    "specialty": "Haircut"
  }
]

16. Book Appointment (Customer)
POST /book
Payload:
{
  "barber_id": 1,
  "service_id": 1,
  "date": "2025-12-28",
  "time": "12:00",
  "price": 1500
}

Response:
{ "msg": "Booking created", "status": "pending" }

17.	View Bookings (Customer)
GET /customer/bookings
Response:
[
  {
    "id": 1,
    "barber": "Barber Kings",
    "service": "Haircut",
    "date": "2025-12-28",
    "time": "12:00",
    "team_member": "Mike",
    "price": 1500,
    "status": "pending"
  }
]

18.	Update Booking Status (Barber)
PATCH /barber/bookings/<booking_id>
Payload:
{ "status": "approved" } or "rejected"

Response:
{ "msg": "Booking updated" }

19.	Logout
POST /logout
Response:
{ "msg": "Logged out" }


Notes
•All endpoints are session-based.
•Customers cannot cancel appointments less than 2 hours before the scheduled time.
•CORS is enabled for http://localhost:5173 (adjust if frontend runs elsewhere).
•Bookings automatically start as pending. Barbers approve/reject them.