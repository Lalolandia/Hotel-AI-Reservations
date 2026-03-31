# app/email.py
from flask_mail import Message
from flask import url_for, current_app
from app import mail
import os

def send_confirmation_email(user_email):
    token = None
    from app.utils import generate_confirmation_token
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = f"""
    <p>Hola,</p>
    <p>Gracias por registrarte. Por favor confirma tu correo haciendo click en el link:</p>
    <p><a href="{confirm_url}">Confirmar correo</a></p>
    <p>Si no funciona, copia y pega esta URL en el navegador:</p>
    <p>{confirm_url}</p>
    """
    subject = "Confirma tu correo - Hotel Reservations"
    msg = Message(subject=subject, recipients=[user_email], html=html)
    # Si no configuras mail en .env, Mail puede lanzar error. En dev, imprime en consola:
    try:
        mail.send(msg)
        return True
    except Exception as e:
        # fallback: imprimir la URL en consola para pruebas locales
        current_app.logger.warning(f"No se pudo enviar email, token URL: {confirm_url} - error: {e}")
        print("VERIFICACION URL:", confirm_url)
        return False