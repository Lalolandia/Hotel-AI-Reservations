# app/utils.py
import random
import string
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


# ── Verificación de correo (registro) ──────────────────────────────────────────

def generate_confirmation_token(email: str) -> str:
    """Genera un token firmado que contiene el email del usuario."""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token: str, expiration: int = 3600 * 24) -> str | bool:
    """
    Verifica el token de confirmación.
    Devuelve el email si es válido, False si expiró o es inválido.
    Expira en 24 horas por defecto.
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except Exception:
        return False
    return email


# ── Recuperación de contraseña (código numérico) ────────────────────────────────

def generate_reset_code(length: int = 6) -> str:
    """Genera un código numérico aleatorio de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=length))


def generate_reset_token(email: str, code: str) -> str:
    """
    Genera un token firmado que vincula email + código.
    Se usa para validar el par sin guardar el código en la BD.
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'email': email, 'code': code}, salt='password-reset-salt')


def verify_reset_token(token: str, code: str, expiration: int = 3600) -> str | bool:
    """
    Verifica el token de recuperación y que el código coincida.
    Devuelve el email si todo es válido, False si no.
    Expira en 1 hora por defecto.
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return False

    if data.get('code') != code:
        return False

    return data.get('email')