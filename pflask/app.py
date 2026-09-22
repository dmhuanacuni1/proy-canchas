import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from extensions import db

load_dotenv()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "No se encontró DATABASE_URL en el archivo .env."
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
CORS(app)


# ==========================================================
# MODELOS
# ==========================================================

class Categoria(db.Model):
    __tablename__ = "categoria"

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)

    def to_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
        }


class Cancha(db.Model):
    __tablename__ = "cancha"

    id_cancha = db.Column(db.Integer, primary_key=True)
    nombre_cancha = db.Column(db.String(80), nullable=False)
    tipo_deporte = db.Column(db.String(50), nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    ubicacion = db.Column(db.String(150))
    estado = db.Column(db.String(20), nullable=False, default="disponible")
    techada = db.Column(db.Boolean, nullable=False, default=False)
    superficie = db.Column(db.String(50))

    # En la BD estos dos campos son NOT NULL.
    id_categoria = db.Column(
        db.Integer,
        db.ForeignKey("categoria.id_categoria"),
        nullable=False,
    )

    id_administrador = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_administrador"),
        nullable=False,
    )

    categoria = db.relationship("Categoria", lazy=True)

    def to_dict(self):
        return {
            "id_cancha": self.id_cancha,
            "nombre_cancha": self.nombre_cancha,
            "tipo_deporte": self.tipo_deporte,
            "precio_hora": float(self.precio_hora),
            "ubicacion": self.ubicacion,
            "estado": self.estado,
            "techada": bool(self.techada),
            "superficie": self.superficie,
            "id_categoria": self.id_categoria,
            "nombre_categoria": (
                self.categoria.nombre if self.categoria else None
            ),
            "id_administrador": self.id_administrador,
        }


# ==========================================================
# CONFIGURACIONES Y FUNCIONES AUXILIARES
# ==========================================================

# Estos valores deben coincidir con el CHECK de PostgreSQL.
ESTADOS_VALIDOS = {
    "disponible",
    "mantenimiento",
    "fuera_servicio",
}


def error_json(mensaje, detalle=None, codigo=400):
    respuesta = {"error": mensaje}

    if detalle:
        respuesta["detalle"] = detalle

    return jsonify(respuesta), codigo


def convertir_precio(valor):
    if valor is None or valor == "":
        raise ValueError("El precio_hora es obligatorio.")

    try:
        precio = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError("precio_hora debe ser un número válido.")

    if not precio.is_finite():
        raise ValueError("precio_hora debe ser un número finito.")

    if precio <= 0:
        raise ValueError("precio_hora debe ser mayor que 0.")

    return precio


def convertir_id_entero(valor, nombre):
    if valor is None or valor == "":
        raise ValueError(f"{nombre} es obligatorio.")

    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"{nombre} debe ser un número entero.")

    if valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que 0.")

    return valor


def convertir_bool(valor, nombre="techada"):
    if isinstance(valor, bool):
        return valor

    if isinstance(valor, str):
        valor_limpio = valor.strip().lower()

        if valor_limpio in {"true", "1", "si", "sí"}:
            return True

        if valor_limpio in {"false", "0", "no"}:
            return False

    if isinstance(valor, int) and valor in (0, 1):
        return bool(valor)

    raise ValueError(f"{nombre} debe ser true o false.")


def obtener_categoria(id_categoria):
    categoria = db.session.get(Categoria, id_categoria)

    if not categoria:
        raise ValueError("La categoría indicada no existe.")

    return categoria


def obtener_administrador(id_administrador):
    # Se consulta mediante SQLAlchemy sin crear un CRUD de administradores.
    administrador = db.session.get(Administrador, id_administrador)

    if not administrador:
        raise ValueError("El administrador indicado no existe.")

    return administrador


# ==========================================================
# MODELO MÍNIMO DE ADMINISTRADOR
# Necesario porque cancha.id_administrador es FK NOT NULL.
# No se implementan rutas de administración de usuarios.
# ==========================================================

