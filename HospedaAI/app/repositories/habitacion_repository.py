from app.models.habitacion import Habitacion
from app.models.tipo_habitacion import TipoHabitacion
from app import db

class HabitacionRepository:

    @staticmethod
    def get_all():
        return Habitacion.query.all()

    @staticmethod
    def get_by_id(id):
        return Habitacion.query.get(id)

    @staticmethod
    def create(data):
        habitacion = Habitacion(**data)
        db.session.add(habitacion)
        db.session.commit()
        return habitacion

    @staticmethod
    def update(id, data):
        habitacion = Habitacion.query.get(id)

        for key, value in data.items():
            setattr(habitacion, key, value)

        db.session.commit()
        return habitacion

    @staticmethod
    def delete(id):
        habitacion = Habitacion.query.get(id)
        db.session.delete(habitacion)
        db.session.commit()


class TipoHabitacionRepository:

    @staticmethod
    def get_all():
        return TipoHabitacion.query.all()

    @staticmethod
    def create(data):
        tipo = TipoHabitacion(**data)
        db.session.add(tipo)
        db.session.commit()
        return tipo