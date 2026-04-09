# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class RegisterForm(FlaskForm):
    nombre    = StringField('Nombre',             validators=[DataRequired(), Length(max=100)])
    telefono  = StringField('Teléfono',           validators=[Optional(), Length(max=20)])
    correo    = StringField('Correo',             validators=[DataRequired(), Email(), Length(max=120)])
    password  = PasswordField('Contraseña',       validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden.')])
    edad      = IntegerField('Edad',              validators=[Optional(), NumberRange(min=0, max=120)])
    genero    = SelectField('Género',             choices=[('', 'Seleccionar'), ('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')])
    submit    = SubmitField('Registrarse')


class LoginForm(FlaskForm):
    correo   = StringField('Correo',    validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit   = SubmitField('Iniciar sesión')


class ForgotPasswordForm(FlaskForm):
    correo = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar código')


class ResetPasswordForm(FlaskForm):
    codigo    = StringField('Código de verificación', validators=[DataRequired(), Length(min=6, max=6)])
    password  = PasswordField('Nueva contraseña',     validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden.')])
    submit    = SubmitField('Cambiar contraseña')


class ProfileForm(FlaskForm):
    """Formulario para editar datos del perfil (sin cambiar correo ni contraseña)."""
    nombre   = StringField('Nombre completo', validators=[DataRequired(), Length(max=100)])
    telefono = StringField('Teléfono',        validators=[Optional(), Length(max=20)])
    edad     = IntegerField('Edad',           validators=[Optional(), NumberRange(min=0, max=120)])
    genero   = SelectField('Género',          choices=[('', 'Seleccionar'), ('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')])
    submit   = SubmitField('Guardar cambios')


class ChangePasswordForm(FlaskForm):
    """Formulario para cambiar contraseña desde el perfil."""
    password_actual  = PasswordField('Contraseña actual',    validators=[DataRequired()])
    password_nueva   = PasswordField('Nueva contraseña',     validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password_nueva', message='Las contraseñas no coinciden.')])
    submit           = SubmitField('Cambiar contraseña')