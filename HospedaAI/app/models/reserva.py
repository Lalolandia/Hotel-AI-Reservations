# app/models/reserva.py
from app import db

class Reserva(db.Model):
    __tablename__ = "reserva"

    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    # FK corregidas: deben coincidir con __tablename__ de cada modelo
    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),   # era "cliente.id" — INCORRECTO
        nullable=False
    )

    habitacion_id = db.Column(
        db.Integer,
        db.ForeignKey("habitacion.id"),
        nullable=False
    )

    paquete_id = db.Column(
        db.Integer,
        db.ForeignKey("paquete.id"),
        nullable=True
    )