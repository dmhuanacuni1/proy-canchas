from datetime import datetime, date
from extensions import db
from models.evento import Evento

class EventosService:
    @staticmethod
    def get_all_eventos():
        return Evento.query.order_by(Evento.fecha_evento.asc(), Evento.hora_inicio.asc()).all()

    @staticmethod
    def get_evento_by_id(id_evento):
        return Evento.query.get(id_evento)

    @staticmethod
    def create_evento(data):
        fecha = datetime.strptime(data["fecha_evento"], "%Y-%m-%d").date()
        if fecha < date.today():
            raise ValueError("La fecha del evento no puede ser anterior a la fecha actual.")

        inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        fin = datetime.strptime(data["hora_fin"], "%H:%M").time()

        if fin <= inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

        nuevo_evento = Evento(
            nombre_evento=data["nombre_evento"],
            tipo_evento=data.get("tipo_evento"),
            fecha_evento=fecha,
            hora_inicio=inicio,
            hora_fin=fin,
            cupo_maximo=data.get("cupo_maximo"),
            organizador=data.get("organizador"),
            descripcion=data.get("descripcion"),
            id_cancha=data["id_cancha"]
        )

        db.session.add(nuevo_evento)
        db.session.commit()
        return nuevo_evento

    @staticmethod
    def update_evento(id_evento, data):
        evento = Evento.query.get(id_evento)
        if not evento:
            return None

        if "nombre_evento" in data:
            evento.nombre_evento = data["nombre_evento"]
        if "tipo_evento" in data:
            evento.tipo_evento = data["tipo_evento"]
        if "fecha_evento" in data and data["fecha_evento"]:
            nueva_fecha = datetime.strptime(data["fecha_evento"], "%Y-%m-%d").date()
            if nueva_fecha < date.today():
                raise ValueError("La fecha del evento no puede ser anterior a la fecha actual.")
            evento.fecha_evento = nueva_fecha
        if "hora_inicio" in data:
            evento.hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        if "hora_fin" in data:
            evento.hora_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()
        if "cupo_maximo" in data:
            evento.cupo_maximo = data["cupo_maximo"]
        if "organizador" in data:
            evento.organizador = data["organizador"]
        if "descripcion" in data:
            evento.descripcion = data["descripcion"]
        if "id_cancha" in data:
            evento.id_cancha = data["id_cancha"]

        if evento.hora_fin <= evento.hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

        db.session.commit()
        return evento

    @staticmethod
    def delete_evento(id_evento):
        evento = Evento.query.get(id_evento)
        if not evento:
            return False
        db.session.delete(evento)
        db.session.commit()
        return True
