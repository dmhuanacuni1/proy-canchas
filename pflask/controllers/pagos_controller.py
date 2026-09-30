from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from services import pagos_service
from validators.pagos_validator import validar_datos_pago, validar_estado_pago
from utils.responses import error_json

pagos_bp = Blueprint("pagos", __name__, url_prefix="/api/pagos")


@pagos_bp.post("")
def crear_pago():
    data = request.get_json(silent=True)

    try:
        datos = validar_datos_pago(data)
        pago = pagos_service.crear_pago(datos)

        return jsonify({
            "mensaje": "Pago registrado con éxito.",
            "pago": pago.to_dict(),
        }), 201

    except ValueError as e:
        db.session.rollback()
        return error_json("Datos inválidos.", str(e))

    except IntegrityError as e:
        db.session.rollback()
        return error_json("No se pudo registrar el pago.", str(e.orig), 409)

    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al registrar el pago.", str(e), 500)


@pagos_bp.get("")
def obtener_pagos():
    try:
        estado = request.args.get("estado")
        con_detalle = request.args.get("detalle", "0") in ("1", "true", "True")
        id_cliente = request.args.get("id_cliente")
        if id_cliente:
            id_cliente = int(id_cliente)
        pagos = pagos_service.listar_pagos(estado, con_detalle=con_detalle, id_cliente=id_cliente)
        return jsonify([p.to_dict() if isinstance(p, object) and hasattr(p, "to_dict") else p for p in pagos]), 200
    except ValueError as e:
        return error_json(str(e))
    except Exception as e:
        return error_json("Error interno al obtener pagos.", str(e), 500)


@pagos_bp.get("/reservas-para-pago")
def obtener_reservas_para_pago():
    try:
        reservas = pagos_service.listar_reservas_para_pago()
        return jsonify(reservas), 200
    except Exception as e:
        return error_json("Error interno al obtener reservas.", str(e), 500)


@pagos_bp.get("/<int:id_pago>")
def obtener_pago(id_pago):
    if id_pago <= 0:
        return error_json("El id_pago debe ser mayor que 0.")

    try:
        pago = pagos_service.obtener_pago_por_id(id_pago)
        return jsonify(pagos_service._pago_detalle(pago)), 200
    except ValueError as e:
        return error_json(str(e), codigo=404)


@pagos_bp.patch("/<int:id_pago>/estado")
def cambiar_estado_pago(id_pago):
    if id_pago <= 0:
        return error_json("El id_pago debe ser mayor que 0.")

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error_json("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    try:
        pago = pagos_service.modificar_estado_pago(
            id_pago, validar_estado_pago(data.get("estado_pago"))
        )

        return jsonify({
            "mensaje": f"Estado actualizado a {pago.estado_pago}.",
            "pago": pago.to_dict(),
        }), 200

    except ValueError as e:
        db.session.rollback()
        mensaje = str(e)
        codigo = 404 if "no existe" in mensaje.lower() else 400
        return error_json(mensaje, codigo=codigo)

    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al cambiar el estado del pago.", str(e), 500)


@pagos_bp.delete("/<int:id_pago>")
def eliminar_pago(id_pago):
    if id_pago <= 0:
        return error_json("El id_pago debe ser mayor que 0.")

    try:
        pagos_service.eliminar_pago(id_pago)
        return jsonify({"mensaje": "Pago eliminado con éxito."}), 200

    except ValueError as e:
        db.session.rollback()
        return error_json(str(e), codigo=404)

    except Exception as e:
        db.session.rollback()
        return error_json("No se pudo eliminar el pago.", str(e), 409)