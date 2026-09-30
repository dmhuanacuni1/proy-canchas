from extensions import db
from models.cancha import Cancha
from models.categoria import Categoria
from models.administrador import Administrador
from validators.cancha_validator import (
    convertir_precio,
    convertir_id_entero,
    convertir_bool,
    validar_estado,
)


def obtener_categoria(id_categoria):
    categoria = db.session.get(Categoria, id_categoria)
    if not categoria:
        raise ValueError("La categoría indicada no existe.")
    return categoria


def obtener_administrador(id_administrador):
    administrador = db.session.get(Administrador, id_administrador)
    if not administrador:
        raise ValueError("El administrador indicado no existe.")
    return administrador


def listar_canchas(estado=None):
    query = Cancha.query
    if estado:
        estado = validar_estado(estado)
        query = query.filter_by(estado=estado)
    return query.order_by(Cancha.id_cancha.asc()).all()


def obtener_cancha_por_id(id_cancha):
    cancha = db.session.get(Cancha, id_cancha)
    if not cancha:
        raise ValueError("La cancha no existe.")
    return cancha


def crear_cancha(datos_texto, datos_crudos):
    precio = convertir_precio(datos_crudos.get("precio_hora"))
    id_categoria = convertir_id_entero(datos_crudos.get("id_categoria"), "id_categoria")
    id_administrador = convertir_id_entero(
        datos_crudos.get("id_administrador"), "id_administrador"
    )

    obtener_categoria(id_categoria)
    obtener_administrador(id_administrador)

    estado = validar_estado(datos_crudos.get("estado", "disponible"))
    techada = convertir_bool(datos_crudos.get("techada", False))

    nueva = Cancha(
        nombre_cancha=datos_texto["nombre_cancha"],
        tipo_deporte=datos_texto["tipo_deporte"],
        precio_hora=precio,
        ubicacion=datos_texto.get("ubicacion"),
        estado=estado,
        techada=techada,
        superficie=datos_texto.get("superficie"),
        id_categoria=id_categoria,
        id_administrador=id_administrador,
    )
    db.session.add(nueva)
    db.session.commit()
    return nueva


def modificar_cancha(id_cancha, datos_texto, datos_crudos):
    cancha = obtener_cancha_por_id(id_cancha)

    for campo in ("nombre_cancha", "tipo_deporte", "ubicacion", "superficie"):
        if campo in datos_texto:
            setattr(cancha, campo, datos_texto[campo])

    if "precio_hora" in datos_crudos:
        cancha.precio_hora = convertir_precio(datos_crudos["precio_hora"])

    if "techada" in datos_crudos:
        cancha.techada = convertir_bool(datos_crudos["techada"])

    if "estado" in datos_crudos:
        cancha.estado = validar_estado(datos_crudos["estado"])

    if "id_categoria" in datos_crudos:
        id_categoria = convertir_id_entero(datos_crudos["id_categoria"], "id_categoria")
        obtener_categoria(id_categoria)
        cancha.id_categoria = id_categoria

    if "id_administrador" in datos_crudos:
        id_administrador = convertir_id_entero(
            datos_crudos["id_administrador"], "id_administrador"
        )
        obtener_administrador(id_administrador)
        cancha.id_administrador = id_administrador

    db.session.commit()
    return cancha


def eliminar_cancha(id_cancha):
    cancha = obtener_cancha_por_id(id_cancha)
    db.session.delete(cancha)
    db.session.commit()


def cambiar_estado_cancha(id_cancha, nuevo_estado):
    cancha = obtener_cancha_por_id(id_cancha)
    cancha.estado = validar_estado(nuevo_estado)
    db.session.commit()
    return cancha
