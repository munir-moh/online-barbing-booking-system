from datetime import datetime
from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    barber_profile = db.relationship("BarberProfile", backref="user", uselist=False)
    bookings = db.relationship("Booking", backref="customer", foreign_keys="Booking.customer_id")


class BarberProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    shop_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    services = db.relationship("Service", backref="barber", cascade="all, delete-orphan")
    team_members = db.relationship("TeamMember", backref="barber", cascade="all, delete-orphan")
    operating_hours = db.relationship("OperatingHour", backref="barber", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", backref="barber_profile", foreign_keys="Booking.barber_id")


class OperatingHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_id = db.Column(db.Integer, db.ForeignKey("barber_profile.id"), nullable=False)

    day = db.Column(db.String(10), nullable=False)  # Monday - Sunday
    open_time = db.Column(db.String(10), nullable=True)   # "09:00"
    close_time = db.Column(db.String(10), nullable=True)  # "18:00"
    is_closed = db.Column(db.Boolean, default=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_id = db.Column(db.Integer, db.ForeignKey("barber_profile.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_id = db.Column(db.Integer, db.ForeignKey("barber_profile.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    barber_id = db.Column(db.Integer, db.ForeignKey("barber_profile.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    team_member = db.Column(db.String(120), nullable=True)

    appointment_date = db.Column(db.String(20), nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)

    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
