from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS

from config import SECRET_KEY, ADMIN_PASSWORD
from database import db, init_db
from models import Barber, Customer, Service, Booking

app = Flask(__name__)

app.config.update(
    SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI="sqlite:///barbing.db",
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,      
)



CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"]
)



init_db(app)

@app.route("/admin/login", methods=["POST"])
def admin_login():
    if request.json.get("password") == ADMIN_PASSWORD:
        session["admin"] = True
        return jsonify({"msg": "Admin logged in"})
    return jsonify({"msg": "Invalid admin password"}), 401

@app.route("/admin/pending-barbers")
def pending_barbers():
    if not session.get("admin"):
        return jsonify({"msg": "Unauthorized"}), 403
    barbers = Barber.query.filter_by(status="pending").all()
    return jsonify([{
        "id": b.id,
        "name": b.name,
        "shop_name": b.shop_name,
        "phone": b.phone
    } for b in barbers])

@app.route("/admin/approve/<int:barber_id>", methods=["POST"])
def approve_barber(barber_id):
    if not session.get("admin"):
        return jsonify({"msg": "Unauthorized"}), 403
    barber = Barber.query.get(barber_id)
    barber.status = "approved"
    db.session.commit()
    return jsonify({"msg": "Barber approved"})

@app.route("/admin/reject/<int:barber_id>", methods=["POST"])
def reject_barber(barber_id):
    if not session.get("admin"):
        return jsonify({"msg": "Unauthorized"}), 403
    barber = Barber.query.get(barber_id)
    barber.status = "rejected"
    db.session.commit()
    return jsonify({"msg": "Barber rejected"})


@app.route("/barber/register", methods=["POST"])
def barber_register():
    data = request.json
    barber = Barber(
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        shop_name=data["shop_name"],
        address=data["address"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(barber)
    db.session.commit()
    return jsonify({"msg": "Barber registered, awaiting approval"})

@app.route("/barber/login", methods=["POST"])
def barber_login():
    data = request.json
    barber = Barber.query.filter(
        (Barber.email == data["login"]) | (Barber.phone == data["login"])
    ).first()

    if barber and check_password_hash(barber.password, data["password"]):
        session["barber_id"] = barber.id
        return jsonify({"msg": "Login successful", "status": barber.status})
    return jsonify({"msg": "Invalid credentials"}), 401

@app.route("/barber/forgot-password", methods=["POST"])
def barber_forgot_password():
    data = request.json
    barber = Barber.query.filter(
        (Barber.email == data["login"]) | (Barber.phone == data["login"])
    ).first()
    if not barber:
        return jsonify({"msg": "Email or phone not registered"}), 404

    barber.password = generate_password_hash(data["new_password"])
    db.session.commit()
    return jsonify({"msg": "Password updated successfully"})

@app.route("/barber/services", methods=["POST"])
def add_service():
    barber_id = session.get("barber_id")
    barber = Barber.query.get(barber_id)
    if not barber or barber.status != "approved":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    service = Service(
        barber_id=barber_id,
        name=data["name"],
        price=data["price"]
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({"msg": "Service added"})

@app.route("/barber/bookings")
def barber_bookings():
    barber_id = session.get("barber_id")
    bookings = Booking.query.filter_by(barber_id=barber_id).all()
    return jsonify([{
        "id": b.id,
        "service": b.service_name,
        "date": b.date,
        "time": b.time,
        "status": b.status
    } for b in bookings])

@app.route("/barber/booking/<int:booking_id>", methods=["PATCH"])
def update_booking(booking_id):
    barber_id = session.get("barber_id")
    booking = Booking.query.get(booking_id)
    if not booking or booking.barber_id != barber_id:
        return jsonify({"msg": "Unauthorized"}), 403

    booking.status = request.json.get("status", booking.status)
    db.session.commit()
    return jsonify({"msg": "Booking updated"})


@app.route("/customer/register", methods=["POST"])
def customer_register():
    data = request.json
    customer = Customer(
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({"msg": "Customer registered"})

@app.route("/customer/login", methods=["POST"])
def customer_login():
    data = request.json
    customer = Customer.query.filter(
        (Customer.email == data["login"]) | (Customer.phone == data["login"])
    ).first()

    if customer and check_password_hash(customer.password, data["password"]):
        session["customer_id"] = customer.id
        return jsonify({"msg": "Login successful"})
    return jsonify({"msg": "Invalid credentials"}), 401

@app.route("/customer/forgot-password", methods=["POST"])
def customer_forgot_password():
    data = request.json
    customer = Customer.query.filter(
        (Customer.email == data["login"]) | (Customer.phone == data["login"])
    ).first()
    if not customer:
        return jsonify({"msg": "Email or phone not registered"}), 404

    customer.password = generate_password_hash(data["new_password"])
    db.session.commit()
    return jsonify({"msg": "Password updated successfully"})

@app.route("/barbers")
def list_barbers():
    barbers = Barber.query.filter_by(status="approved").all()
    return jsonify([{
        "id": b.id,
        "shop_name": b.shop_name
    } for b in barbers])

@app.route("/book", methods=["POST"])
def book_barber():
    customer_id = session.get("customer_id")
    data = request.json

    existing = Booking.query.filter_by(
        barber_id=data["barber_id"],
        date=data["date"],
        time=data["time"]
    ).first()
    if existing:
        return jsonify({"msg": "Time already booked"}), 400

    booking = Booking(
        barber_id=data["barber_id"],
        customer_id=customer_id,
        service_name=data["service"],
        date=data["date"],
        time=data["time"],
        location=data["location"]
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({"msg": "Booking created"})

@app.route("/my-bookings")
def my_bookings():
    customer_id = session.get("customer_id")
    bookings = Booking.query.filter_by(customer_id=customer_id).all()
    return jsonify([{
        "id": b.id,
        "date": b.date,
        "time": b.time,
        "status": b.status
    } for b in bookings])

@app.route("/cancel/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    customer_id = session.get("customer_id")
    booking = Booking.query.get(booking_id)
    if not booking or booking.customer_id != customer_id:
        return jsonify({"msg": "Unauthorized"}), 403

    booking_time = datetime.strptime(
        f"{booking.date} {booking.time}", "%Y-%m-%d %H:%M"
    )
    if datetime.now() + timedelta(hours=2) > booking_time:
        return jsonify({"msg": "Too late to cancel"}), 400

    db.session.delete(booking)
    db.session.commit()
    return jsonify({"msg": "Booking cancelled"})


if __name__ == "__main__":
    app.run(debug=True)
