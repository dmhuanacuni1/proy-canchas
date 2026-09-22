import re
import secrets
from datetime import date

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from .email_service import send_recovery_email, smtp_is_configured
from .models import Cliente, Empleado, Persona, Usuario#añadir 'Empleado'
from .security import (
    create_reset_token,
    create_token,
    decode_token,
    frontend_role,
    hash_password,
    verify_password,
)

auth_bp = Blueprint("auth", __name__)


def _json():
    return request.get_json(silent=True) or {}


def _split_nombre(nombre_completo, apellido_explicit=None):
    parts = (nombre_completo or "").strip().split()
    nombre = parts[0] if parts else ""
    if apellido_explicit and str(apellido_explicit).strip():
        apellido = str(apellido_explicit).strip()
    else:
        apellido = " ".join(parts[1:]) if len(parts) > 1 else nombre
    return nombre[:80], apellido[:80]


def _unique_username(base):
    cleaned = re.sub(r"[^a-zA-Z0-9._]", "", (base or "").strip())[:40] or "usuario"
    candidate = cleaned
    n = 1
    while Usuario.query.filter_by(username=candidate).first():
        suffix = str(n)
        candidate = f"{cleaned[: 50 - len(suffix)]}{suffix}"
        n += 1
    return candidate


def _unique_ci(preferred=None):
    if preferred:
        existing = Persona.query.filter_by(ci=preferred).first()
        if not existing:
            return preferred[:20]
    for _ in range(20):
        ci = secrets.token_hex(8)[:20]
        if not Persona.query.filter_by(ci=ci).first():
            return ci
    raise RuntimeError("No se pudo generar un CI único")


def _serialize_user(user):
    persona = user.persona
    nombre_completo = (
        f"{persona.nombre} {persona.apellido}" if persona else user.username
    )
    
    # Obtener IDs de las tablas especializadas
    id_cliente = None
    id_administrador = None
    id_empleado = None
    
    if user.rol == "cliente":
        cliente = Cliente.query.filter_by(id_usuario=user.id_usuario).first()
        if cliente:
            id_cliente = cliente.id_cliente
    elif user.rol in ("administrador", "admin"):
        admin = Administrador.query.filter_by(id_usuario=user.id_usuario).first()
        if admin:
            id_administrador = admin.id_administrador
    elif user.rol == "empleado":
        emp = Empleado.query.filter_by(id_usuario=user.id_usuario).first()
        if emp:
            id_empleado = emp.id_empleado
    
    return {
        "id": user.id_usuario,
        "id_usuario": user.id_usuario,
        "username": user.username,
        "rol": user.rol,
        "role": frontend_role(user.rol),
        "email": persona.email if persona else None,
        "nombre": persona.nombre if persona else None,
        "apellido": persona.apellido if persona else None,
        "nombre_completo": nombre_completo,
        "id_cliente": id_cliente,
        "id_administrador": id_administrador,
        "id_empleado": id_empleado,
    }


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = _json()
    identifier = (data.get("email") or data.get("username") or "").strip()
    password = (data.get("contrasena") or data.get("password") or "").strip()

    if not identifier or not password:
        return jsonify({"error": "Se requiere username/email y contrasena"}), 400

    user = Usuario.query.filter(Usuario.username.ilike(identifier)).first()
    if not user:
        persona = Persona.query.filter(Persona.email.ilike(identifier)).first()
        if persona:
            user = Usuario.query.filter_by(id_persona=persona.id_persona).first()

    if not user or not verify_password(user.contrasena, password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if not user.contrasena.startswith(("pbkdf2:", "scrypt:", "argon2:")):
        user.contrasena = hash_password(password)
        db.session.commit()

    payload = _serialize_user(user)
    payload["token"] = create_token(user)
    return jsonify(payload), 200


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = _json()
    nombre_in = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("contrasena") or data.get("password") or ""
    apellido_in = data.get("apellido")
    ci_in = (data.get("ci") or "").strip() or None
    celular = (data.get("celular") or "").strip() or None
    username_in = (data.get("username") or "").strip() or None

    if not nombre_in or not email or not password:
        return jsonify({"error": "nombre, email y contrasena son obligatorios"}), 400
    if "@" not in email:
        return jsonify({"error": "email inválido"}), 400
    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    if Persona.query.filter(Persona.email.ilike(email)).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    nombre, apellido = _split_nombre(nombre_in, apellido_in)
    username_base = username_in or email.split("@")[0]
    username = _unique_username(username_base)

    try:
        persona = Persona(
            nombre=nombre,
            apellido=apellido,
            ci=_unique_ci(ci_in),
            celular=celular,
            email=email,
        )
        db.session.add(persona)
        db.session.flush()

        usuario = Usuario(
            username=username,
            contrasena=hash_password(password),
            rol="cliente",
            id_persona=persona.id_persona,
        )
        db.session.add(usuario)
        db.session.flush()

        cliente = Cliente(
            id_usuario=usuario.id_usuario,
            fecha_afiliacion=date.today(),
        )
        db.session.add(cliente)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se pudo registrar: datos duplicados"}), 409
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error en registro")
        return jsonify({"error": "No se pudo completar el registro"}), 500

    return jsonify({
        "message": "Usuario registrado",
        "user": _serialize_user(usuario),
    }), 201


@auth_bp.route("/auth/recover", methods=["POST"])
def recover():
    data = _json()
    email = (data.get("email") or "").strip()

    if not email:
        return jsonify({"error": "El email es obligatorio"}), 400

    persona = Persona.query.filter(Persona.email.ilike(email)).first()
    if persona:
        user = Usuario.query.filter_by(id_persona=persona.id_persona).first()
        if user:
            token = create_reset_token(user)
            frontend = current_app.config.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")
            recover_url = f"{frontend}/reset-password/{token}"
            destino = persona.email

            if smtp_is_configured(current_app.config):
                try:
                    send_recovery_email(current_app.config, destino, recover_url)
                    current_app.logger.info("Correo de recuperación enviado a %s", destino)
                except Exception:
                    current_app.logger.exception("No se pudo enviar el correo de recuperación")
                    return jsonify({
                        "error": "No se pudo enviar el correo. Revisa la configuración SMTP."
                    }), 500
            else:
                current_app.logger.warning(
                    "SMTP no configurado. URL de recuperación para %s: %s", destino, recover_url
                )
                print(f"[AUTH RECOVER] SMTP no configurado. {destino} -> {recover_url}")

    return jsonify({
        "message": "Si el correo está registrado, se envió un enlace de recuperación."
    }), 200


@auth_bp.route("/auth/reset", methods=["POST"])
def reset():
    data = _json()
    token = (data.get("token") or "").strip()
    password = data.get("contrasena") or data.get("password") or data.get("nueva_contrasena") or ""

    if not token or not password:
        return jsonify({"error": "token y contrasena son obligatorios"}), 400
    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    try:
        payload = decode_token(token, expected_type="reset")
    except Exception:
        return jsonify({"error": "El enlace es inválido o ha expirado"}), 400

    user = db.session.get(Usuario, int(payload["sub"]))
    if not user:
        return jsonify({"error": "El enlace es inválido o ha expirado"}), 400

    user.contrasena = hash_password(password)
    db.session.commit()
    return jsonify({"message": "Contraseña actualizada"}), 200
