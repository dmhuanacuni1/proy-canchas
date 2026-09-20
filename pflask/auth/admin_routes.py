from datetime import date

from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from .models import Administrador, Cliente, Empleado, Persona, Usuario
from .security import frontend_role, hash_password, require_auth

admin_bp = Blueprint("admin", __name__)

VALID_ROLES = ("cliente", "administrador", "empleado")
FRONTEND_TO_DB_ROLE = {
    "admin": "administrador",
    "user": "cliente",
    "empleado": "empleado",
    "administrador": "administrador",
    "cliente": "cliente",
}


def _serialize_user(usuario, persona):
    return {
        "id": usuario.id_usuario,
        "email": persona.email if persona else None,
        "role": frontend_role(usuario.rol),
        "rol": usuario.rol,
        "username": usuario.username,
        "nombre": persona.nombre if persona else None,
        "apellido": persona.apellido if persona else None,
        "ci": persona.ci if persona else None,
        "celular": persona.celular if persona else None,
    }


def _normalize_rol(value):
    if not value:
        return None
    key = str(value).strip().lower()
    return FRONTEND_TO_DB_ROLE.get(key, key if key in VALID_ROLES else None)


def _administrador_id_para_empleado():
    propio = Administrador.query.filter_by(id_usuario=g.current_user.id_usuario).first()
    if propio:
        return propio.id_administrador
    cualquiera = Administrador.query.first()
    return cualquiera.id_administrador if cualquiera else None


def _sync_rol_tablas(user, nuevo_rol):
    if nuevo_rol == "cliente":
        if not Cliente.query.filter_by(id_usuario=user.id_usuario).first():
            db.session.add(Cliente(
                id_usuario=user.id_usuario,
                fecha_afiliacion=date.today(),
            ))
    else:
        Cliente.query.filter_by(id_usuario=user.id_usuario).delete(synchronize_session=False)

    if nuevo_rol == "administrador":
        if not Administrador.query.filter_by(id_usuario=user.id_usuario).first():
            db.session.add(Administrador(
                nivel_acceso="parcial",
                fecha_designado=date.today(),
                area_responsabilidad="General",
                id_usuario=user.id_usuario,
            ))
    else:
        Administrador.query.filter_by(id_usuario=user.id_usuario).delete(synchronize_session=False)

    if nuevo_rol == "empleado":
        existente = Empleado.query.filter_by(id_usuario=user.id_usuario).first()
        if not existente:
            admin_id = _administrador_id_para_empleado()
            if not admin_id:
                raise ValueError("No hay un administrador al que asignar el empleado")
            db.session.add(Empleado(
                cargo="Sin asignar",
                turno_laboral="Mañana",
                fecha_contratacion=date.today(),
                salario=0,
                id_administrador=admin_id,
                id_usuario=user.id_usuario,
            ))
    else:
        Empleado.query.filter_by(id_usuario=user.id_usuario).update(
            {"id_usuario": None}, synchronize_session=False
        )


@admin_bp.route("/admin/users", methods=["GET"])
@require_auth(roles=["administrador"])
def list_users():
    rows = (
        db.session.query(Usuario, Persona)
        .join(Persona, Usuario.id_persona == Persona.id_persona)
        .order_by(Usuario.id_usuario.asc())
        .all()
    )
    return jsonify([_serialize_user(usuario, persona) for usuario, persona in rows]), 200


