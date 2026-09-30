from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from services import canchas_service
from validators.cancha_validator import validar_datos_cancha
from utils.responses import error_json

canchas_bp = Blueprint("canchas", __name__, url_prefix="/api/canchas")


@canchas_bp.post("")
def crear_cancha():
    data = request.get_json(silent=True)

    try:
        datos_texto = validar_datos_cancha(data)
        cancha = canchas_service.crear_cancha(datos_texto, data)

        return jsonify({
            "mensaje": "Cancha registrada con éxito.",
            "cancha": cancha.to_dict(),
        }), 201

    except ValueError as e:
        db.session.rollback()
        return error_json("Datos inválidos.", str(e))

    except IntegrityError as e:
        db.session.rollback()
        return error_json("No se pudo registrar la cancha.", str(e.orig), 409)

    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al registrar la cancha.", str(e), 500)


@canchas_bp.get("")
def obtener_canchas():
    try:
        estado = request.args.get("estado")
        canchas = canchas_service.listar_canchas(estado)
        return jsonify([c.to_dict() for c in canchas]), 200
    except ValueError as e:
        return error_json(str(e))
    except Exception as e:
        return error_json("Error interno al obtener canchas.", str(e), 500)


@canchas_bp.get("/<int:id_cancha>")
def obtener_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json("El id_cancha debe ser mayor que 0.")

    try:
        cancha = canchas_service.obtener_cancha_por_id(id_cancha)
        return jsonify(cancha.to_dict()), 200
    except ValueError as e:
        return error_json(str(e), codigo=404)


@canchas_bp.patch("/<int:id_cancha>")
def modificar_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json("El id_cancha debe ser mayor que 0.")

    data = request.get_json(silent=True)

    try:
        datos_texto = validar_datos_cancha(data, parcial=True)
        cancha = canchas_service.modificar_cancha(id_cancha, datos_texto, data)

        return jsonify({
            "mensaje": "Cancha modificada con éxito.",
            "cancha": cancha.to_dict(),
        }), 200

    except ValueError as e:
        db.session.rollback()
        mensaje = str(e)
        codigo = 404 if "no existe" in mensaje.lower() else 400
        return error_json(mensaje, codigo=codigo)

    except IntegrityError as e:
        db.session.rollback()
        return error_json("No se pudo modificar la cancha.", str(e.orig), 409)

    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al modificar la cancha.", str(e), 500)


@canchas_bp.delete("/<int:id_cancha>")
def eliminar_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json("El id_cancha debe ser mayor que 0.")

    try:
        canchas_service.eliminar_cancha(id_cancha)
        return jsonify({"mensaje": "Cancha retirada con éxito."}), 200

    except ValueError as e:
        return error_json(str(e), codigo=404)

    except IntegrityError:
        db.session.rollback()
        return error_json(
            "No se puede retirar físicamente la cancha porque tiene reservas o "
            "eventos asociados. Use PATCH /api/canchas/<id>/estado para "
            "colocarla como fuera_servicio.",
            codigo=409,
        )

    except Exception as e:
        db.session.rollback()
        return error_json("No se pudo retirar la cancha.", str(e), 409)


@canchas_bp.patch("/<int:id_cancha>/estado")
def cambiar_estado_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json("El id_cancha debe ser mayor que 0.")

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error_json("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    try:
        cancha = canchas_service.cambiar_estado_cancha(id_cancha, data.get("estado"))

        return jsonify({
            "mensaje": f"Estado actualizado a {cancha.estado}.",
            "cancha": cancha.to_dict(),
        }), 200

    except ValueError as e:
        db.session.rollback()
        mensaje = str(e)
        codigo = 404 if "no existe" in mensaje.lower() else 400
        return error_json(mensaje, codigo=codigo)

    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al cambiar el estado.", str(e), 500)
