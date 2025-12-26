Endpoints, Payloads, and Responses
1. Register (Barber or Customer)

POST /register

Payload:
{
  "name": "John Doe",
  "phone": "08012345678",
  "email": "john@example.com",
  "password": "password123",
  "role": "barber"   // or "customer"
}

Response:
{
  "msg": "Registered successfully"
}

2. Login
POST /login

Payload:
{
  "email": "john@example.com",
  "password": "password123"
}

Response (Barber):
{
  "msg": "Login successful",
  "role": "barber"
}

Response (Customer):
{
  "msg": "Login successful",
  "role": "customer"
}

3. Forgot Password

POST /forgot-password

Payload:
{
  "email": "john@example.com",
  "new_password": "newpassword123"
}

Response:
{
  "msg": "Password updated successfully"
}

4. Setup Barber Shop Profile

POST /barber/setup

Payload:
{
  "shop_name": "Barber Kings",
  "description": "Luxury haircuts and grooming",
  "address": "123 Barber Street",
  "phone": "08012345678",
  "email": "barber@example.com",
  "operating_hours": {
    "monday": "09:00-18:00",
    "tuesday": "09:00-18:00",
    "wednesday": "09:00-18:00",
    "thursday": "09:00-18:00",
    "friday": "09:00-18:00",
    "saturday": "10:00-16:00",
    "sunday": "closed"
  }
}

Response:
{
  "msg": "Barber profile set up successfully"
}

5. Add Service

POST /barber/service

Payload:
{
  "name": "Haircut",
  "price": 1500,
  "duration": 60,
  "description": "Standard haircut"
}

Response:
{
  "msg": "Service added successfully"
}

6. Add Team Member

POST /barber/team-member

Payload:
{
  "name": "Mike",
  "specialization": "Haircut"
}

Response:
{
  "msg": "Team member added successfully"
}

7. View Barbers (Customer)

GET /barbers

Response:
[
  {
    "id": 1,
    "shop_name": "Barber Kings",
    "address": "123 Barber Street",
    "phone": "08012345678",
    "email": "barber@example.com",
    "description": "Luxury haircuts and grooming",
    "operating_hours": {
      "monday": "09:00-18:00",
      "tuesday": "09:00-18:00",
      ...
    }
  }
]

8. Book Appointment (Customer)

POST /book

Payload:
{
  "barber_id": 1,
  "service_name": "Haircut",
  "date": "2025-12-28",
  "time": "12:00",
  "preferred_team_member": "Mike",
  "location": "shop"  // or "home"
}

Response:
{
  "msg": "Booking created"
}

9. View Bookings (Customer)

GET /my-bookings

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

10. Update Booking (Barber)

PATCH /barber/booking/<booking_id>

Payload:
{
  "status": "approved"  // or "rejected" or "completed"
}

Response:
{
  "msg": "Booking updated"
}

11. Cancel Booking (Customer)

DELETE /cancel/<booking_id>

Response:
{
  "msg": "Booking cancelled"
}

12. Logout

POST /logout

Response:
{
  "msg": "Logged out successfully"
}

Notes
All endpoints are session-based
Barber approvals are not required; as soon as they set up their profile, they are listed publicly.
Bookings automatically start as pending, and barbers can approve/reject them.
Customers cannot cancel appointments less than 2 hours before the booked time.
CORS is enabled for http://localhost:5173 (adjust if your frontend runs elsewhere).