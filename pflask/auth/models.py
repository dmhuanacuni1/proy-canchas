from extensions import db


class Persona(db.Model):
    __tablename__ = "persona"

    id_persona = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    ci = db.Column(db.String(20), nullable=False, unique=True)
    celular = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)


class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    id_persona = db.Column(
        db.Integer,
        db.ForeignKey("persona.id_persona", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    persona = db.relationship("Persona", backref=db.backref("usuario", uselist=False))


class Cliente(db.Model):
    __tablename__ = "cliente"

    id_cliente = db.Column(db.Integer, primary_key=True)
    fecha_afiliacion = db.Column(db.Date, nullable=False, server_default=db.text("CURRENT_DATE"))
    deporte_pref = db.Column(db.String(50))
    historial_reservas = db.Column(db.Text)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )


class Administrador(db.Model):
    __tablename__ = "administrador"

    id_administrador = db.Column(db.Integer, primary_key=True)
    nivel_acceso = db.Column(db.String(30), nullable=False)
    fecha_designado = db.Column(db.Date, nullable=False, server_default=db.text("CURRENT_DATE"))
    area_responsabilidad = db.Column(db.String(100))
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )


class Empleado(db.Model):
    __tablename__ = "empleado"

    id_empleado = db.Column(db.Integer, primary_key=True)
    cargo = db.Column(db.String(50), nullable=False)
    turno_laboral = db.Column(db.String(30))
    fecha_contratacion = db.Column(db.Date, nullable=False, server_default=db.text("CURRENT_DATE"))
    salario = db.Column(db.Numeric(10, 2), nullable=False)
    id_administrador = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"))
