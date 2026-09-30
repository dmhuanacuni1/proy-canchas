from flask import jsonify


def error_json(mensaje, detalle=None, codigo=400):
    respuesta = {"error": mensaje}

    if detalle:
        respuesta["detalle"] = detalle

    return jsonify(respuesta), codigo
