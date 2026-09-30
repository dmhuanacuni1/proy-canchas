from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from sqlalchemy.exc import IntegrityError

from extensions import db
from services import reportes_service
from services.reportes_exporters import exportar_excel, exportar_pdf
from utils.responses import error_json
from validators.reportes_validator import validar_datos_reporte

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")


def _parsear_fechas():
    fi = request.args.get("fecha_inicio")
    ff = request.args.get("fecha_fin")
    if not fi or not ff:
        raise ValueError("Debe indicar fecha_inicio y fecha_fin (AAAA-MM-DD)")
    try:
        fi_dt = datetime.strptime(fi, "%Y-%m-%d").date()
        ff_dt = datetime.strptime(ff, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Formato de fecha inválido. Use AAAA-MM-DD")
    return fi_dt, ff_dt


# =====================================================================
# REPORTES GENERADOS (consultas + exportación PDF/Excel)
# =====================================================================
@reportes_bp.get("/datos/<tipo>")
def obtener_reporte_datos(tipo):
    if tipo not in reportes_service.REPORTES:
        return error_json("Tipo de reporte no válido. Use: reservas, ocupacion o ingresos.", codigo=400)
    try:
        fi, ff = _parsear_fechas()
        filas = reportes_service.REPORTES[tipo](fi, ff)
        return jsonify({
            "tipo": tipo,
            "fecha_inicio": fi.isoformat(),
            "fecha_fin": ff.isoformat(),
            "total_registros": len(filas),
            "filas": filas,
        }), 200
    except ValueError as e:
        return error_json(str(e), codigo=400)
    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al generar el reporte.", str(e), 500)


@reportes_bp.get("/exportar/<tipo>")
def exportar_reporte(tipo):
    if tipo not in reportes_service.REPORTES:
        return error_json("Tipo de reporte no válido. Use: reservas, ocupacion o ingresos.", codigo=400)

    formato = request.args.get("formato", "pdf").lower()
    try:
        fi, ff = _parsear_fechas()
        filas = reportes_service.REPORTES[tipo](fi, ff)

        if formato == "excel":
            buffer = exportar_excel(tipo, filas, fi.isoformat(), ff.isoformat())
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"reporte_{tipo}_{fi}_{ff}.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        buffer = exportar_pdf(tipo, filas, fi.isoformat(), ff.isoformat())
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"reporte_{tipo}_{fi}_{ff}.pdf",
            mimetype="application/pdf",
        )
    except ValueError as e:
        return error_json(str(e), codigo=400)
    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al exportar el reporte.", str(e), 500)


# =====================================================================
# CRUD DE LA TABLA reporte
# =====================================================================
@reportes_bp.post("")
def generar_reporte():
    data = request.get_json(silent=True)

    try:
        datos = validar_datos_reporte(data)
        reporte = reportes_service.generar_reporte(datos)

        return jsonify({
            "mensaje": "Reporte generado con éxito.",
            "reporte": reporte.to_dict(),
        }), 201

    except ValueError as e:
        db.session.rollback()
        return error_json("Datos inválidos.", str(e))

    except IntegrityError as e:
        db.session.rollback()
        return error_json("No se pudo generar el reporte.", str(e.orig), 409)

    except Exception as e:
        db.session.rollback()
        return error_json("Error interno al generar el reporte.", str(e), 500)


@reportes_bp.get("")
def obtener_reportes():
    try:
        reportes = reportes_service.listar_reportes()
        return jsonify([r.to_dict() for r in reportes]), 200
    except Exception as e:
        return error_json("Error interno al obtener reportes.", str(e), 500)


@reportes_bp.get("/<int:id_reporte>")
def obtener_reporte(id_reporte):
    if id_reporte <= 0:
        return error_json("El id_reporte debe ser mayor que 0.")

    try:
        reporte = reportes_service.obtener_reporte_por_id(id_reporte)
        return jsonify(reporte.to_dict()), 200
    except ValueError as e:
        return error_json(str(e), codigo=404)


@reportes_bp.delete("/<int:id_reporte>")
def eliminar_reporte(id_reporte):
    if id_reporte <= 0:
        return error_json("El id_reporte debe ser mayor que 0.")

    try:
        reportes_service.eliminar_reporte(id_reporte)
        return jsonify({"mensaje": "Reporte eliminado con éxito."}), 200

    except ValueError as e:
        db.session.rollback()
        return error_json(str(e), codigo=404)

    except Exception as e:
        db.session.rollback()
        return error_json("No se pudo eliminar el reporte.", str(e), 409)