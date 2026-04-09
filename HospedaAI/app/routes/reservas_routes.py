from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app import db
from app.models.reserva import Reserva
from app.models.cliente import Cliente
from app.models.habitacion import Habitacion

reservas_bp = Blueprint('reservas', __name__)


# =========================
# VISTAS (WEB)
# =========================

@reservas_bp.route('/reservas')
def listar_reservas():
    reservas = Reserva.query.all()
    return render_template('reservas/lista.html', reservas=reservas)


@reservas_bp.route('/reservar', methods=['GET', 'POST'])
def crear_reserva():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        habitacion_id = request.form['habitacion_id']
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(request.form['fecha_fin'], "%Y-%m-%d").date()

        noches = (fecha_fin - fecha_inicio).days

        habitacion = Habitacion.query.get(habitacion_id)
        precio_noche = habitacion.tipo.precio_noche
        total = noches * float(precio_noche)

        nueva_reserva = Reserva(
            cliente_id=cliente_id,
            habitacion_id=habitacion_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total=total
        )

        db.session.add(nueva_reserva)
        db.session.commit()

        flash("Reserva creada correctamente", "success")
        return redirect(url_for('reservas.listar_reservas'))

    clientes = Cliente.query.all()
    habitaciones = Habitacion.query.all()

    return render_template(
        'reservas/crear.html',
        clientes=clientes,
        habitaciones=habitaciones
    )


@reservas_bp.route('/reserva/<int:id>')
def detalle_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    return render_template('reservas/detalles.html', reserva=reserva)


@reservas_bp.route('/cancelar_reserva/<int:id>')
def cancelar_reserva(id):
    reserva = Reserva.query.get_or_404(id)

    db.session.delete(reserva)
    db.session.commit()

    flash("Reserva cancelada correctamente", "success")
    return redirect(url_for('reservas.listar_reservas'))


# =========================
# API REST
# =========================

@reservas_bp.route('/api/reservas', methods=['GET'])
def api_listar_reservas():
    reservas = Reserva.query.all()

    return jsonify([
        {
            "id": r.id,
            "cliente_id": r.cliente_id,
            "habitacion_id": r.habitacion_id,
            "fecha_inicio": str(r.fecha_inicio),
            "fecha_fin": str(r.fecha_fin),
            "total": float(r.total)
        }
        for r in reservas
    ])


@reservas_bp.route('/api/reservas', methods=['POST'])
def api_crear_reserva():
    data = request.json

    fecha_inicio = datetime.strptime(data['fecha_inicio'], "%Y-%m-%d").date()
    fecha_fin = datetime.strptime(data['fecha_fin'], "%Y-%m-%d").date()

    noches = (fecha_fin - fecha_inicio).days

    habitacion = Habitacion.query.get(data['habitacion_id'])
    precio_noche = habitacion.tipo.precio_noche
    total = noches * float(precio_noche)

    nueva_reserva = Reserva(
        cliente_id=data['cliente_id'],
        habitacion_id=data['habitacion_id'],
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total=total
    )

    db.session.add(nueva_reserva)
    db.session.commit()

    return jsonify({
        "message": "Reserva creada correctamente",
        "id": nueva_reserva.id
    })


@reservas_bp.route('/api/reservas/<int:id>', methods=['DELETE'])
def api_delete_reserva(id):
    reserva = Reserva.query.get_or_404(id)

    db.session.delete(reserva)
    db.session.commit()

    return jsonify({
        "message": "Reserva eliminada correctamente"
    })