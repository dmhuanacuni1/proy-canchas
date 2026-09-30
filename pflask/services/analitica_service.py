from sqlalchemy import text

from extensions import db


def _filas(query, params=None):
    resultado = db.session.execute(text(query), params or {})
    columnas = list(resultado.keys())
    return [
        {c: (row[i].isoformat() if hasattr(row[i], "isoformat") else float(row[i])
             if row[i] is not None and isinstance(row[i], (int, float)) else row[i])
         for i, c in enumerate(columnas)}
        for row in resultado.fetchall()
    ]


def resumen_analitico():
    """Agrupa las vistas analíticas en una sola respuesta para el dashboard."""
    return {
        "ganancias_mensuales": _filas(
            "SELECT DISTINCT mes, cantidad_pagados, ingresos, por_cobrar, reembolsos "
            "FROM vista_ganancias_mensuales ORDER BY mes"
        ),
        "empleados": _filas(
            "SELECT nombre_empleado, cargo, pagos_procesados, total_recaudado, por_cobrar "
            "FROM vista_analitica_empleados ORDER BY total_recaudado DESC"
        ),
        "top_canchas": _filas(
            "SELECT nombre_cancha, tipo_deporte, SUM(cantidad) AS reservas "
            "FROM vista_analitica_reservas "
            "WHERE estado_reserva <> 'cancelada' "
            "GROUP BY nombre_cancha, tipo_deporte ORDER BY reservas DESC"
        ),
        "saldos_clientes": _filas(
            "SELECT nombre_cliente, total_comprometido, total_pagado, saldo_pendiente "
            "FROM vista_saldos_clientes ORDER BY saldo_pendiente DESC"
        ),
        "pagos_por_metodo": _filas(
            "SELECT metodo_pago, SUM(monto_total) AS total, "
            "SUM(cantidad_pagos) AS cantidad "
            "FROM vista_analitica_pagos GROUP BY metodo_pago "
            "ORDER BY total DESC"
        ),
    }