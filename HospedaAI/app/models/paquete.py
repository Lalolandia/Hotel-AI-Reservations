from app import db

class Paquete(db.Model):
    __tablename__ = "paquete"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_total = db.Column(db.Numeric(10,2), nullable=False)

    reservas = db.relationship("Reserva", backref="paquete", lazy=True)