# app/models/cliente.py
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Cliente(db.Model):

    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    telefono = db.Column(db.String(20))

    edad = db.Column(db.Integer)

    genero = db.Column(db.String(20))

    password_hash = db.Column(db.String(200))

    email_verificado = db.Column(db.Boolean, default=False)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)