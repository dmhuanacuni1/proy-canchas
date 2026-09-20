from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from .models import Usuario

ROLE_TO_FRONTEND = {
    "administrador": "admin",
    "cliente": "user",
    "empleado": "empleado",
}


def hash_password(plain_password):
    return generate_password_hash(plain_password, method="pbkdf2:sha256")


def verify_password(stored, plain_password):
    if not stored or not plain_password:
        return False
    stored = stored.strip() if isinstance(stored, str) else stored
    plain_password = plain_password.strip() if isinstance(plain_password, str) else plain_password
    if stored.startswith(("pbkdf2:", "scrypt:", "argon2:")):
        return check_password_hash(stored, plain_password)
    return stored == plain_password


def frontend_role(rol):
    return ROLE_TO_FRONTEND.get(rol, rol)


def create_token(user, token_type="access", expires_delta=None):
    if expires_delta is None:
        hours = int(current_app.config.get("JWT_EXPIRES_HOURS", 12))
        expires_delta = timedelta(hours=hours)

    payload = {
        "sub": str(user.id_usuario),
        "rol": user.rol,
        "username": user.username,
        "type": token_type,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def create_reset_token(user):
    seconds = int(current_app.config.get("RESET_TOKEN_EXPIRES_SECONDS", 3600))
    return create_token(user, token_type="reset", expires_delta=timedelta(seconds=seconds))


def decode_token(token, expected_type="access"):
    payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Tipo de token inválido")
    return payload


def _extract_bearer_token():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return header.split(" ", 1)[1].strip() or None


def require_auth(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _extract_bearer_token()
            if not token:
                return jsonify({"error": "No autenticado"}), 401
            try:
                payload = decode_token(token, expected_type="access")
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token inválido"}), 401

            user = db.session.get(Usuario, int(payload["sub"]))
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 401
            if roles and user.rol not in roles:
                return jsonify({"error": "No autorizado"}), 403

            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
