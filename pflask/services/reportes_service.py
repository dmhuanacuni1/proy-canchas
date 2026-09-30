from sqlalchemy import text

from extensions import db
from models.reporte import Reporte
from models.administrador import Administrador


def _validar_rango(fecha_inicio, fecha_fin):
    if not fecha_inicio or not fecha_fin:
        raise ValueError("Debe indicar fecha_inicio y fecha_fin (AAAA-MM-DD).")
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha de inicio no puede ser mayor que la fecha fin.")


# =====================================================================
# CRUD de la tabla reporte (metadatos)
# =====================================================================
def listar_reportes():
    return Reporte.query.order_by(Reporte.fecha_generado.desc()).all()


def obtener_reporte_por_id(id_reporte):
    reporte = db.session.get(Reporte, id_reporte)
    if not reporte:
        raise ValueError("El reporte no existe.")
    return reporte


def generar_reporte(datos):
    if "id_administrador" in datos:
        administrador = db.session.get(Administrador, datos["id_administrador"])
        if not administrador:
            raise ValueError("El administrador indicado no existe.")

    nuevo = Reporte(
        tipo=datos["tipo"],
        fecha_generado=datos["fecha_generado"],
        descripcion=datos.get("descripcion"),
        id_administrador=datos.get("id_administrador") if datos.get("id_administrador") else None,
    )
    db.session.add(nuevo)
    db.session.commit()
    return nuevo


def eliminar_reporte(id_reporte):
    reporte = obtener_reporte_por_id(id_reporte)
    db.session.delete(reporte)
    db.session.commit()
    return True


# =====================================================================
# REPORTE GENERADO: RESERVAS POR CANCHA
# =====================================================================
def reporte_reservas(fecha_inicio, fecha_fin):
    _validar_rango(fecha_inicio, fecha_fin)
    sql = text("""
        SELECT
            c.id_cancha,
            c.nombre_cancha,
            c.tipo_deporte,
            COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva <> 'cancelada') AS total,
            COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva = 'confirmada') AS confirmadas,
            COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva = 'completada') AS completadas,
            COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva = 'pendiente')  AS pendientes,
            COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva = 'cancelada')  AS canceladas
        FROM cancha c
        LEFT JOIN reserva r
               ON r.id_cancha = c.id_cancha
              AND r.fecha_reserva BETWEEN :fi AND :ff
        GROUP BY c.id_cancha, c.nombre_cancha, c.tipo_deporte
        ORDER BY total DESC, c.nombre_cancha ASC
    """)
    filas = db.session.execute(sql, {"fi": fecha_inicio, "ff": fecha_fin}).mappings().all()
    return [dict(f) for f in filas]


# =====================================================================
# REPORTE GENERADO: OCUPACIÓN POR CANCHA (jornada 06:00 - 23:00 = 17 h/día)
# =====================================================================
def reporte_ocupacion(fecha_inicio, fecha_fin):
    _validar_rango(fecha_inicio, fecha_fin)
    dias = (fecha_fin - fecha_inicio).days + 1 if fecha_fin >= fecha_inicio else 0
    horas_disponibles = dias * 17 if dias > 0 else 0

    sql = text("""
        SELECT
            c.id_cancha,
            c.nombre_cancha,
            c.tipo_deporte,
            COALESCE(SUM(
                EXTRACT(EPOCH FROM (r.hora_fin - r.hora_inicio)) / 3600.0
            ) FILTER (WHERE r.estado_reserva NOT IN ('cancelada')), 0) AS horas_reservadas
        FROM cancha c
        LEFT JOIN reserva r
               ON r.id_cancha = c.id_cancha
              AND r.fecha_reserva BETWEEN :fi AND :ff
        GROUP BY c.id_cancha, c.nombre_cancha, c.tipo_deporte
        ORDER BY horas_reservadas DESC, c.nombre_cancha ASC
    """)
    filas = db.session.execute(sql, {"fi": fecha_inicio, "ff": fecha_fin}).mappings().all()

    resultado = []
    for f in filas:
        horas = float(f["horas_reservadas"] or 0)
        porcentaje = round((horas / horas_disponibles) * 100, 2) if horas_disponibles else 0
        resultado.append({
            "id_cancha": f["id_cancha"],
            "nombre_cancha": f["nombre_cancha"],
            "tipo_deporte": f["tipo_deporte"],
            "horas_reservadas": round(horas, 2),
            "horas_disponibles": horas_disponibles,
            "porcentaje_ocupacion": porcentaje,
        })
    return resultado


# =====================================================================
# REPORTE GENERADO: INGRESOS POR CANCHA
# =====================================================================
def reporte_ingresos(fecha_inicio, fecha_fin):
    _validar_rango(fecha_inicio, fecha_fin)
    sql = text("""
        SELECT
            c.id_cancha,
            c.nombre_cancha,
            c.tipo_deporte,
            COUNT(p.id_pago) AS cantidad_pagos,
            COALESCE(SUM(p.monto) FILTER (WHERE p.estado_pago = 'pagado'), 0) AS total_ingresos,
            COALESCE(SUM(p.monto) FILTER (WHERE p.estado_pago = 'pendiente'), 0) AS total_pendiente,
            COALESCE(SUM(p.monto) FILTER (WHERE p.estado_pago = 'reembolsado'), 0) AS total_reembolsado
        FROM cancha c
        LEFT JOIN reserva r ON r.id_cancha = c.id_cancha
        LEFT JOIN pago p
               ON p.id_reserva = r.id_reserva
              AND p.fecha_pago::date BETWEEN :fi AND :ff
        GROUP BY c.id_cancha, c.nombre_cancha, c.tipo_deporte
        ORDER BY total_ingresos DESC, c.nombre_cancha ASC
    """)
    filas = db.session.execute(sql, {"fi": fecha_inicio, "ff": fecha_fin}).mappings().all()
    return [
        {
            "id_cancha": f["id_cancha"],
            "nombre_cancha": f["nombre_cancha"],
            "tipo_deporte": f["tipo_deporte"],
            "cantidad_pagos": f["cantidad_pagos"],
            "total_ingresos": float(f["total_ingresos"] or 0),
            "total_pendiente": float(f["total_pendiente"] or 0),
            "total_reembolsado": float(f["total_reembolsado"] or 0),
        }
        for f in filas
    ]


REPORTES = {
    "reservas": reporte_reservas,
    "ocupacion": reporte_ocupacion,
    "ingresos": reporte_ingresos,
}