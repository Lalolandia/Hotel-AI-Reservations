# app/models/habitacion.py
from app import db


class Habitacion(db.Model):
    __tablename__ = "habitacion"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    piso = db.Column(db.Integer, nullable=True)  # campo faltante — agregado
    estado = db.Column(db.String(20), nullable=False)  # ej: "disponible", "ocupada"
    capacidad = db.Column(db.Integer, nullable=True)  # campo faltante — agregado

    tipo_id = db.Column(
        db.Integer,
        db.ForeignKey("tipo_habitacion.id"),
        nullable=False
    )

    reservas = db.relationship("Reserva", backref="habitacion", lazy=True)

    def __repr__(self):
        return f"<Habitacion {self.numero}>"
