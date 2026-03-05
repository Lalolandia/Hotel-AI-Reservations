from app import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    reservas = db.relationship("Reserva", backref="cliente", lazy=True)
    chats = db.relationship("Chat", backref="cliente", lazy=True)