from app.repositories.habitacion_repository import HabitacionRepository

class HabitacionService:

    @staticmethod
    def listar_habitaciones():
        return HabitacionRepository.get_all()

    @staticmethod
    def obtener_habitacion(id):
        return HabitacionRepository.get_by_id(id)

    @staticmethod
    def crear_habitacion(data):
        return HabitacionRepository.create(data)

    @staticmethod
    def actualizar_habitacion(id, data):
        return HabitacionRepository.update(id, data)

    @staticmethod
    def eliminar_habitacion(id):
        HabitacionRepository.delete(id)