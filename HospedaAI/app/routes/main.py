# app/routes/main.py
from flask import Blueprint, render_template, request
from app.models import Habitacion, Paquete
from app.models.tipo_habitacion import TipoHabitacion

main = Blueprint('main', __name__)


@main.route('/')
def index():
    rooms = Habitacion.query.limit(3).all()
    return render_template('index.html', rooms=rooms)


@main.route('/rooms')
def rooms():
    # Filtros
    capacidad  = request.args.get('personas', 0, type=int)
    tipo_id    = request.args.get('tipo', 0, type=int)
    precio_max = request.args.get('precio_max', 0, type=int)

    query = Habitacion.query.join(TipoHabitacion)

    if capacidad > 0:
        query = query.filter(TipoHabitacion.capacidad >= capacidad)

    if tipo_id > 0:
        query = query.filter(Habitacion.tipo_id == tipo_id)

    if precio_max > 0:
        query = query.filter(TipoHabitacion.precio_noche <= precio_max)

    habitaciones = query.all()
    tipos        = TipoHabitacion.query.all()

    return render_template('habitaciones/rooms.html',
                           rooms=habitaciones,
                           tipos=tipos,
                           filtro_capacidad=capacidad,
                           filtro_tipo=tipo_id,
                           filtro_precio=precio_max)


@main.route('/room/<int:room_id>')
def room_detail(room_id):
    room = Habitacion.query.get_or_404(room_id)
    return render_template('habitaciones/room_detail.html', room=room)



@main.route('/packages')
def packages():
    packages = Paquete.query.all()
    return render_template('packages.html', packages=packages)


@main.route('/search')
def search():
    q       = request.args.get('q', '')
    people  = request.args.get('people', 1, type=int)
    # Redirige a /rooms con el filtro de personas aplicado
    from flask import redirect, url_for
    return redirect(url_for('main.rooms', personas=people))


@main.route('/chat')
def chat():
    return render_template('chatAI/chat.html')