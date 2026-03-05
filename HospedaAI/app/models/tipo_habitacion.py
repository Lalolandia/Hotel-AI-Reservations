from app import db

class TipoHabitacion(db.Model):
    __tablename__ = "tipo_habitacion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    precio_noche = db.Column(db.Numeric(10,2), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)

    habitaciones = db.relationship("Habitacion", backref="tipo", lazy=True)