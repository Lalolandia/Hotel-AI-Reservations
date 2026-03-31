# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app import db, login_manager
from app.models.cliente import Cliente
from app.forms import RegisterForm, LoginForm
from app.email import send_confirmation_email
from app.utils import confirm_token
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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
            nombre=form.nombre.data,
            telefono=form.telefono.data,
            correo=form.correo.data.lower(),
            edad=form.edad.data,
            genero=form.genero.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        sent = send_confirmation_email(user.correo)
        flash("Cuenta creada. Revisa tu correo para confirmar tu cuenta.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("El enlace de confirmación es inválido o ha expirado.", "danger")
        return redirect(url_for('main.index'))

    user = Cliente.query.filter_by(correo=email).first_or_404()
    if user.correo_confirmado:
        flash("Cuenta ya confirmada. Inicia sesión.", "info")
    else:
        user.correo_confirmado = True
        user.correo_confirmado_en = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash("¡Correo confirmado! Ya puedes iniciar sesión.", "success")
    return redirect(url_for('auth.login'))


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
            flash("Debes confirmar tu correo antes de iniciar sesión.", "warning")
            return render_template('auth/login.html', form=form)

        login_user(user)
        flash(f"¡Bienvenido, {user.nombre}!", "success")
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return Cliente.query.get(int(user_id))