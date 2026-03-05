from app import db
from datetime import datetime

class Chat(db.Model):
    __tablename__ = "chat"

    id = db.Column(db.Integer, primary_key=True)
    mensaje_usuario = db.Column(db.Text, nullable=False)
    respuesta_ia = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("cliente.id"),
        nullable=False
    )