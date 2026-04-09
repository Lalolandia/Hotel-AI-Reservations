# app/email.py
from flask_mail import Message
from flask import url_for, current_app
from app import mail


# ── Estilos compartidos ─────────────────────────────────────────────────────────

_BASE_STYLE = """
    body { margin:0; padding:0; background:#F8F4EF; font-family:'Segoe UI',Arial,sans-serif; }
    .wrapper { max-width:560px; margin:40px auto; background:#ffffff;
               border-radius:16px; overflow:hidden;
               box-shadow:0 4px 24px rgba(0,0,0,0.08); }
    .header  { background:linear-gradient(135deg,#1A1916,#2A2010);
               padding:40px 48px; text-align:center; }
    .brand   { font-size:28px; font-weight:700; color:#ffffff; letter-spacing:-0.5px; }
    .brand span { color:#C9A86C; }
    .body    { padding:40px 48px; }
    .title   { font-size:22px; font-weight:600; color:#1A1916; margin:0 0 12px; }
    .text    { font-size:15px; color:#5A5650; line-height:1.7; margin:0 0 24px; }
    .btn     { display:inline-block; background:#C9A86C; color:#ffffff !important;
               padding:14px 36px; border-radius:8px; font-size:15px;
               font-weight:600; text-decoration:none; }
    .code-box{ background:#F8F4EF; border:2px dashed #C9A86C; border-radius:12px;
               padding:24px; text-align:center; margin:24px 0; }
    .code    { font-size:42px; font-weight:700; letter-spacing:14px;
               color:#1A1916; font-family:monospace; }
    .expire  { font-size:13px; color:#9A9690; margin-top:8px; }
    .divider { border:none; border-top:1px solid #EDE9E4; margin:28px 0; }
    .footer  { background:#F0EBE4; padding:24px 48px; text-align:center; }
    .footer p{ font-size:12px; color:#9A9690; margin:0; line-height:1.6; }
    .warning { font-size:13px; color:#B07020; background:#FEF3E2;
               border-radius:8px; padding:12px 16px; margin-top:20px; }
"""


def _html_email(body_content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><style>{_BASE_STYLE}</style></head>
    <body>
      <div class="wrapper">
        <div class="header">
          <div class="brand">Hotel<span>AI</span></div>
        </div>
        <div class="body">{body_content}</div>
        <div class="footer">
          <p>© 2026 HotelAI Reservations · San José, Costa Rica</p>
        </div>
      </div>
    </body>
    </html>
    """


def _send(subject: str, recipients: list, html: str,
          fallback: str = "", label: str = "EMAIL") -> bool:
    """Envía el correo via Flask-Mail (Gmail). Si falla imprime fallback en consola."""
    try:
        msg = Message(subject=subject, recipients=recipients, html=html)
        mail.send(msg)
        current_app.logger.info(f"[EMAIL] Enviado a {recipients[0]}: {subject}")
        return True
    except Exception as e:
        current_app.logger.warning(f"[EMAIL] Fallo al enviar: {e}")
        print(f"\n{'='*60}")
        print(f"  {label}: {fallback}")
        print(f"  ERROR: {e}")
        print(f"{'='*60}\n")
        return False


# ── 1. Verificación de cuenta ───────────────────────────────────────────────────

def send_confirmation_email(user_email: str) -> bool:
    from app.utils import generate_confirmation_token

    token       = generate_confirmation_token(user_email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    html = _html_email(f"""
        <h1 class="title">Confirma tu cuenta ✉️</h1>
        <p class="text">
            Gracias por registrarte en <strong>HotelAI</strong>.<br>
            Haz clic en el botón para verificar tu correo y activar tu cuenta.
        </p>
        <p style="text-align:center;margin:32px 0">
            <a class="btn" href="{confirm_url}">Verificar mi cuenta</a>
        </p>
        <hr class="divider">
        <p class="text" style="font-size:13px;color:#9A9690">
            Si el botón no funciona, copia y pega este enlace:<br>
            <a href="{confirm_url}" style="color:#C9A86C;word-break:break-all">{confirm_url}</a>
        </p>
        <div class="warning">
            ⚠️ Este enlace expira en <strong>24 horas</strong>.
            Si no creaste esta cuenta, ignora este mensaje.
        </div>
    """)

    return _send(
        subject    = "✅ Verifica tu cuenta — HotelAI",
        recipients = [user_email],
        html       = html,
        fallback   = confirm_url,
        label      = "VERIFICACION URL"
    )


# ── 2. Recuperación de contraseña ───────────────────────────────────────────────

def send_reset_password_email(user_email: str, user_nombre: str, code: str) -> bool:

    html = _html_email(f"""
        <h1 class="title">Restablecer contraseña 🔐</h1>
        <p class="text">
            Hola <strong>{user_nombre}</strong>,<br>
            recibimos una solicitud para restablecer la contraseña de tu cuenta.
            Usa el siguiente código:
        </p>
        <div class="code-box">
            <div class="code">{code}</div>
            <div class="expire">⏱ Expira en <strong>1 hora</strong></div>
        </div>
        <p class="text">
            Ingresa este código en la página de recuperación de contraseña.
        </p>
        <hr class="divider">
        <div class="warning">
            🔒 Si no solicitaste esto, ignora este mensaje. Tu cuenta está segura.
        </div>
    """)

    return _send(
        subject    = "🔑 Código para restablecer contraseña — HotelAI",
        recipients = [user_email],
        html       = html,
        fallback   = f"CODIGO DE RESET: {code}",
        label      = "RESET CODE"
    )