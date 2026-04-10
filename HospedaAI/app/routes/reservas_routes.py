# app/routes/reservas_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from app import db
from app.models.reserva import Reserva
from app.models.cliente import Cliente
from app.models.habitacion import Habitacion
from flask_login import login_required, current_user

reservas_bp = Blueprint('reservas', __name__)


# ════════════════════════════════════════
#  LISTAR RESERVAS
# ════════════════════════════════════════

@reservas_bp.route('/reservas')
@login_required
def listar_reservas():
    # Cada usuario solo ve SUS reservas
    reservas = Reserva.query.filter_by(cliente_id=current_user.id).all()
    return render_template('reservas/lista.html', reservas=reservas)


# ════════════════════════════════════════
#  CREAR RESERVA
# ════════════════════════════════════════

@reservas_bp.route('/reservar', methods=['GET', 'POST'])
@login_required
def crear_reserva():
    # Parámetros que pueden venir desde room_detail via GET
    habitacion_id_pre  = request.args.get('habitacion_id', type=int)
    fecha_inicio_pre   = request.args.get('fecha_inicio', '')
    fecha_fin_pre      = request.args.get('fecha_fin', '')

    if request.method == 'POST':
        habitacion_id = request.form.get('habitacion_id', type=int)
        fecha_inicio_str = request.form.get('fecha_inicio', '')
        fecha_fin_str    = request.form.get('fecha_fin', '')

        # ── Validar fechas ──────────────────────────────────────────
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            fecha_fin    = datetime.strptime(fecha_fin_str,    "%Y-%m-%d").date()
        except ValueError:
            flash("Las fechas ingresadas no son válidas.", "danger")
            return redirect(request.url)

        if fecha_inicio < date.today():
            flash("La fecha de inicio no puede ser en el pasado.", "danger")
            return redirect(request.url)

        if fecha_fin <= fecha_inicio:
            flash("La fecha de salida debe ser posterior a la de entrada.", "danger")
            return redirect(request.url)

        # ── Validar habitación ──────────────────────────────────────
        habitacion = Habitacion.query.get_or_404(habitacion_id)

        if habitacion.estado != 'disponible':
            flash("Esta habitación no está disponible para reservar.", "warning")
            return redirect(request.url)

        # ── Verificar que no haya reserva solapada ──────────────────
        solapada = Reserva.query.filter(
            Reserva.habitacion_id == habitacion_id,
            Reserva.fecha_fin   >  fecha_inicio,
            Reserva.fecha_inicio < fecha_fin
        ).first()

        if solapada:
            flash("La habitación ya tiene una reserva en esas fechas.", "warning")
            return redirect(request.url)

        # ── Calcular total ──────────────────────────────────────────
        noches = (fecha_fin - fecha_inicio).days
        total  = noches * float(habitacion.tipo.precio_noche)

        # ── Guardar reserva ─────────────────────────────────────────
        nueva_reserva = Reserva(
            cliente_id    = current_user.id,   # siempre el usuario logueado
            habitacion_id = habitacion_id,
            fecha_inicio  = fecha_inicio,
            fecha_fin     = fecha_fin,
            total         = total
        )

        db.session.add(nueva_reserva)
        db.session.commit()

        flash(f"¡Reserva creada correctamente! Total: ${total:.2f}", "success")
        return redirect(url_for('reservas.detalle_reserva', id=nueva_reserva.id))

    # GET — mostrar formulario
    habitaciones = Habitacion.query.filter_by(estado='disponible').all()

    return render_template(
        'reservas/crear.html',
        habitaciones     = habitaciones,
        habitacion_id_pre = habitacion_id_pre,
        fecha_inicio_pre  = fecha_inicio_pre,
        fecha_fin_pre     = fecha_fin_pre
    )


# ════════════════════════════════════════
#  DETALLE DE RESERVA
# ════════════════════════════════════════

@reservas_bp.route('/reserva/<int:id>')
@login_required
def detalle_reserva(id):
    reserva = Reserva.query.get_or_404(id)

    # Solo el dueño de la reserva puede verla
    if reserva.cliente_id != current_user.id:
        flash("No tienes permiso para ver esta reserva.", "danger")
        return redirect(url_for('reservas.listar_reservas'))

    noches = (reserva.fecha_fin - reserva.fecha_inicio).days
    return render_template('reservas/detalles.html', reserva=reserva, noches=noches)


# ════════════════════════════════════════
#  CANCELAR RESERVA (POST — seguro)
# ════════════════════════════════════════

@reservas_bp.route('/cancelar_reserva/<int:id>', methods=['POST'])
@login_required
def cancelar_reserva(id):
    reserva = Reserva.query.get_or_404(id)

    # Solo el dueño puede cancelar
    if reserva.cliente_id != current_user.id:
        flash("No tienes permiso para cancelar esta reserva.", "danger")
        return redirect(url_for('reservas.listar_reservas'))

    # No cancelar reservas pasadas
    if reserva.fecha_inicio <= date.today():
        flash("No se puede cancelar una reserva que ya comenzó.", "warning")
        return redirect(url_for('reservas.detalle_reserva', id=id))

    db.session.delete(reserva)
    db.session.commit()

    flash("Reserva cancelada correctamente.", "success")
    return redirect(url_for('reservas.listar_reservas'))


# ════════════════════════════════════════
#  API REST
# ════════════════════════════════════════

@reservas_bp.route('/api/reservas', methods=['GET'])
@login_required
def api_listar_reservas():
    reservas = Reserva.query.filter_by(cliente_id=current_user.id).all()
    return jsonify([
        {
            "id":            r.id,
            "cliente_id":    r.cliente_id,
            "habitacion_id": r.habitacion_id,
            "fecha_inicio":  str(r.fecha_inicio),
            "fecha_fin":     str(r.fecha_fin),
            "total":         float(r.total)
        }
        for r in reservas
    ])


@reservas_bp.route('/api/reservas', methods=['POST'])
@login_required
def api_crear_reserva():
    data = request.json

    fecha_inicio = datetime.strptime(data['fecha_inicio'], "%Y-%m-%d").date()
    fecha_fin    = datetime.strptime(data['fecha_fin'],    "%Y-%m-%d").date()

    if fecha_fin <= fecha_inicio:
        return jsonify({"error": "Fechas inválidas"}), 400

    habitacion   = Habitacion.query.get_or_404(data['habitacion_id'])
    noches       = (fecha_fin - fecha_inicio).days
    total        = noches * float(habitacion.tipo.precio_noche)

    nueva_reserva = Reserva(
        cliente_id    = current_user.id,
        habitacion_id = data['habitacion_id'],
        fecha_inicio  = fecha_inicio,
        fecha_fin     = fecha_fin,
        total         = total
    )
    db.session.add(nueva_reserva)
    db.session.commit()

    return jsonify({"message": "Reserva creada", "id": nueva_reserva.id}), 201


@reservas_bp.route('/api/reservas/<int:id>', methods=['DELETE'])
@login_required
def api_delete_reserva(id):
    reserva = Reserva.query.get_or_404(id)

    if reserva.cliente_id != current_user.id:
        return jsonify({"error": "Sin permiso"}), 403

    db.session.delete(reserva)
    db.session.commit()
    return jsonify({"message": "Reserva eliminada"})