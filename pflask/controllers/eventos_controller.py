from flask import Blueprint, jsonify, request
from services.eventos_service import EventosService
from validators.evento_validator import EventoValidator

# Integración con el sistema de autenticación y roles
try:
    from services.auth_service import require_auth
except ImportError:
    # Fallback transparente para desarrollo aislado si auth no está en la misma ruta
    def require_auth(roles=None):
        def decorator(fn):
            return fn
        return decorator

eventos_bp = Blueprint("eventos", __name__, url_prefix="/api/eventos")


@eventos_bp.route("", methods=["GET"])
def get_eventos():
    try:
        eventos = EventosService.get_all_eventos()
        return jsonify([e.to_dict() for e in eventos]), 200
    except Exception as ex:
        return jsonify({"error": "Error al consultar los eventos", "detalle": str(ex)}), 500

@eventos_bp.route("/<int:id_evento>", methods=["GET"])
def get_evento(id_evento):
    try:
        evento = EventosService.get_evento_by_id(id_evento)
        if not evento:
            return jsonify({"error": "Evento no encontrado"}), 404
        return jsonify(evento.to_dict()), 200
    except Exception as ex:
        return jsonify({"error": "Error al consultar el evento", "detalle": str(ex)}), 500

@eventos_bp.route("", methods=["POST"])
@require_auth(roles=["administrador", "empleado"])
def create_evento():
    try:
        data = request.get_json()
        valido, errores = EventoValidator.validate_create_payload(data)
        if not valido:
            return jsonify({"error": "Datos inválidos", "detalles": errores}), 400

        nuevo = EventosService.create_evento(data)
        return jsonify(nuevo.to_dict()), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"error": "Error interno al crear el evento", "detalle": str(ex)}), 500

@eventos_bp.route("/<int:id_evento>", methods=["PUT"])
@require_auth(roles=["administrador"])
def update_evento(id_evento):
    try:
        data = request.get_json()
        valido, errores = EventoValidator.validate_update_payload(data)
        if not valido:
            return jsonify({"error": "Datos inválidos", "detalles": errores}), 400

        evento_actualizado = EventosService.update_evento(id_evento, data)
        if not evento_actualizado:
            return jsonify({"error": "Evento no encontrado"}), 404
        return jsonify(evento_actualizado.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"error": "Error al actualizar el evento", "detalle": str(ex)}), 500

@eventos_bp.route("/<int:id_evento>", methods=["DELETE"])
@require_auth(roles=["administrador"])
def delete_evento(id_evento):
    try:
        eliminado = EventosService.delete_evento(id_evento)
        if not eliminado:
            return jsonify({"error": "Evento no encontrado"}), 404
        return jsonify({"mensaje": "Evento eliminado exitosamente"}), 200
    except Exception as ex:
        return jsonify({"error": "Error al eliminar el evento", "detalle": str(ex)}), 500
