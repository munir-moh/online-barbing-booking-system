Barbing Booking System API – API Documentation

Base URL:
https://barbing-salon-api.onrender.com

Local (development):
http://localhost:5000

Authentication:
JWT (Bearer Token)

Header format:
Authorization: Bearer <token>

Token expires after 7 days.

Authentication (Public)

Register
POST /register

Request Body:
{
  "name": "John Doe",
  "phone": "08012345678",
  "email": "john@example.com",
  "role": "customer",
  "password": "password123"
}

Response:
{
  "msg": "Registration successful",
  "token": "<jwt_token>",
  "role": "customer",
  "user_id": 1
}


Login
POST /login

Request Body:
{
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "msg": "Login successful",
  "token": "<jwt_token>",
  "role": "customer",
  "user_id": 1
}


Logout
POST /logout

Response:
{
  "msg": "Logged out"
}



Forgot Password
POST /forgot-password

Request Body:
{
  "email": "john@example.com",
  "new_password": "newpassword123"
}

Success Response (200):
{
  "msg": "Password updated"
}

Error Response (404):
{
  "error": "User not found"
}



User (Protected)

Get Current User
GET /me

Headers:
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "role": "barber",
  "has_profile": true
}



Barber Profile
Create Barber Profile (Protected – Barber Only)
POST /barber/setup

Headers:
Authorization: Bearer <token>

Request Body:
{
  "shop_name": "Elite Cuts",
  "description": "Luxury barbing experience",
  "address": "Kaduna",
  "phone": "08098765432",
  "email": "elitecuts@gmail.com",
  "operating_hours": {
    "monday": "09:00-18:00",
    "sunday": "closed"
  }
}

Response:
{
  "msg": "Barber profile created"
}



List All Barbers (Public)
GET /barbers

Response:
[
  {
    "id": 2,
    "shop_name": "Elite Cuts",
    "address": "Kaduna",
    "phone": "08098765432",
    "email": "elitecuts@gmail.com",
    "description": "Luxury barbing experience"
  }
]

---

Get Barber Details (Public)
GET /barbers/{barber_id}

Response:
{
  "id": 2,
  "shop_name": "Elite Cuts",
  "address": "Kaduna",
  "phone": "08098765432",
  "email": "elitecuts@gmail.com",
  "description": "Luxury barbing experience",
  "operating_hours": {
    "monday": "09:00-18:00",
    "sunday": "closed"
  }
}



Services
Create Service (Protected – Barber Only)
POST /barber/services

Headers:
Authorization: Bearer <token>

Request Body:
{
  "name": "Hair Cut",
  "description": "Professional haircut",
  "price": 3000,
  "duration": 30
}

Response:
{
  "msg": "Service created",
  "id": 1
}


Get Barber Services (Public)
GET /barbers/{barber_id}/services

Response:
[
  {
    "id": 1,
    "name": "Hair Cut",
    "description": "Professional haircut",
    "price": 3000,
    "duration": 30
  }
]



Delete Service (Protected – Barber Only)
DELETE /barber/services/{service_id}

Headers:
Authorization: Bearer <token>

Response:
{
  "msg": "Service deleted"
}


Team
Add Team Member (Protected – Barber Only)
POST /barber/team

Headers:
Authorization: Bearer <token>

Request Body:
{
  "name": "Munir",
  "specialty": "Fade cuts"
}

Response:
{
  "msg": "Team member added",
  "id": 1
}


Get Barber Team (Public)
GET /barbers/{barber_id}/team

Response:
[
  {
    "id": 1,
    "name": "Munir",
    "specialty": "Fade cuts"
  }
]


Remove Team Member (Protected – Barber Only)
DELETE /barber/team/{member_id}

Headers:
Authorization: Bearer <token>

Response:
{
  "msg": "Team member deleted"
}


Bookings
Create Booking (Protected – Customer or Barber)
POST /book

Headers:
Authorization: Bearer <token>

Request Body:
{
  "barber_id": 1,
  "service_id": 1,
  "date": "2026-01-10",
  "time": "14:00",
  "price": 3000
}

Response (201):
{
  "msg": "Booking created",
  "id": 1
}


View My Bookings (Protected)
GET /customer/bookings

Headers:
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "barber": "Elite Cuts",
    "service": "Hair Cut",
    "date": "2026-01-10",
    "time": "14:00",
    "status": "pending",
    "price": 3000
  }
]



View Barber Bookings (Protected – Barber Only)
GET /barber/bookings

Headers:
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "customer_id": 3,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "service_id": 1,
    "service": "Hair Cut",
    "date": "2026-01-10",
    "time": "14:00",
    "status": "pending",
    "price": 3000
  }
]


Update Booking Status (Protected – Barber Only)
PATCH /barber/bookings/{booking_id}

Headers:
Authorization: Bearer <token>

Request Body:
{
  "status": "approved"
}

Response:
{
  "msg": "Booking updated"
}