from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.habitacion import Habitacion
from app.models.tipo_habitacion import TipoHabitacion
from app.models.paquete import Paquete
from app.models.reserva import Reserva
from app.models.cliente import Cliente

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Decorador: solo admins ──────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.es_admin:
            flash("No tienes permiso para acceder al panel de administración.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated


# ════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════

@admin_bp.route('/')
@admin_required
def dashboard():
    total_clientes = Cliente.query.count()
    total_habitaciones = Habitacion.query.count()
    total_reservas = Reserva.query.count()
    total_paquetes = Paquete.query.count()

    disponibles = Habitacion.query.filter_by(estado='disponible').count()
    ocupadas = Habitacion.query.filter_by(estado='ocupada').count()

    ingresos = db.session.query(db.func.sum(Reserva.total)).scalar() or 0

    reservas_recientes = Reserva.query.order_by(Reserva.id.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_clientes=total_clientes,
                           total_habitaciones=total_habitaciones,
                           total_reservas=total_reservas,
                           total_paquetes=total_paquetes,
                           disponibles=disponibles,
                           ocupadas=ocupadas,
                           ingresos=ingresos,
                           reservas_recientes=reservas_recientes,
                           )


# ════════════════════════════════════════
#  TIPOS DE HABITACIÓN
# ════════════════════════════════════════

@admin_bp.route('/tipos')
@admin_required
def listar_tipos():
    tipos = TipoHabitacion.query.all()
    return render_template('admin/tipos.html', tipos=tipos)


@admin_bp.route('/tipos/crear', methods=['GET', 'POST'])
@admin_required
def crear_tipo():
    if request.method == 'POST':
        tipo = TipoHabitacion(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion', ''),
            precio_noche=float(request.form['precio_noche']),
            capacidad=int(request.form['capacidad']),
            imagen=request.form.get('imagen', '') or None,
        )
        db.session.add(tipo)
        db.session.commit()
        flash("Tipo de habitación creado.", "success")
        return redirect(url_for('admin.listar_tipos'))
    return render_template('admin/tipo_form.html', tipo=None, accion='Crear')


@admin_bp.route('/tipos/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_tipo(id):
    tipo = TipoHabitacion.query.get_or_404(id)
    if request.method == 'POST':
        tipo.nombre = request.form['nombre']
        tipo.descripcion = request.form.get('descripcion', '')
        tipo.precio_noche = float(request.form['precio_noche'])
        tipo.capacidad = int(request.form['capacidad'])
        tipo.imagen = request.form.get('imagen', '') or None
        db.session.commit()
        flash("Tipo de habitación actualizado.", "success")
        return redirect(url_for('admin.listar_tipos'))
    return render_template('admin/tipo_form.html', tipo=tipo, accion='Editar')


@admin_bp.route('/tipos/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_tipo(id):
    tipo = TipoHabitacion.query.get_or_404(id)
    if tipo.habitaciones:
        flash("No se puede eliminar: tiene habitaciones asociadas.", "warning")
        return redirect(url_for('admin.listar_tipos'))
    db.session.delete(tipo)
    db.session.commit()
    flash("Tipo eliminado.", "success")
    return redirect(url_for('admin.listar_tipos'))


# ════════════════════════════════════════
#  HABITACIONES
# ════════════════════════════════════════

@admin_bp.route('/habitaciones')
@admin_required
def listar_habitaciones():
    habitaciones = Habitacion.query.all()
    return render_template('admin/habitaciones.html', habitaciones=habitaciones)


@admin_bp.route('/habitaciones/crear', methods=['GET', 'POST'])
@admin_required
def crear_habitacion():
    tipos = TipoHabitacion.query.all()
    if request.method == 'POST':
        hab = Habitacion(
            numero=request.form['numero'],
            piso=int(request.form['piso']) if request.form.get('piso') else None,
            estado=request.form['estado'],
            capacidad=int(request.form['capacidad']) if request.form.get('capacidad') else None,
            tipo_id=int(request.form['tipo_id']),
        )
        db.session.add(hab)
        db.session.commit()
        flash("Habitación creada.", "success")
        return redirect(url_for('admin.listar_habitaciones'))
    return render_template('admin/habitacion_form.html', habitacion=None, tipos=tipos, accion='Crear')


@admin_bp.route('/habitaciones/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_habitacion(id):
    hab = Habitacion.query.get_or_404(id)
    tipos = TipoHabitacion.query.all()
    if request.method == 'POST':
        hab.numero = request.form['numero']
        hab.piso = int(request.form['piso']) if request.form.get('piso') else None
        hab.estado = request.form['estado']
        hab.capacidad = int(request.form['capacidad']) if request.form.get('capacidad') else None
        hab.tipo_id = int(request.form['tipo_id'])
        db.session.commit()
        flash("Habitación actualizada.", "success")
        return redirect(url_for('admin.listar_habitaciones'))
    return render_template('admin/habitacion_form.html', habitacion=hab, tipos=tipos, accion='Editar')


@admin_bp.route('/habitaciones/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_habitacion(id):
    hab = Habitacion.query.get_or_404(id)
    if hab.reservas:
        flash("No se puede eliminar: tiene reservas activas.", "warning")
        return redirect(url_for('admin.listar_habitaciones'))
    db.session.delete(hab)
    db.session.commit()
    flash("Habitación eliminada.", "success")
    return redirect(url_for('admin.listar_habitaciones'))


# ════════════════════════════════════════
#  PAQUETES
# ════════════════════════════════════════

@admin_bp.route('/paquetes')
@admin_required
def listar_paquetes():
    paquetes = Paquete.query.all()
    return render_template('admin/paquetes.html', paquetes=paquetes)


@admin_bp.route('/paquetes/crear', methods=['GET', 'POST'])
@admin_required
def crear_paquete():
    if request.method == 'POST':
        paquete = Paquete(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion', ''),
            precio_total=float(request.form['precio_total']),
        )
        db.session.add(paquete)
        db.session.commit()
        flash("Paquete creado.", "success")
        return redirect(url_for('admin.listar_paquetes'))
    return render_template('admin/paquete_form.html', paquete=None, accion='Crear')


@admin_bp.route('/paquetes/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_paquete(id):
    paquete = Paquete.query.get_or_404(id)
    if request.method == 'POST':
        paquete.nombre = request.form['nombre']
        paquete.descripcion = request.form.get('descripcion', '')
        paquete.precio_total = float(request.form['precio_total'])
        db.session.commit()
        flash("Paquete actualizado.", "success")
        return redirect(url_for('admin.listar_paquetes'))
    return render_template('admin/paquete_form.html', paquete=paquete, accion='Editar')


@admin_bp.route('/paquetes/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_paquete(id):
    paquete = Paquete.query.get_or_404(id)
    db.session.delete(paquete)
    db.session.commit()
    flash("Paquete eliminado.", "success")
    return redirect(url_for('admin.listar_paquetes'))


# ════════════════════════════════════════
#  RESERVAS
# ════════════════════════════════════════

@admin_bp.route('/reservas')
@admin_required
def listar_reservas():
    reservas = Reserva.query.order_by(Reserva.id.desc()).all()
    return render_template('admin/reservas.html', reservas=reservas)


@admin_bp.route('/reservas/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    flash("Reserva eliminada.", "success")
    return redirect(url_for('admin.listar_reservas'))


# ════════════════════════════════════════
#  CLIENTES
# ════════════════════════════════════════

@admin_bp.route('/clientes')
@admin_required
def listar_clientes():
    clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).all()
    return render_template('admin/clientes.html', clientes=clientes)


@admin_bp.route('/clientes/toggle-admin/<int:id>', methods=['POST'])
@admin_required
def toggle_admin(id):
    cliente = Cliente.query.get_or_404(id)
    if cliente.id == current_user.id:
        flash("No puedes modificar tu propio rol.", "warning")
        return redirect(url_for('admin.listar_clientes'))
    cliente.es_admin = not cliente.es_admin
    db.session.commit()
    flash(f"{'Admin activado' if cliente.es_admin else 'Admin desactivado'} para {cliente.nombre}.", "success")
    return redirect(url_for('admin.listar_clientes'))
