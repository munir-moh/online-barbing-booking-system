from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
from models import db, User, Appointment
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///barbing.db"
app.config["JWT_SECRET_KEY"] = "super-secret-key"

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# Barber working hours
OPEN_TIME = time(10, 0)
CLOSE_TIME = time(22, 0)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({"access_token": token})


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"message": "Email not registered"}), 404

    user.password = generate_password_hash(data["new_password"])
    db.session.commit()

    return jsonify({"message": "Password reset successful"})


@app.route("/appointments", methods=["POST"])
@jwt_required()
def create_appointment():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    start_time = datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M")
    duration = data.get("duration", 30)
    end_time = start_time + timedelta(minutes=duration)

    if start_time < datetime.now():
        return jsonify({"message": "Cannot book in the past"}), 400

    if not (OPEN_TIME <= start_time.time() < CLOSE_TIME and OPEN_TIME < end_time.time() <= CLOSE_TIME):
        return jsonify({"message": "Working hours are 10:00 AM - 10:00 PM"}), 400

    conflict = Appointment.query.filter(
        Appointment.status.in_(["pending", "approved"]),
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
    ).first()

    if conflict:
        return jsonify({"message": "Time slot already booked"}), 409

    appointment = Appointment(
        user_id=user_id,
        service=data["service"],
        start_time=start_time,
        end_time=end_time
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment booked"}), 201


@app.route("/appointments", methods=["GET"])
@jwt_required()
def my_appointments():
    user_id = int(get_jwt_identity())

    appointments = Appointment.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": a.id,
            "service": a.service,
            "start_time": a.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": a.end_time.strftime("%Y-%m-%d %H:%M"),
            "status": a.status
        } for a in appointments
    ])


@app.route("/appointments/<int:id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_appointment(id):
    user_id = int(get_jwt_identity())
    appointment = Appointment.query.get_or_404(id)

    if appointment.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    appointment.status = "cancelled"
    db.session.commit()

    return jsonify({"message": "Appointment cancelled"})


@app.route("/admin/appointments", methods=["GET"])
@jwt_required()
def admin_view():
    claims = get_jwt()

    if claims["role"] != "admin":
        return jsonify({"message": "Admin access required"}), 403

    appointments = Appointment.query.all()

    return jsonify([
        {
            "id": a.id,
            "user_id": a.user_id,
            "service": a.service,
            "start_time": a.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": a.end_time.strftime("%Y-%m-%d %H:%M"),
            "status": a.status
        } for a in appointments
    ])


@app.route("/admin/appointments/<int:id>", methods=["PUT"])
@jwt_required()
def update_status(id):
    claims = get_jwt()

    if claims["role"] != "admin":
        return jsonify({"message": "Admin only"}), 403

    appointment = Appointment.query.get_or_404(id)
    appointment.status = request.json["status"]
    db.session.commit()

    return jsonify({"message": "Status updated"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
