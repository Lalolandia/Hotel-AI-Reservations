from flask import Blueprint, render_template, request
from app.models import Habitacion, Paquete
main = Blueprint('main', __name__)

@main.route('/')
def index():
    rooms = Habitacion.query.limit(3).all()
    return render_template('index.html', rooms=rooms)

@main.route('/rooms')
def rooms():
    rooms = Habitacion.query.all()
    return render_template('rooms.html', rooms=rooms)

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
    q = request.args.get('q','')
    dates = request.args.get('dates','')
    people = request.args.get('people',1, type=int)
    # crear lógica de búsqueda: filtrar habitaciones por tipo/capacidad
    rooms = Habitacion.query.filter(Habitacion.capacidad >= people).all()
    return render_template('rooms.html', rooms=rooms)

@main.route('/chat')
def chat():
    return render_template('chat.html')

