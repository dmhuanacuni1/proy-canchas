"""
Módulo de autenticación y usuarios (sprint de inicio de sesión).

No editar app.py ni el resto de módulos de canchas/reservas desde aquí.
Las rutas públicas siguen siendo las mismas:
  POST /auth/login
  POST /auth/register
  POST /auth/recover
  POST /auth/reset
  GET    /admin/users
  PUT    /admin/users/<id>
  DELETE /admin/users/<id>
(también disponibles con prefijo /api/...)
"""
import os
from pathlib import Path

from .email_service import smtp_is_configured
from .admin_routes import admin_bp
from .routes import auth_bp


def register_auth(app):
    config_dir = Path(__file__).resolve().parent / "config"
    from dotenv import load_dotenv
    load_dotenv(config_dir / "correo.env")

    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_EXPIRES_HOURS"] = int(os.getenv("JWT_EXPIRES_HOURS", "12"))
    app.config["RESET_TOKEN_EXPIRES_SECONDS"] = int(
        os.getenv("RESET_TOKEN_EXPIRES_SECONDS", "3600")
    )
    app.config["FRONTEND_URL"] = os.getenv("FRONTEND_URL", "http://localhost:5173")
    app.config["SMTP_HOST"] = os.getenv("SMTP_HOST", "").strip()
    app.config["SMTP_PORT"] = os.getenv("SMTP_PORT", "587").strip()
    app.config["SMTP_USER"] = os.getenv("SMTP_USER", "").strip()
    app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD", "").strip()
    app.config["SMTP_FROM"] = os.getenv("SMTP_FROM", "").strip()
    app.config["SMTP_USE_TLS"] = os.getenv("SMTP_USE_TLS", "true").strip()
    app.config["SMTP_USE_SSL"] = os.getenv("SMTP_USE_SSL", "false").strip()

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp, url_prefix="/api", name="auth_api")
    app.register_blueprint(admin_bp, url_prefix="/api", name="admin_api")

    if smtp_is_configured(app.config):
        app.logger.info("SMTP configurado: los correos de recuperación se enviarán por email.")
    else:
        app.logger.warning(
            "SMTP no configurado. La recuperación de contraseña se imprimirá en la consola."
        )