class Administrador(db.Model):
    __tablename__ = "administrador"

    id_administrador = db.Column(db.Integer, primary_key=True)
    nivel_acceso = db.Column(db.String(30), nullable=False)
    fecha_designado = db.Column(db.Date, nullable=False)
    area_responsabilidad = db.Column(db.String(100))
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False,
    )


# ==========================================================
# RUTA DE INICIO
# ==========================================================

@app.get("/")
def inicio():
    return jsonify({
        "mensaje": "API de Gestión de Canchas funcionando",
        "endpoints": {
            "categorias": [
                "POST /api/categorias",
                "GET /api/categorias",
                "GET /api/categorias/<id>",
                "PATCH /api/categorias/<id>",
                "DELETE /api/categorias/<id>",
            ],
            "canchas": [
                "POST /api/canchas",
                "GET /api/canchas",
                "GET /api/canchas/<id>",
                "PATCH /api/canchas/<id>",
                "DELETE /api/canchas/<id>",
                "PATCH /api/canchas/<id>/estado",
            ],
        },
    }), 200


# ==========================================================
# CATEGORÍAS
# ==========================================================

@app.post("/api/categorias")
def crear_categoria():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_json(
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )

    if not data:
        return error_json(
            "El cuerpo de la solicitud no puede estar vacío."
        )

    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not isinstance(nombre, str):
        return error_json(
            "El campo nombre debe ser un texto válido."
        )

    nombre = nombre.strip()

    if not nombre:
        return error_json(
            "El campo nombre es obligatorio."
        )

    if len(nombre) > 50:
        return error_json(
            "El nombre de la categoría no puede superar 50 caracteres."
        )

    if descripcion is not None and not isinstance(descripcion, str):
        return error_json(
            "La descripción debe ser un texto válido o null."
        )

    try:
        categoria_existente = Categoria.query.filter_by(
            nombre=nombre
        ).first()

        if categoria_existente:
            return error_json(
                "Ya existe una categoría con ese nombre.",
                codigo=409,
            )

        nueva_categoria = Categoria(
            nombre=nombre,
            descripcion=(
                descripcion.strip()
                if descripcion is not None
                else None
            ),
        )

        db.session.add(nueva_categoria)
        db.session.commit()

        return jsonify({
            "mensaje": "Categoría creada con éxito.",
            "categoria": nueva_categoria.to_dict(),
        }), 201

    except IntegrityError:
        db.session.rollback()
        return error_json(
            "No se pudo crear la categoría porque el nombre ya existe.",
            codigo=409,
        )

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al crear categoría")
        return error_json(
            "Error interno al crear la categoría.",
            str(e),
            500,
        )


@app.get("/api/categorias")
def obtener_categorias():
    try:
        categorias = Categoria.query.order_by(
            Categoria.id_categoria.asc()
        ).all()

        return jsonify([
            categoria.to_dict()
            for categoria in categorias
        ]), 200

    except Exception as e:
        app.logger.exception("Error al obtener categorías")
        return error_json(
            "Error interno al obtener categorías.",
            str(e),
            500,
        )


@app.get("/api/categorias/<int:id_categoria>")
def obtener_categoria(id_categoria):
    if id_categoria <= 0:
        return error_json(
            "El id_categoria debe ser mayor que 0."
        )

    categoria = db.session.get(Categoria, id_categoria)

    if not categoria:
        return error_json(
            "La categoría no existe.",
            codigo=404,
        )

    return jsonify(categoria.to_dict()), 200


