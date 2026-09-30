VALID_ROLES = ("cliente", "administrador", "empleado")


def validar_login(data):
    """Valida el cuerpo de POST /auth/login. Devuelve identifier y password."""
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    identifier = (data.get("email") or data.get("username") or "").strip()
    password = (data.get("contrasena") or data.get("password") or "").strip()

    if not identifier or not password:
        raise ValueError("Se requiere username/email y contrasena")

    return {"identifier": identifier, "password": password}


def validar_registro(data):
    """Valida el cuerpo de POST /auth/register. Devuelve datos limpios."""
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    nombre_in = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("contrasena") or data.get("password") or ""
    apellido_in = data.get("apellido")
    ci_in = (data.get("ci") or "").strip() or None
    celular = (data.get("celular") or "").strip() or None
    username_in = (data.get("username") or "").strip() or None

    if not nombre_in or not email or not password:
        raise ValueError("nombre, email y contrasena son obligatorios")
    if "@" not in email:
        raise ValueError("email inválido")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")

    return {
        "nombre": nombre_in,
        "apellido": apellido_in,
        "email": email,
        "password": password,
        "ci": ci_in,
        "celular": celular,
        "username": username_in,
    }


def validar_recuperacion(data):
    """Valida el cuerpo de POST /auth/recover. Devuelve el email."""
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    email = (data.get("email") or "").strip()

    if not email:
        raise ValueError("El email es obligatorio")

    return email


def validar_reset(data):
    """Valida el cuerpo de POST /auth/reset. Devuelve token y password."""
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    token = (data.get("token") or "").strip()
    password = data.get("contrasena") or data.get("password") or data.get("nueva_contrasena") or ""

    if not token or not password:
        raise ValueError("token y contrasena son obligatorios")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")

    return {"token": token, "password": str(password)}


def validar_rol(value):
    """Normaliza un nombre de rol desde el frontend ('admin', 'user', 'empleado', ...)."""
    if not value:
        return None
    key = str(value).strip().lower()
    FRONTEND_TO_DB = {
        "admin": "administrador",
        "user": "cliente",
        "empleado": "empleado",
        "administrador": "administrador",
        "cliente": "cliente",
    }
    return FRONTEND_TO_DB.get(key, key if key in VALID_ROLES else None)