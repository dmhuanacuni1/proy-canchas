from sqlalchemy import text

from extensions import db
from models.pago import Pago
from models.reserva import Reserva
from models.cancha import Cancha
from models.empleado import Empleado

METODOS_PAGO_VALIDOS = ["efectivo", "tarjeta", "transferencia", "qr"]


def listar_pagos(estado=None, con_detalle=False, id_cliente=None):
    if estado:
        estado = estado.strip().lower()
        if estado not in ("pendiente", "pagado", "reembolsado"):
            raise ValueError("Estado no válido. Use: pendiente, pagado o reembolsado.")

    query = Pago.query
    if estado:
        query = query.filter_by(estado_pago=estado)
    if id_cliente:
        query = query.join(Reserva).filter(Reserva.id_cliente == id_cliente)

    pagos = query.order_by(Pago.fecha_pago.desc()).all()
    if con_detalle:
        return [_pago_detalle(p) for p in pagos]
    return pagos


def _info_cliente_nombre(id_cliente):
    if not id_cliente:
        return None
    sql = text("""
        SELECT per.nombre || ' ' || per.apellido AS nombre
        FROM cliente cl
        JOIN usuario u   ON u.id_usuario = cl.id_usuario
        JOIN persona per ON per.id_persona = u.id_persona
        WHERE cl.id_cliente = :id_cliente
    """)
    fila = db.session.execute(sql, {"id_cliente": id_cliente}).first()
    return fila[0] if fila else None


def _pago_detalle(pago):
    datos = pago.to_dict()
    datos["metodo_pago"] = (pago.metodo_pago or "").capitalize()
    reserva = db.session.get(Reserva, pago.id_reserva)
    if reserva:
        cancha = db.session.get(Cancha, reserva.id_cancha) if reserva.id_cancha else None
        datos["reserva"] = {
            "id_reserva": reserva.id_reserva,
            "fecha_reserva": reserva.fecha_reserva.isoformat() if reserva.fecha_reserva else None,
            "hora_inicio": reserva.hora_inicio.strftime("%H:%M") if reserva.hora_inicio else None,
            "estado_reserva": reserva.estado_reserva,
            "cancha": getattr(cancha, "nombre_cancha", None) if cancha else None,
            "cliente": _info_cliente_nombre(reserva.id_cliente),
        }
    return datos


def listar_reservas_para_pago():
    sql = text("""
        SELECT
            r.id_reserva,
            r.fecha_reserva,
            r.hora_inicio,
            r.hora_fin,
            r.monto_total,
            r.estado_reserva,
            c.nombre_cancha,
            c.tipo_deporte,
            per.nombre || ' ' || per.apellido AS cliente
        FROM reserva r
        JOIN cancha c       ON c.id_cancha = r.id_cancha
        JOIN cliente cl     ON cl.id_cliente = r.id_cliente
        JOIN usuario u      ON u.id_usuario = cl.id_usuario
        JOIN persona per    ON per.id_persona = u.id_persona
        WHERE r.estado_reserva IN ('confirmada', 'completada', 'pendiente')
        ORDER BY r.fecha_reserva DESC
    """)
    filas = db.session.execute(sql).mappings().all()
    return [
        {
            "id_reserva": f["id_reserva"],
            "fecha_reserva": str(f["fecha_reserva"]) if f["fecha_reserva"] else None,
            "hora_inicio": str(f["hora_inicio"]) if f["hora_inicio"] else None,
            "monto_total": float(f["monto_total"]) if f["monto_total"] is not None else None,
            "estado_reserva": f["estado_reserva"],
            "cancha": f["nombre_cancha"],
            "tipo_deporte": f["tipo_deporte"],
            "cliente": f["cliente"],
        }
        for f in filas
    ]


def obtener_pago_por_id(id_pago):
    pago = db.session.get(Pago, id_pago)
    if not pago:
        raise ValueError("El pago no existe.")
    return pago


def crear_pago(datos):
    id_reserva = datos.get("id_reserva")
    reserva = db.session.get(Reserva, id_reserva)
    if not reserva:
        raise ValueError("La reserva indicada no existe.")

    metodo = str(datos["metodo_pago"]).strip().lower()
    if metodo not in METODOS_PAGO_VALIDOS:
        raise ValueError(
            "Método de pago no válido. Use: efectivo, tarjeta, transferencia o qr."
        )

    id_empleado = datos.get("id_empleado")
    if id_empleado and not db.session.get(Empleado, id_empleado):
        raise ValueError("El empleado indicado no existe.")

    nuevo = Pago(
        metodo_pago=metodo,
        estado_pago=datos.get("estado_pago", "pendiente"),
        monto=datos["monto"],
        fecha_pago=datos["fecha_pago"],
        id_reserva=id_reserva,
        id_empleado=id_empleado,
    )
    db.session.add(nuevo)
    db.session.commit()
    return nuevo


def modificar_estado_pago(id_pago, nuevo_estado):
    pago = obtener_pago_por_id(id_pago)
    pago.estado_pago = nuevo_estado
    db.session.commit()
    return pago


def eliminar_pago(id_pago):
    pago = obtener_pago_por_id(id_pago)
    db.session.delete(pago)
    db.session.commit()
    return True