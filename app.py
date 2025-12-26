from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS

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
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)


CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

init_db(app)


@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already registered"}), 400

    user = User(
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        role=data["role"],  # barber | customer
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

    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({
        "msg": "Login successful",
        "role": user.role
    })


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"msg": "Email not registered"}), 404

    user.password = generate_password_hash(data["new_password"])
    db.session.commit()

    return jsonify({"msg": "Password updated"})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"msg": "Logged out"})


@app.route("/barber/setup", methods=["POST"])
def barber_setup():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    user_id = session["user_id"]

    profile = BarberProfile(
        user_id=user_id,
        shop_name=data["shop_name"],
        description=data.get("description"),
        address=data["address"],
        phone=data["phone"],
        email=data["email"]
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify({"msg": "Barber profile created"})


@app.route("/barber/operating-hours", methods=["POST"])
def set_operating_hours():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    barber_id = session["user_id"]

    OperatingHour.query.filter_by(barber_id=barber_id).delete()

    for day in data["hours"]:
        hour = OperatingHour(
            barber_id=barber_id,
            day=day["day"],
            open_time=day.get("open_time"),
            close_time=day.get("close_time"),
            closed=day.get("closed", False)
        )
        db.session.add(hour)

    db.session.commit()
    return jsonify({"msg": "Operating hours saved"})


@app.route("/barber/services", methods=["POST"])
def add_service():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json

    service = Service(
        barber_id=session["user_id"],
        name=data["name"],
        price=data["price"],
        duration=data["duration"],
        description=data.get("description")
    )

    db.session.add(service)
    db.session.commit()

    return jsonify({"msg": "Service added"})


@app.route("/barber/services/<int:service_id>", methods=["DELETE"])
def delete_service(service_id):
    service = Service.query.get(service_id)
    if not service or service.barber_id != session["user_id"]:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(service)
    db.session.commit()

    return jsonify({"msg": "Service removed"})



@app.route("/barber/team", methods=["POST"])
def add_team_member():
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json

    member = TeamMember(
        barber_id=session["user_id"],
        name=data["name"],
        specialization=data["specialization"]
    )

    db.session.add(member)
    db.session.commit()

    return jsonify({"msg": "Team member added"})


@app.route("/barber/team/<int:member_id>", methods=["DELETE"])
def remove_team_member(member_id):
    member = TeamMember.query.get(member_id)
    if not member or member.barber_id != session["user_id"]:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(member)
    db.session.commit()

    return jsonify({"msg": "Team member removed"})


# -------------------------------------------------
# BOOKINGS
# -------------------------------------------------

@app.route("/book", methods=["POST"])
def book():
    if session.get("role") != "customer":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json

    booking = Booking(
        barber_id=data["barber_id"],
        customer_id=session["user_id"],
        service_id=data["service_id"],
        team_member_id=data.get("team_member_id"),
        date=data["date"],
        time=data["time"],
        price=data["price"]
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({"msg": "Booking created", "status": "pending"})


@app.route("/barber/bookings/<int:booking_id>", methods=["PATCH"])
def update_booking(booking_id):
    if session.get("role") != "barber":
        return jsonify({"msg": "Unauthorized"}), 403

    booking = Booking.query.get(booking_id)
    if not booking or booking.barber_id != session["user_id"]:
        return jsonify({"msg": "Unauthorized"}), 403

    booking.status = request.json["status"]  # approved | rejected
    db.session.commit()

    return jsonify({"msg": "Booking updated"})


@app.route("/customer/bookings")
def customer_bookings():
    if session.get("role") != "customer":
        return jsonify({"msg": "Unauthorized"}), 403

    bookings = Booking.query.filter_by(customer_id=session["user_id"]).all()

    return jsonify([
        {
            "id": b.id,
            "date": b.date,
            "time": b.time,
            "status": b.status,
            "price": b.price
        } for b in bookings
    ])


@app.route("/barbers")
def list_barbers():
    barbers = BarberProfile.query.all()
    return jsonify([
        {
            "id": b.user_id,
            "shop_name": b.shop_name,
            "address": b.address,
            "phone": b.phone,
            "email": b.email
        } for b in barbers
    ])


if __name__ == "__main__":
    app.run(debug=True)
