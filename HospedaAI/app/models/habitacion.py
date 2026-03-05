from app import db

class Habitacion(db.Model):
    __tablename__ = "habitacion"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    tipo_id = db.Column(
        db.Integer,
        db.ForeignKey("tipo_habitacion.id"),
        nullable=False
    )

    reservas = db.relationship("Reserva", backref="habitacion", lazy=True)