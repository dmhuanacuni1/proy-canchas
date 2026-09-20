import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "No se encontró DATABASE_URL en el archivo .env."
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
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

    if precio <= 0:
        raise ValueError("precio_hora debe ser mayor que 0.")

    return precio


def convertir_id_entero(valor, nombre):
    if valor is None or valor == "":
        raise ValueError(f"{nombre} es obligatorio.")

    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número entero.")


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
    data = request.get_json(silent=True) or {}

    nombre = str(data.get("nombre", "")).strip()
    descripcion = data.get("descripcion")

    if not nombre:
        return error_json(
            "El campo nombre es obligatorio."
        )

    if len(nombre) > 50:
        return error_json(
            "El nombre de la categoría no puede superar 50 caracteres."
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
                str(descripcion).strip()
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
    categoria = db.session.get(Categoria, id_categoria)

    if not categoria:
        return error_json(
            "La categoría no existe.",
            codigo=404,
        )

    return jsonify(categoria.to_dict()), 200


@app.patch("/api/categorias/<int:id_categoria>")
def modificar_categoria(id_categoria):
    categoria = db.session.get(Categoria, id_categoria)

    if not categoria:
        return error_json(
            "La categoría no existe.",
            codigo=404,
        )

    data = request.get_json(silent=True) or {}

    try:
        if "nombre" in data:
            nombre = str(data["nombre"]).strip()

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
            categoria.descripcion = (
                str(data["descripcion"]).strip()
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
    data = request.get_json(silent=True) or {}

    nombre = str(data.get("nombre_cancha", "")).strip()
    deporte = str(data.get("tipo_deporte", "")).strip()

    if not nombre or not deporte:
        return error_json(
            "Campos obligatorios faltantes.",
            "Debe proporcionar nombre_cancha y tipo_deporte.",
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

        estado = str(
            data.get("estado", "disponible")
        ).strip().lower()

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
                str(data.get("ubicacion", "")).strip()
                or None
            ),
            estado=estado,
            techada=techada,
            superficie=(
                str(data.get("superficie", "")).strip()
                or None
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
    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    return jsonify(cancha.to_dict()), 200


@app.patch("/api/canchas/<int:id_cancha>")
def modificar_cancha(id_cancha):
    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    data = request.get_json(silent=True) or {}

    try:
        if "nombre_cancha" in data:
            nombre = str(data["nombre_cancha"]).strip()

            if not nombre:
                return error_json(
                    "El nombre de la cancha no puede estar vacío."
                )

            cancha.nombre_cancha = nombre

        if "tipo_deporte" in data:
            deporte = str(data["tipo_deporte"]).strip()

            if not deporte:
                return error_json(
                    "El deporte no puede estar vacío."
                )

            cancha.tipo_deporte = deporte

        if "precio_hora" in data:
            cancha.precio_hora = convertir_precio(
                data["precio_hora"]
            )

        if "ubicacion" in data:
            cancha.ubicacion = (
                str(data["ubicacion"]).strip()
                or None
            )

        if "superficie" in data:
            cancha.superficie = (
                str(data["superficie"]).strip()
                or None
            )

        if "techada" in data:
            cancha.techada = convertir_bool(
                data["techada"]
            )

        if "estado" in data:
            estado = str(
                data["estado"]
            ).strip().lower()

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
    cancha = db.session.get(Cancha, id_cancha)

    if not cancha:
        return error_json(
            "La cancha no existe.",
            codigo=404,
        )

    data = request.get_json(silent=True) or {}
    estado = str(data.get("estado", "")).strip().lower()

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

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
