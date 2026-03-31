# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    correo = StringField('Correo', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    edad = IntegerField('Edad', validators=[Optional(), NumberRange(min=0, max=120)])
    genero = SelectField('Género', choices=[('', 'Seleccionar'), ('M','Masculino'),('F','Femenino'),('O','Otro')])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')