from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import timedelta, datetime
import jwt
import os

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
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Enable CORS for all routes
CORS(
    app,
    resources={r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "*"],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }}
)

init_db(app)

# ------------------------
# JWT Helper Functions
# ------------------------
def create_token(user_id, role):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token():
    """Verify JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]  # Remove 'Bearer ' prefix
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
        return None

def require_auth(role=None):
    """Decorator to require authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            payload = verify_token()
            if not payload:
                return jsonify({"msg": "Unauthorized"}), 401
            
            if role and payload.get('role') != role:
                return jsonify({"msg": "Forbidden"}), 403
            
            request.current_user = payload
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

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
    
    # Create token
    token = create_token(user.id, user.role)
    
    return jsonify({
        "msg": "Registration successful",
        "token": token,
        "role": user.role,
        "user_id": user.id
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_token(user.id, user.role)
    
    return jsonify({
        "msg": "Login successful",
        "token": token,
        "role": user.role,
        "user_id": user.id
    })

@app.route("/logout", methods=["POST"])
def logout():
    # With JWT, logout is handled client-side by removing the token
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
# /me Route
# ------------------------
@app.route("/me", methods=["GET"])
@require_auth()
def me():
    user_id = request.current_user['user_id']
    role = request.current_user['role']
    
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
@require_auth(role="barber")
def barber_setup():
    user_id = request.current_user['user_id']
    
    data = request.json
    existing = BarberProfile.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({"msg": "Profile already exists"}), 400

    profile = BarberProfile(
        user_id=user_id,
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
            "id": b.user_id,
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
@require_auth(role="barber")
def create_service():
    user_id = request.current_user['user_id']
    
    data = request.json
    service = Service(
        barber_id=user_id,
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
@require_auth(role="barber")
def delete_service(service_id):
    user_id = request.current_user['user_id']
    
    service = Service.query.filter_by(id=service_id, barber_id=user_id).first()
    if not service:
        return jsonify({"msg": "Service not found"}), 404

    db.session.delete(service)
    db.session.commit()
    return jsonify({"msg": "Service deleted"})

# ------------------------
# Team Members Routes
# ------------------------
@app.route("/barber/team", methods=["POST"])
@require_auth(role="barber")
def create_team_member():
    user_id = request.current_user['user_id']
    
    data = request.json
    member = TeamMember(
        barber_id=user_id,
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
@require_auth(role="barber")
def delete_team_member(member_id):
    user_id = request.current_user['user_id']
    
    member = TeamMember.query.filter_by(id=member_id, barber_id=user_id).first()
    if not member:
        return jsonify({"msg": "Team member not found"}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({"msg": "Team member deleted"})

# ------------------------
# Booking Routes
# ------------------------
@app.route("/book", methods=["POST"])
@require_auth()
def create_booking():
    user_id = request.current_user['user_id']
    data = request.json or {}

    required_fields = ["barber_id", "service_id", "date", "time", "price"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    booking = Booking(
        customer_id=user_id,
        barber_id=data["barber_id"],
        service_id=data["service_id"],
        appointment_date=data["date"],
        appointment_time=data["time"],
        price=data["price"],
        status="pending"
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({"msg": "Booking created", "id": booking.id}), 201

@app.route("/customer/bookings", methods=["GET"])
@require_auth()
def get_customer_bookings():
    user_id = request.current_user['user_id']
    
    bookings = Booking.query.filter_by(customer_id=user_id).all()
    result = []

    for b in bookings:
        barber = BarberProfile.query.filter_by(id=b.barber_id).first()
        service = Service.query.get(b.service_id)

        result.append({
            "id": b.id,
            "barber": barber.shop_name if barber else "Unknown",
            "service": service.name if service else "Unknown",
            "date": b.appointment_date,
            "time": b.appointment_time,
            "status": b.status,
            "price": b.price
        })

    return jsonify(result)

@app.route("/barber/bookings", methods=["GET"])
@require_auth(role="barber")
def get_barber_bookings():
    user_id = request.current_user['user_id']
    
    bookings = Booking.query.filter_by(barber_id=user_id).all()
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
            "date": b.appointment_date,
            "time": b.appointment_time,
            "status": b.status,
            "price": b.price
        })

    return jsonify(result)

@app.route("/barber/bookings/<int:booking_id>", methods=["PATCH"])
@require_auth(role="barber")
def update_booking_status(booking_id):
    user_id = request.current_user['user_id']
    
    booking = Booking.query.filter_by(id=booking_id, barber_id=user_id).first()
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404

    data = request.json
    booking.status = data["status"]
    db.session.commit()
    return jsonify({"msg": "Booking updated"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)