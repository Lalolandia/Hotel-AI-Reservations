# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db, login_manager
from app.models.cliente import Cliente
from app.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.email import send_confirmation_email, send_reset_password_email
from app.utils import confirm_token, generate_reset_code, generate_reset_token, verify_reset_token
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ════════════════════════════════════════
#  REGISTRO
# ════════════════════════════════════════

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if Cliente.query.filter_by(correo=form.correo.data.lower()).first():
            flash("Ya existe una cuenta con ese correo.", "warning")
            return render_template('auth/register.html', form=form)

        user = Cliente(
            nombre   = form.nombre.data,
            telefono = form.telefono.data,
            correo   = form.correo.data.lower(),
            edad     = form.edad.data,
            genero   = form.genero.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        send_confirmation_email(user.correo)
        flash("¡Cuenta creada! Revisa tu correo para confirmar tu cuenta.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# ════════════════════════════════════════
#  CONFIRMAR CORREO
# ════════════════════════════════════════

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("El enlace de confirmación es inválido o ha expirado.", "danger")
        return redirect(url_for('main.index'))

    user = Cliente.query.filter_by(correo=email).first_or_404()
    if user.correo_confirmado:
        flash("Tu cuenta ya estaba confirmada. Inicia sesión.", "info")
    else:
        user.correo_confirmado    = True
        user.correo_confirmado_en = datetime.utcnow()
        db.session.commit()
        flash("¡Correo confirmado exitosamente! Ya puedes iniciar sesión. 🎉", "success")

    return redirect(url_for('auth.login'))


# ════════════════════════════════════════
#  LOGIN
# ════════════════════════════════════════

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Cliente.query.filter_by(correo=form.correo.data.lower()).first()

        if user is None or not user.check_password(form.password.data):
            flash("Correo o contraseña incorrectos.", "danger")
            return render_template('auth/login.html', form=form)

        if not user.correo_confirmado:
            flash("Debes confirmar tu correo antes de iniciar sesión. Revisa tu bandeja.", "warning")
            return render_template('auth/login.html', form=form)

        login_user(user)
        flash(f"¡Bienvenido de vuelta, {user.nombre.split()[0]}! 👋", "success")
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)


# ════════════════════════════════════════
#  LOGOUT
# ════════════════════════════════════════

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('main.index'))


# ════════════════════════════════════════
#  PERFIL
# ════════════════════════════════════════

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')


# ════════════════════════════════════════
#  RECUPERACIÓN — Paso 1: ingresar correo
# ════════════════════════════════════════

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        correo = form.correo.data.lower()
        user   = Cliente.query.filter_by(correo=correo).first()

        # Mismo mensaje siempre — no revelar si el correo existe
        flash("Si ese correo está registrado, recibirás un código en breve.", "info")

        if user:
            code  = generate_reset_code()
            token = generate_reset_token(correo, code)
            session['reset_token'] = token
            send_reset_password_email(correo, user.nombre, code)

        return redirect(url_for('auth.reset_password'))

    return render_template('auth/forgot_password.html', form=form)


# ════════════════════════════════════════
#  RECUPERACIÓN — Paso 2: código + nueva clave
# ════════════════════════════════════════

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    token = session.get('reset_token')
    if not token:
        flash("Primero solicita el restablecimiento de contraseña.", "warning")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        code  = form.codigo.data.strip()
        email = verify_reset_token(token, code, expiration=3600)

        if not email:
            flash("El código es incorrecto o ha expirado. Solicita uno nuevo.", "danger")
            return render_template('auth/reset_password.html', form=form)

        user = Cliente.query.filter_by(correo=email).first()
        if not user:
            flash("No se encontró una cuenta con ese correo.", "danger")
            return redirect(url_for('auth.forgot_password'))

        user.set_password(form.password.data)
        db.session.commit()
        session.pop('reset_token', None)

        flash("¡Contraseña actualizada exitosamente! Ya puedes iniciar sesión. 🔐", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


# ════════════════════════════════════════
#  REENVIAR VERIFICACIÓN
# ════════════════════════════════════════

@auth_bp.route('/resend-confirmation', methods=['POST'])
def resend_confirmation():
    correo = request.form.get('correo', '').lower()
    user   = Cliente.query.filter_by(correo=correo).first()
    if user and not user.correo_confirmado:
        send_confirmation_email(user.correo)
    flash("Si tu cuenta existe y no está confirmada, recibirás un nuevo correo.", "info")
    return redirect(url_for('auth.login'))


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return Cliente.query.get(int(user_id))