from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_

from app.models import Habitacion, Paquete, TipoHabitacion

main = Blueprint('main', __name__)


@main.route('/')
def index():
    rooms = Habitacion.query.limit(3).all()
    return render_template('index.html', rooms=rooms)


@main.route('/rooms')
def rooms():
    return redirect(url_for('habitaciones.listar'))


@main.route('/room/<int:room_id>')
def room_detail(room_id):
    room = Habitacion.query.get_or_404(room_id)
    return render_template('room_detail.html', room=room)


@main.route('/packages')
def packages():
    packages = Paquete.query.all()
    return render_template('packages.html', packages=packages)


@main.route('/search')
def search():
    q = request.args.get('q', '')
    dates = request.args.get('dates', '')
    people = request.args.get('people', 1, type=int)

    query = Habitacion.query.join(Habitacion.tipo)

    if q:
        query = query.filter(
            or_(
                Habitacion.numero.ilike(f'%{q}%'),
                TipoHabitacion.nombre.ilike(f'%{q}%'),
            )
        )

    habitaciones = [
        room for room in query.all()
        if room.tipo and room.tipo.capacidad >= people
    ]

    return render_template(
        'habitaciones/lista.html',
        habitaciones=habitaciones,
        search_term=q,
        dates=dates,
        people=people,
    )


@main.route('/chat')
def chat():
    return render_template('chat.html')
