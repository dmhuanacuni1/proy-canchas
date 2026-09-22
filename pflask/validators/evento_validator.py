from datetime import datetime, date

class EventoValidator:
    @staticmethod
    def validate_create_payload(data):
        errors = []
        if not data:
            return False, ["No se proporcionaron datos JSON."]

        required_fields = ["nombre_evento", "fecha_evento", "hora_inicio", "hora_fin", "id_cancha"]
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                errors.append(f"El campo '{field}' es obligatorio.")

        if errors:
            return False, errors

        # Validar formato de fecha (YYYY-MM-DD) y que no sea anterior a hoy
        try:
            fecha = datetime.strptime(data["fecha_evento"], "%Y-%m-%d").date()
            if fecha < date.today():
                errors.append("La fecha del evento no puede ser anterior a la fecha actual.")
        except ValueError:
            errors.append("El formato de 'fecha_evento' debe ser YYYY-MM-DD.")

        # Validar horas (HH:MM)
        try:
            h_inicio = datetime.strptime(data["hora_inicio"], "%H:%M")
            h_fin = datetime.strptime(data["hora_fin"], "%H:%M")
            if h_fin <= h_inicio:
                errors.append("La hora de fin debe ser estrictamente posterior a la hora de inicio.")
        except ValueError:
            errors.append("Las horas deben tener formato militar HH:MM (ej. 14:30).")

        # Validar cupo
        if "cupo_maximo" in data and data["cupo_maximo"] is not None:
            try:
                cupo = int(data["cupo_maximo"])
                if cupo <= 0:
                    errors.append("El cupo máximo debe ser un entero positivo.")
            except (ValueError, TypeError):
                errors.append("El cupo máximo debe ser un número entero.")

        # Validar id_cancha
        try:
            int(data["id_cancha"])
        except (ValueError, TypeError):
            errors.append("El identificador 'id_cancha' debe ser un número entero.")

        if errors:
            return False, errors
        return True, []

    @staticmethod
    def validate_update_payload(data):
        errors = []
        if not data:
            return False, ["No se proporcionaron datos JSON."]

        if "fecha_evento" in data and data["fecha_evento"]:
            try:
                fecha = datetime.strptime(data["fecha_evento"], "%Y-%m-%d").date()
                if fecha < date.today():
                    errors.append("La fecha del evento no puede ser anterior a la fecha actual.")
            except ValueError:
                errors.append("El formato de 'fecha_evento' debe ser YYYY-MM-DD.")

        if "hora_inicio" in data and "hora_fin" in data:
            try:
                h_inicio = datetime.strptime(data["hora_inicio"], "%H:%M")
                h_fin = datetime.strptime(data["hora_fin"], "%H:%M")
                if h_fin <= h_inicio:
                    errors.append("La hora de fin debe ser estrictamente posterior a la hora de inicio.")
            except ValueError:
                errors.append("Las horas deben tener formato militar HH:MM (ej. 14:30).")

        if "cupo_maximo" in data and data["cupo_maximo"] is not None:
            try:
                cupo = int(data["cupo_maximo"])
                if cupo <= 0:
                    errors.append("El cupo máximo debe ser un entero positivo.")
            except (ValueError, TypeError):
                errors.append("El cupo máximo debe ser un número entero.")

        if "id_cancha" in data and data["id_cancha"] is not None:
            try:
                int(data["id_cancha"])
            except (ValueError, TypeError):
                errors.append("El identificador 'id_cancha' debe ser un número entero.")

        if errors:
            return False, errors
        return True, []
