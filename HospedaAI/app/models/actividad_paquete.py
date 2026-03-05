from app import db

class ActividadPaquete(db.Model):
    __tablename__ = "actividad_paquete"

    paquete_id = db.Column(
        db.Integer,
        db.ForeignKey("paquete.id"),
        primary_key=True
    )

    actividad_id = db.Column(
        db.Integer,
        db.ForeignKey("actividad.id"),
        primary_key=True
    )