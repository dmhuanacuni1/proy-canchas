import smtplib
from email.message import EmailMessage


def _as_bool(value, default=False):
    if value is None or value == "":
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def smtp_is_configured(config):
    return bool(
        str(config.get("SMTP_HOST") or "").strip()
        and str(config.get("SMTP_USER") or "").strip()
        and str(config.get("SMTP_PASSWORD") or "").strip()
    )


def send_recovery_email(config, to_email, recover_url):
    host = str(config["SMTP_HOST"]).strip()
    port = int(config.get("SMTP_PORT") or 587)
    user = str(config["SMTP_USER"]).strip()
    password = str(config.get("SMTP_PASSWORD") or "").replace(" ", "")
    sender = str(config.get("SMTP_FROM") or user).strip() or user
    use_ssl = _as_bool(config.get("SMTP_USE_SSL"), default=(port == 465))
    use_tls = _as_bool(config.get("SMTP_USE_TLS"), default=True)

    msg = EmailMessage()
    msg["Subject"] = "Recuperar contraseña - Gestión de canchas"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        "Hola,\n\n"
        "Recibimos una solicitud para restablecer tu contraseña.\n"
        "Abre este enlace (válido por 1 hora):\n\n"
        f"{recover_url}\n\n"
        "Si no fuiste tú, ignora este correo.\n"
    )
    msg.add_alternative(
        f"""
        <div style="font-family:sans-serif;line-height:1.5">
          <p>Hola,</p>
          <p>Recibimos una solicitud para restablecer tu contraseña.</p>
          <p>
            <a href="{recover_url}" style="display:inline-block;padding:10px 16px;
               background:#007BFF;color:#fff;text-decoration:none;border-radius:4px">
              Crear nueva contraseña
            </a>
          </p>
          <p>El enlace caduca en 1 hora. Si no fuiste tú, ignora este correo.</p>
        </div>
        """,
        subtype="html",
    )

    if use_ssl:
        smtp = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        smtp = smtplib.SMTP(host, port, timeout=20)

    try:
        smtp.ehlo()
        if not use_ssl and use_tls:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)
    finally:
        try:
            smtp.quit()
        except Exception:
            smtp.close()
