from datetime import datetime, date
from sqlalchemy import text
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
    def _verificar_disponibilidad(id_cancha, fecha, hora_inicio, hora_fin, id_evento_excluir=None):
        """
        Verifica que la cancha se encuentre operativa y libre durante todo el intervalo solicitado.
        - Comprueba que la cancha no esté 'fuera_servicio' ni en 'mantenimiento'.
        - Comprueba solapamientos con otros eventos existentes en la misma cancha y fecha (excluyendo el actual si es edición).
        - Consulta reservas activas (solo lectura) en la misma cancha y fecha.
        """
        # -1. Comprobar que no sea fecha u hora pasada
        if isinstance(hora_inicio, str):
            hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        if isinstance(hora_fin, str):
            hora_fin = datetime.strptime(hora_fin, "%H:%M").time()

        ahora = datetime.now()
        if fecha < ahora.date():
            raise ValueError("No se pueden programar eventos en una fecha anterior a la actual.")
        if fecha == ahora.date() and hora_inicio <= ahora.time():
            h_actual = ahora.strftime("%H:%M")
            raise ValueError(f"No se pueden programar eventos en una hora que ya ha transcurrido (hora actual: {h_actual}).")

        # 0. Comprobar estado operativo de la cancha
        cancha_data = db.session.execute(
            text("SELECT nombre_cancha, estado FROM cancha WHERE id_cancha = :cancha"),
            {"cancha": id_cancha}
        ).fetchone()

        if not cancha_data:
            raise ValueError(f"La cancha seleccionada (ID {id_cancha}) no existe.")

        nombre_cancha, estado_cancha = cancha_data[0], cancha_data[1]
        if estado_cancha == "fuera_servicio":
            raise ValueError(f"La cancha '{nombre_cancha}' se encuentra fuera de servicio y no puede recibir eventos.")
        if estado_cancha == "mantenimiento":
            raise ValueError(f"La cancha '{nombre_cancha}' se encuentra en mantenimiento y no puede recibir eventos.")

        # 1. Comprobar choque con otros eventos
        query_eventos = Evento.query.filter(
            Evento.id_cancha == id_cancha,
            Evento.fecha_evento == fecha,
            Evento.hora_inicio < hora_fin,
            Evento.hora_fin > hora_inicio
        )
        if id_evento_excluir:
            query_eventos = query_eventos.filter(Evento.id_evento != id_evento_excluir)

        evento_solapado = query_eventos.first()
        if evento_solapado:
            h_ini = evento_solapado.hora_inicio.strftime("%H:%M")
            h_fin = evento_solapado.hora_fin.strftime("%H:%M")
            raise ValueError(
                f"Conflicto de ocupación: La cancha ya tiene asignado el evento '{evento_solapado.nombre_evento}' ({h_ini} - {h_fin})."
            )

        # 2. Consulta de solo lectura sobre la tabla reserva
        reserva_choque = db.session.execute(
            text("""
                SELECT id_reserva, hora_inicio, hora_fin 
                FROM reserva 
                WHERE id_cancha = :cancha 
                  AND fecha_reserva = :fecha 
                  AND LOWER(estado_reserva) NOT IN ('cancelada', 'expirada')
                  AND (hora_inicio < :fin AND hora_fin > :inicio)
                LIMIT 1
            """),
            {
                "cancha": id_cancha,
                "fecha": fecha,
                "inicio": hora_inicio,
                "fin": hora_fin
            }
        ).fetchone()

        if reserva_choque:
            r_ini = str(reserva_choque[1])[:5]
            r_fin = str(reserva_choque[2])[:5]
            raise ValueError(
                f"Conflicto de ocupación: La cancha cuenta con una reserva activa en ese horario ({r_ini} - {r_fin})."
            )

    @staticmethod
    def create_evento(data):
        fecha = datetime.strptime(data["fecha_evento"], "%Y-%m-%d").date()
        if fecha < date.today():
            raise ValueError("La fecha del evento no puede ser anterior a la fecha actual.")

        inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        fin = datetime.strptime(data["hora_fin"], "%H:%M").time()

        if fin <= inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

        id_cancha = int(data["id_cancha"])

        # Verificar disponibilidad de la cancha contra eventos y reservas
        EventosService._verificar_disponibilidad(id_cancha, fecha, inicio, fin)

        nuevo_evento = Evento(
            nombre_evento=data["nombre_evento"],
            tipo_evento=data.get("tipo_evento"),
            fecha_evento=fecha,
            hora_inicio=inicio,
            hora_fin=fin,
            cupo_maximo=data.get("cupo_maximo"),
            organizador=data.get("organizador"),
            descripcion=data.get("descripcion"),
            id_cancha=id_cancha
        )

        db.session.add(nuevo_evento)
        db.session.commit()
        return nuevo_evento

    @staticmethod
    def update_evento(id_evento, data):
        evento = Evento.query.get(id_evento)
        if not evento:
            return None

        nueva_fecha = evento.fecha_evento
        nuevo_inicio = evento.hora_inicio
        nuevo_fin = evento.hora_fin
        nueva_cancha = evento.id_cancha
        tiempo_o_cancha_cambio = False

        if "fecha_evento" in data and data["fecha_evento"]:
            f = datetime.strptime(data["fecha_evento"], "%Y-%m-%d").date()
            if f < date.today():
                raise ValueError("La fecha del evento no puede ser anterior a la fecha actual.")
            if f != evento.fecha_evento:
                nueva_fecha = f
                tiempo_o_cancha_cambio = True

        if "hora_inicio" in data and data["hora_inicio"]:
            hi = datetime.strptime(data["hora_inicio"], "%H:%M").time()
            if hi != evento.hora_inicio:
                nuevo_inicio = hi
                tiempo_o_cancha_cambio = True

        if "hora_fin" in data and data["hora_fin"]:
            hf = datetime.strptime(data["hora_fin"], "%H:%M").time()
            if hf != evento.hora_fin:
                nuevo_fin = hf
                tiempo_o_cancha_cambio = True

        if "id_cancha" in data and data["id_cancha"]:
            c = int(data["id_cancha"])
            if c != evento.id_cancha:
                nueva_cancha = c
                tiempo_o_cancha_cambio = True

        if nuevo_fin <= nuevo_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

        # Revalidar disponibilidad si cambiaron cancha, fecha u horario
        if tiempo_o_cancha_cambio:
            EventosService._verificar_disponibilidad(
                nueva_cancha, nueva_fecha, nuevo_inicio, nuevo_fin, id_evento_excluir=id_evento
            )

        # Aplicar actualizaciones
        if "nombre_evento" in data:
            evento.nombre_evento = data["nombre_evento"]
        if "tipo_evento" in data:
            evento.tipo_evento = data["tipo_evento"]
        evento.fecha_evento = nueva_fecha
        evento.hora_inicio = nuevo_inicio
        evento.hora_fin = nuevo_fin
        evento.id_cancha = nueva_cancha
        if "cupo_maximo" in data:
            evento.cupo_maximo = data["cupo_maximo"]
        if "organizador" in data:
            evento.organizador = data["organizador"]
        if "descripcion" in data:
            evento.descripcion = data["descripcion"]

        db.session.commit()
        return evento

    @staticmethod
    def delete_evento(id_evento):
        """
        Elimina físicamente un evento de la base de datos.
        Exclusivo para el Administrador.
        """
        evento = Evento.query.get(id_evento)
        if not evento:
            return False
        db.session.delete(evento)
        db.session.commit()
        return True
