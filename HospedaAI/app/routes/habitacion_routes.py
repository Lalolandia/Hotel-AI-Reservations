from flask import Blueprint, request, jsonify, render_template, redirect
from app.services.habitacion_service import HabitacionService
from app.models.tipo_habitacion import TipoHabitacion

habitacion_bp = Blueprint("habitaciones", __name__)

# LISTAR
@habitacion_bp.route("/habitaciones")
def listar():
    habitaciones = HabitacionService.listar_habitaciones()
    return render_template("habitaciones/lista.html", habitaciones=habitaciones)


# CREAR
@habitacion_bp.route("/habitaciones/crear", methods=["GET", "POST"])
def crear():

    if request.method == "POST":

        data = {
            "numero": request.form["numero"],
            "piso": request.form["piso"],
            "estado": request.form["estado"],
            "tipo_habitacion_id": request.form["tipo_habitacion_id"]
        }

        HabitacionService.crear_habitacion(data)

        return redirect("/habitaciones")

    tipos = TipoHabitacion.query.all()

    return render_template("habitaciones/crear.html", tipos=tipos)


# EDITAR
@habitacion_bp.route("/habitaciones/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    habitacion = HabitacionService.obtener_habitacion(id)

    if request.method == "POST":

        data = {
            "numero": request.form["numero"],
            "piso": request.form["piso"],
            "estado": request.form["estado"]
        }

        HabitacionService.actualizar_habitacion(id, data)

        return redirect("/habitaciones")

    return render_template("habitaciones/editar.html", habitacion=habitacion)


# ELIMINAR
@habitacion_bp.route("/habitaciones/eliminar/<int:id>")
def eliminar(id):

    HabitacionService.eliminar_habitacion(id)

    return redirect("/habitaciones")

# API GET
@habitacion_bp.route("/api/habitaciones")
def api_listar():

    habitaciones = HabitacionService.listar_habitaciones()

    return jsonify([
        {
            "id": h.id,
            "numero": h.numero,
            "piso": h.piso,
            "estado": h.estado
        }
        for h in habitaciones
    ])


# API POST
@habitacion_bp.route("/api/habitaciones", methods=["POST"])
def api_crear():

    data = request.json

    habitacion = HabitacionService.crear_habitacion(data)

    return jsonify({"id": habitacion.id})


# API PUT
@habitacion_bp.route("/api/habitaciones/<int:id>", methods=["PUT"])
def api_update(id):

    data = request.json

    habitacion = HabitacionService.actualizar_habitacion(id, data)

    return jsonify({"id": habitacion.id})


# API DELETE
@habitacion_bp.route("/api/habitaciones/<int:id>", methods=["DELETE"])
def api_delete(id):

    HabitacionService.eliminar_habitacion(id)

    return jsonify({"message": "Habitacion eliminada"})