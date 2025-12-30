from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from datetime import timedelta

from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI
from database import db, init_db
from models import (
    User,
    BarberProfile,
    OperatingHour,
    Service,
    TeamMember,
    Booking
)

app = Flask(__name__)

app.config.update(
    SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)


# Enable CORS for all routes with credentials
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}}
)

init_db(app)

# ------------------------
# Authentication Routes
# ------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already registered"}), 400

    user = User(
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        role=data["role"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Registration successful"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    session.permanent = True
    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({"msg": "Login successful", "role": user.role})

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"msg": "Logged out"})

@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.password = generate_password_hash(data["new_password"])
    db.session.commit()
    return jsonify({"msg": "Password updated"}), 200

# ------------------------
# /me Route for frontend
# ------------------------
@app.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    role = session.get("role")
    if not user_id or not role:
        return jsonify({"msg": "Not logged in"}), 401

    has_profile = False
    if role == "barber":
        profile = BarberProfile.query.filter_by(user_id=user_id).first()
        has_profile = profile is not None

    return jsonify({
        "id": user_id,
        "role": role,
        "has_profile": has_profile
    })

# ------------------------
# Barber Setup and Management
# ------------------------
@app.route("/barber/setup", methods=["POST"])
def barber_setup():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    existing = BarberProfile.query.filter_by(user_id=session["user_id"]).first()
    if existing:
        return jsonify({"msg": "Profile already exists"}), 400

    profile = BarberProfile(
        user_id=session["user_id"],
        shop_name=data["shop_name"],
        description=data.get("description"),
        address=data["address"],
        phone=data["phone"],
        email=data["email"]
    )
    db.session.add(profile)
    db.session.flush()

    # Add operating hours if provided
    if 'operating_hours' in data:
        for day, hours in data['operating_hours'].items():
            if hours == 'closed':
                oh = OperatingHour(barber_id=profile.user_id, day=day, is_closed=True)
            else:
                times = hours.split('-')
                oh = OperatingHour(
                    barber_id=profile.user_id,
                    day=day,
                    open_time=times[0],
                    close_time=times[1],
                    is_closed=False
                )
            db.session.add(oh)

    db.session.commit()
    return jsonify({"msg": "Barber profile created"})

@app.route("/barbers", methods=["GET"])
def list_barbers():
    barbers = BarberProfile.query.all()
    return jsonify([
        {
            "id": b.user_id,  # Return user_id as id for consistency
            "shop_name": b.shop_name,
            "address": b.address,
            "phone": b.phone,
            "email": b.email,
            "description": b.description
        } for b in barbers
    ])

@app.route("/barbers/<int:barber_id>", methods=["GET"])
def get_barber(barber_id):
    barber = BarberProfile.query.filter_by(user_id=barber_id).first()
    if not barber:
        return jsonify({"msg": "Barber not found"}), 404
    
    # Get operating hours
    hours = OperatingHour.query.filter_by(barber_id=barber_id).all()
    operating_hours = {}
    for h in hours:
        if h.is_closed:
            operating_hours[h.day] = "closed"
        else:
            operating_hours[h.day] = f"{h.open_time}-{h.close_time}"
    
    return jsonify({
        "id": barber.user_id,
        "shop_name": barber.shop_name,
        "address": barber.address,
        "phone": barber.phone,
        "email": barber.email,
        "description": barber.description,
        "operating_hours": operating_hours
    })

# ------------------------
# Services Routes
# ------------------------
@app.route("/barber/services", methods=["POST"])
def create_service():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    service = Service(
        barber_id=session["user_id"],
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        duration=data["duration"]
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({"msg": "Service created", "id": service.id})

@app.route("/barbers/<int:barber_id>/services", methods=["GET"])
def get_barber_services(barber_id):
    services = Service.query.filter_by(barber_id=barber_id).all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "price": s.price,
            "duration": s.duration
        } for s in services
    ])

@app.route("/barber/services/<int:service_id>", methods=["DELETE"])
def delete_service(service_id):
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    service = Service.query.filter_by(id=service_id, barber_id=session["user_id"]).first()
    if not service:
        return jsonify({"msg": "Service not found"}), 404

    db.session.delete(service)
    db.session.commit()
    return jsonify({"msg": "Service deleted"})

# ------------------------
# Team Members Routes
# ------------------------
@app.route("/barber/team", methods=["POST"])
def create_team_member():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    member = TeamMember(
        barber_id=session["user_id"],
        name=data["name"],
        specialty=data["specialty"]
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"msg": "Team member added", "id": member.id})

@app.route("/barbers/<int:barber_id>/team", methods=["GET"])
def get_barber_team(barber_id):
    team = TeamMember.query.filter_by(barber_id=barber_id).all()
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "specialty": m.specialty
        } for m in team
    ])

@app.route("/barber/team/<int:member_id>", methods=["DELETE"])
def delete_team_member(member_id):
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    member = TeamMember.query.filter_by(id=member_id, barber_id=session["user_id"]).first()
    if not member:
        return jsonify({"msg": "Team member not found"}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({"msg": "Team member deleted"})

# ------------------------
# Booking Routes
# ------------------------

@app.route("/book", methods=["POST"])
def create_booking():
    if not session.get("user_id"):
        return jsonify({"msg": "Not logged in"}), 401

    data = request.json or {}

    # Validation (prevents 500 errors)
    required_fields = ["barber_id", "service_id", "date", "time", "price"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    booking = Booking(
        customer_id=session["user_id"],
        barber_id=data["barber_id"],
        service_id=data["service_id"],
        appointment_date=data["date"],      # ✅ FIXED
        appointment_time=data["time"],      # ✅ FIXED
        price=data["price"],
        status="pending"
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({"msg": "Booking created", "id": booking.id}), 201


@app.route("/customer/bookings", methods=["GET"])
def get_customer_bookings():
    if not session.get("user_id"):
        return jsonify({"msg": "Not logged in"}), 401

    bookings = Booking.query.filter_by(customer_id=session["user_id"]).all()
    result = []

    for b in bookings:
        barber = BarberProfile.query.filter_by(id=b.barber_id).first()
        service = Service.query.get(b.service_id)

        result.append({
            "id": b.id,
            "barber": barber.shop_name if barber else "Unknown",
            "service": service.name if service else "Unknown",
            "date": b.appointment_date,        # ✅ FIXED
            "time": b.appointment_time,        # ✅ FIXED
            "status": b.status,
            "price": b.price
        })

    return jsonify(result)


@app.route("/barber/bookings", methods=["GET"])
def get_barber_bookings():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    bookings = Booking.query.filter_by(barber_id=session["user_id"]).all()
    result = []

    for b in bookings:
        customer = User.query.get(b.customer_id)
        service = Service.query.get(b.service_id)

        result.append({
            "id": b.id,
            "customer_id": b.customer_id,
            "customer_name": customer.name if customer else "Unknown",
            "customer_email": customer.email if customer else "Unknown",
            "service_id": b.service_id,
            "service": service.name if service else "Unknown",
            "date": b.appointment_date,        # ✅ FIXED
            "time": b.appointment_time,        # ✅ FIXED
            "status": b.status,
            "price": b.price
        })

    return jsonify(result)


@app.route("/barber/bookings/<int:booking_id>", methods=["PATCH"])
def update_booking_status(booking_id):
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    booking = Booking.query.filter_by(id=booking_id, barber_id=session["user_id"]).first()
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404

    data = request.json
    booking.status = data["status"]
    db.session.commit()
    return jsonify({"msg": "Booking updated"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)