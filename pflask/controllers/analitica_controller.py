from flask import Blueprint, jsonify

from services import analitica_service
from utils.responses import error_json

analitica_bp = Blueprint("analitica", __name__, url_prefix="/api/analitica")


@analitica_bp.get("")
def resumen():
    try:
        return jsonify(analitica_service.resumen_analitico()), 200
    except Exception as e:
        return error_json("Error interno al consultar la analítica.", str(e), 500)