@app.patch("/api/categorias/<int:id_categoria>")
def modificar_categoria(id_categoria):
    if id_categoria <= 0:
        return error_json(
            "El id_categoria debe ser mayor que 0."
        )

    categoria = db.session.get(Categoria, id_categoria)

    if not categoria:
        return error_json(
            "La categoría no existe.",
            codigo=404,
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_json(
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )

    if not data:
        return error_json(
            "El cuerpo de la solicitud no puede estar vacío."
        )

    try:
        if "nombre" in data:
            if not isinstance(data["nombre"], str):
                return error_json(
                    "El nombre de la categoría debe ser un texto válido."
                )

            nombre = data["nombre"].strip()

            if not nombre:
                return error_json(
                    "El nombre de la categoría no puede estar vacío."
                )

            if len(nombre) > 50:
                return error_json(
                    "El nombre de la categoría no puede superar 50 caracteres."
                )

            otra_categoria = Categoria.query.filter(
                Categoria.nombre == nombre,
                Categoria.id_categoria != id_categoria,
            ).first()

            if otra_categoria:
                return error_json(
                    "Ya existe otra categoría con ese nombre.",
                    codigo=409,
                )

            categoria.nombre = nombre

        if "descripcion" in data:
            if data["descripcion"] is not None and not isinstance(data["descripcion"], str):
                return error_json(
                    "La descripción debe ser un texto válido o null."
                )

            categoria.descripcion = (
                data["descripcion"].strip()
                if data["descripcion"] is not None
                else None
            )

        db.session.commit()

        return jsonify({
            "mensaje": "Categoría modificada con éxito.",
            "categoria": categoria.to_dict(),
        }), 200

    except IntegrityError:
        db.session.rollback()
        return error_json(
            "No se pudo modificar la categoría.",
            codigo=409,
        )

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al modificar categoría")
        return error_json(
            "Error interno al modificar la categoría.",
            str(e),
            500,
        )


@app.delete("/api/categorias/<int:id_categoria>")
def eliminar_categoria(id_categoria):
    if id_categoria <= 0:
        return error_json(
            "El id_categoria debe ser mayor que 0."
        )

    categoria = db.session.get(Categoria, id_categoria)

    if not categoria:
        return error_json(
            "La categoría no existe.",
            codigo=404,
        )

    try:
        # PostgreSQL tiene ON DELETE RESTRICT para cancha.id_categoria.
        # Por eso no se permite eliminar una categoría que todavía tenga canchas.
        if Cancha.query.filter_by(id_categoria=id_categoria).first():
            return error_json(
                "No se puede eliminar la categoría porque tiene canchas asociadas.",
                codigo=409,
            )

        db.session.delete(categoria)
        db.session.commit()

        return jsonify({
            "mensaje": "Categoría eliminada con éxito.",
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al eliminar categoría")
        return error_json(
            "No se pudo eliminar la categoría.",
            str(e),
            409,
        )


# ==========================================================
# CANCHAS
# ==========================================================

@app.post("/api/canchas")
def crear_cancha():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_json(
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )

    if not data:
        return error_json(
            "El cuerpo de la solicitud no puede estar vacío."
        )

    nombre = data.get("nombre_cancha")
    deporte = data.get("tipo_deporte")

    if not isinstance(nombre, str):
        return error_json(
            "nombre_cancha debe ser texto válido."
        )
    if not isinstance(deporte, str):
        return error_json(
            "tipo_deporte debe ser texto válido."
        )

    nombre = nombre.strip()
    deporte = deporte.strip()

    if not nombre or not deporte:
        return error_json(
            "Campos obligatorios faltantes.",
            "Debe proporcionar nombre_cancha y tipo_deporte.",
        )

    if len(nombre) > 80:
        return error_json(
            "El nombre de la cancha no puede superar 80 caracteres."
        )

    if len(deporte) > 50:
        return error_json(
            "El tipo de deporte no puede superar 50 caracteres."
        )

    ubicacion = data.get("ubicacion")
    superficie = data.get("superficie")

    if ubicacion is not None and not isinstance(ubicacion, str):
        return error_json(
            "La ubicación debe ser un texto válido o null."
        )

    if superficie is not None and not isinstance(superficie, str):
        return error_json(
            "La superficie debe ser un texto válido o null."
        )

    if ubicacion is not None and len(ubicacion.strip()) > 150:
        return error_json(
            "La ubicación no puede superar 150 caracteres."
        )

    if superficie is not None and len(superficie.strip()) > 50:
        return error_json(
            "La superficie no puede superar 50 caracteres."
        )

    try:
        precio = convertir_precio(data.get("precio_hora"))

        id_categoria = convertir_id_entero(
            data.get("id_categoria"),
            "id_categoria",
        )

        id_administrador = convertir_id_entero(
            data.get("id_administrador"),
            "id_administrador",
        )

        obtener_categoria(id_categoria)
        obtener_administrador(id_administrador)

        estado = data.get("estado", "disponible")

        if not isinstance(estado, str):
            return error_json(
                "El estado debe ser un texto válido."
            )

        estado = estado.strip().lower()

        if estado not in ESTADOS_VALIDOS:
            return error_json(
                "Estado no válido.",
                "Use: disponible, mantenimiento o fuera_servicio.",
            )

        techada = convertir_bool(
            data.get("techada", False)
        )

        nueva_cancha = Cancha(
            nombre_cancha=nombre,
            tipo_deporte=deporte,
            precio_hora=precio,
            ubicacion=(
                ubicacion.strip()
                if ubicacion is not None and ubicacion.strip()
                else None
            ),
            estado=estado,
            techada=techada,
            superficie=(
                superficie.strip()
                if superficie is not None and superficie.strip()
                else None
            ),
            id_categoria=id_categoria,
            id_administrador=id_administrador,
        )

        db.session.add(nueva_cancha)
        db.session.commit()

        return jsonify({
            "mensaje": "Cancha registrada con éxito.",
            "cancha": nueva_cancha.to_dict(),
        }), 201

    except ValueError as e:
        db.session.rollback()
        return error_json(
            "Datos inválidos.",
            str(e),
        )

    except IntegrityError as e:
        db.session.rollback()
        return error_json(
            "No se pudo registrar la cancha.",
            str(e.orig),
            409,
        )

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al crear cancha")
        return error_json(
            "Error interno al registrar la cancha.",
            str(e),
            500,
        )


@app.get("/api/canchas")
def obtener_canchas():
    try:
        estado = request.args.get("estado")

        query = Cancha.query

        if estado:
            estado = estado.strip().lower()

            if estado not in ESTADOS_VALIDOS:
                return error_json(
                    "Estado no válido.",
                    "Use: disponible, mantenimiento o fuera_servicio.",
                )

            query = query.filter_by(estado=estado)

        canchas = query.order_by(
            Cancha.id_cancha.asc()
        ).all()

        return jsonify([
            cancha.to_dict()
            for cancha in canchas
        ]), 200

    except Exception as e:
        app.logger.exception("Error al obtener canchas")
        return error_json(
            "Error interno al obtener canchas.",
            str(e),
            500,
        )


@app.get("/api/canchas/<int:id_cancha>")
def obtener_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json(
            "El id_cancha debe ser mayor que 0."
        )

    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    return jsonify(cancha.to_dict()), 200


@app.patch("/api/canchas/<int:id_cancha>")
def modificar_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json(
            "El id_cancha debe ser mayor que 0."
        )

    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_json(
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )

    if not data:
        return error_json(
            "El cuerpo de la solicitud no puede estar vacío."
        )

    try:
        if "nombre_cancha" in data:
            if not isinstance(data["nombre_cancha"], str):
                return error_json(
                    "El nombre de la cancha debe ser un texto válido."
                )

            nombre = data["nombre_cancha"].strip()

            if not nombre:
                return error_json(
                    "El nombre de la cancha no puede estar vacío."
                )

            if len(nombre) > 80:
                return error_json(
                    "El nombre de la cancha no puede superar 80 caracteres."
                )

            cancha.nombre_cancha = nombre

        if "tipo_deporte" in data:
            if not isinstance(data["tipo_deporte"], str):
                return error_json(
                    "El deporte debe ser un texto válido."
                )

            deporte = data["tipo_deporte"].strip()

            if not deporte:
                return error_json(
                    "El deporte no puede estar vacío."
                )

            if len(deporte) > 50:
                return error_json(
                    "El tipo de deporte no puede superar 50 caracteres."
                )

            cancha.tipo_deporte = deporte

        if "precio_hora" in data:
            cancha.precio_hora = convertir_precio(
                data["precio_hora"]
            )

        if "ubicacion" in data:
            if data["ubicacion"] is not None and not isinstance(data["ubicacion"], str):
                return error_json(
                    "La ubicación debe ser un texto válido o null."
                )

            if data["ubicacion"] is not None and len(data["ubicacion"].strip()) > 150:
                return error_json(
                    "La ubicación no puede superar 150 caracteres."
                )

            cancha.ubicacion = (
                data["ubicacion"].strip()
                if data["ubicacion"] is not None and data["ubicacion"].strip()
                else None
            )

        if "superficie" in data:
            if data["superficie"] is not None and not isinstance(data["superficie"], str):
                return error_json(
                    "La superficie debe ser un texto válido o null."
                )

            if data["superficie"] is not None and len(data["superficie"].strip()) > 50:
                return error_json(
                    "La superficie no puede superar 50 caracteres."
                )

            cancha.superficie = (
                data["superficie"].strip()
                if data["superficie"] is not None and data["superficie"].strip()
                else None
            )

        if "techada" in data:
            cancha.techada = convertir_bool(
                data["techada"]
            )

        if "estado" in data:
            if not isinstance(data["estado"], str):
                return error_json(
                    "El estado debe ser un texto válido."
                )

            estado = data["estado"].strip().lower()

            if estado not in ESTADOS_VALIDOS:
                return error_json(
                    "Estado no válido.",
                    "Use: disponible, mantenimiento o fuera_servicio.",
                )

            cancha.estado = estado

        if "id_categoria" in data:
            id_categoria = convertir_id_entero(
                data["id_categoria"],
                "id_categoria",
            )

            obtener_categoria(id_categoria)
            cancha.id_categoria = id_categoria

        if "id_administrador" in data:
            id_administrador = convertir_id_entero(
                data["id_administrador"],
                "id_administrador",
            )

            obtener_administrador(id_administrador)
            cancha.id_administrador = id_administrador

        db.session.commit()

        return jsonify({
            "mensaje": "Cancha modificada con éxito.",
            "cancha": cancha.to_dict(),
        }), 200

    except ValueError as e:
        db.session.rollback()
        return error_json(
            "Datos inválidos.",
            str(e),
        )

    except IntegrityError as e:
        db.session.rollback()
        return error_json(
            "No se pudo modificar la cancha.",
            str(e.orig),
            409,
        )

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al modificar cancha")
        return error_json(
            "Error interno al modificar la cancha.",
            str(e),
            500,
        )


@app.delete("/api/canchas/<int:id_cancha>")
def eliminar_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json(
            "El id_cancha debe ser mayor que 0."
        )

    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    try:
        db.session.delete(cancha)
        db.session.commit()

        return jsonify({
            "mensaje": "Cancha retirada con éxito.",
        }), 200

    except IntegrityError:
        db.session.rollback()

        return error_json(
            "No se puede retirar físicamente la cancha porque tiene reservas o eventos asociados. Use PATCH /api/canchas/<id>/estado para colocarla como fuera_servicio.",
            codigo=409,
        )

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al retirar cancha")

        return error_json(
            "No se pudo retirar la cancha.",
            str(e),
            409,
        )


@app.patch("/api/canchas/<int:id_cancha>/estado")
def cambiar_estado_cancha(id_cancha):
    if id_cancha <= 0:
        return error_json(
            "El id_cancha debe ser mayor que 0."
        )

    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_json(
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )

    if not data:
        return error_json(
            "El cuerpo de la solicitud no puede estar vacío."
        )

    estado = data.get("estado")

    if not isinstance(estado, str):
        return error_json(
            "El estado debe ser un texto válido."
        )

    estado = estado.strip().lower()

    if estado not in ESTADOS_VALIDOS:
        return error_json(
            "Estado no válido.",
            "Use: disponible, mantenimiento o fuera_servicio.",
        )

    try:
        cancha.estado = estado
        db.session.commit()

        return jsonify({
            "mensaje": f"Estado actualizado a {estado}.",
            "cancha": cancha.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error al cambiar estado")

        return error_json(
            "Error interno al cambiar el estado.",
            str(e),
            500,
        )


# ==========================================================
# EJECUCIÓN
# ==========================================================

# Ver auth/LEEME.txt
from auth import register_auth
register_auth(app)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
