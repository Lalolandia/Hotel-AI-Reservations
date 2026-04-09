from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

from app.models.tipo_habitacion import TipoHabitacion
from app.services.habitacion_service import HabitacionService

habitacion_bp = Blueprint("habitaciones", __name__)


@habitacion_bp.route("/habitaciones")
def listar():
    habitaciones = HabitacionService.listar_habitaciones()
    return render_template("habitaciones/lista.html", habitaciones=habitaciones)


@habitacion_bp.route("/habitaciones/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        data = {
            "numero": request.form["numero"],
            "estado": request.form["estado"],
            "tipo_id": request.form["tipo_id"],
        }

        HabitacionService.crear_habitacion(data)
        flash("Habitacion creada correctamente.", "success")
        return redirect(url_for("habitaciones.listar"))

    tipos = TipoHabitacion.query.all()
    return render_template("habitaciones/crear.html", tipos=tipos)


@habitacion_bp.route("/habitaciones/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    habitacion = HabitacionService.obtener_habitacion(id)
    tipos = TipoHabitacion.query.all()

    if not habitacion:
        flash("La habitacion que intentas editar no existe.", "warning")
        return redirect(url_for("habitaciones.listar"))

    if request.method == "POST":
        data = {
            "numero": request.form["numero"],
            "estado": request.form["estado"],
            "tipo_id": request.form["tipo_id"],
        }

        HabitacionService.actualizar_habitacion(id, data)
        flash("Habitacion actualizada correctamente.", "success")
        return redirect(url_for("habitaciones.listar"))

    return render_template("habitaciones/editar.html", habitacion=habitacion, tipos=tipos)


@habitacion_bp.route("/habitaciones/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    HabitacionService.eliminar_habitacion(id)
    flash("Habitacion eliminada correctamente.", "success")
    return redirect(url_for("habitaciones.listar"))


@habitacion_bp.route("/api/habitaciones")
def api_listar():
    habitaciones = HabitacionService.listar_habitaciones()

    return jsonify([
        {
            "id": h.id,
            "numero": h.numero,
            "estado": h.estado,
            "tipo_id": h.tipo_id,
        }
        for h in habitaciones
    ])


@habitacion_bp.route("/api/habitaciones", methods=["POST"])
def api_crear():
    data = request.json
    habitacion = HabitacionService.crear_habitacion(data)
    return jsonify({"id": habitacion.id})


@habitacion_bp.route("/api/habitaciones/<int:id>", methods=["PUT"])
def api_update(id):
    data = request.json
    habitacion = HabitacionService.actualizar_habitacion(id, data)
    return jsonify({"id": habitacion.id})


@habitacion_bp.route("/api/habitaciones/<int:id>", methods=["DELETE"])
def api_delete(id):
    HabitacionService.eliminar_habitacion(id)
    return jsonify({"message": "Habitacion eliminada"})