@admin_bp.route("/admin/users/<int:user_id>", methods=["PUT", "PATCH"])
@require_auth(roles=["administrador"])
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    persona = db.session.get(Persona, user.id_persona)
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    nuevo_rol = _normalize_rol(data.get("rol") or data.get("role"))
    if "rol" in data or "role" in data:
        if not nuevo_rol:
            return jsonify({"error": "Rol inválido. Usa cliente, administrador o empleado"}), 400
        if user.id_usuario == g.current_user.id_usuario and nuevo_rol != user.rol:
            return jsonify({"error": "No puedes cambiar tu propio rol"}), 400
        if user.rol == "administrador" and nuevo_rol != "administrador":
            otros = Usuario.query.filter(
                Usuario.rol == "administrador",
                Usuario.id_usuario != user.id_usuario,
            ).count()
            if otros == 0:
                return jsonify({"error": "No puedes quitar el último administrador"}), 400

    nombre = data.get("nombre")
    apellido = data.get("apellido")
    ci = data.get("ci")
    celular = data.get("celular") if "celular" in data else persona.celular
    email = data.get("email")
    username = data.get("username")
    password = data.get("contrasena") or data.get("password")

    if nombre is not None:
        nombre = str(nombre).strip()
        if not nombre:
            return jsonify({"error": "El nombre no puede estar vacío"}), 400
        persona.nombre = nombre[:80]
    if apellido is not None:
        apellido = str(apellido).strip()
        if not apellido:
            return jsonify({"error": "El apellido no puede estar vacío"}), 400
        persona.apellido = apellido[:80]
    if ci is not None:
        ci = str(ci).strip()
        if not ci:
            return jsonify({"error": "El CI no puede estar vacío"}), 400
        duplicado = Persona.query.filter(Persona.ci == ci, Persona.id_persona != persona.id_persona).first()
        if duplicado:
            return jsonify({"error": "Ese CI ya está registrado"}), 409
        persona.ci = ci[:20]
    if "celular" in data:
        persona.celular = (str(celular).strip()[:20] if celular else None)
    if email is not None:
        email = str(email).strip().lower()
        if email and "@" not in email:
            return jsonify({"error": "email inválido"}), 400
        if email:
            duplicado = Persona.query.filter(
                Persona.email.ilike(email),
                Persona.id_persona != persona.id_persona,
            ).first()
            if duplicado:
                return jsonify({"error": "Ese email ya está registrado"}), 409
        persona.email = email or None
    if username is not None:
        username = str(username).strip()
        if not username:
            return jsonify({"error": "El username no puede estar vacío"}), 400
        duplicado = Usuario.query.filter(
            Usuario.username.ilike(username),
            Usuario.id_usuario != user.id_usuario,
        ).first()
        if duplicado:
            return jsonify({"error": "Ese username ya está registrado"}), 409
        user.username = username[:50]
    if password:
        if len(str(password)) < 8:
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400
        user.contrasena = hash_password(str(password))

    try:
        if nuevo_rol and nuevo_rol != user.rol:
            _sync_rol_tablas(user, nuevo_rol)
            user.rol = nuevo_rol
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "No se pudo actualizar: el rol tiene registros relacionados (reservas, canchas, etc.)."
        }), 409
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error al actualizar usuario")
        return jsonify({"error": "No se pudo actualizar el usuario"}), 500

    db.session.refresh(user)
    db.session.refresh(persona)
    return jsonify(_serialize_user(user, persona)), 200


@admin_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
@require_auth(roles=["administrador"])
def delete_user(user_id):
    if g.current_user.id_usuario == user_id:
        return jsonify({"error": "No puedes eliminar tu propia cuenta"}), 400

    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    persona_id = user.id_persona
    try:
        Cliente.query.filter_by(id_usuario=user.id_usuario).delete(synchronize_session=False)
        Administrador.query.filter_by(id_usuario=user.id_usuario).delete(synchronize_session=False)
        Empleado.query.filter_by(id_usuario=user.id_usuario).update(
            {"id_usuario": None}, synchronize_session=False
        )
        db.session.delete(user)
        persona = db.session.get(Persona, persona_id)
        if persona:
            db.session.delete(persona)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "No se puede eliminar el usuario porque tiene registros relacionados (reservas u otros)."
        }), 409
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error al eliminar usuario")
        return jsonify({"error": "No se pudo eliminar el usuario"}), 500

    return jsonify({"message": "Usuario eliminado"}), 200
