from extensions import db


class Empleado(db.Model):
    __tablename__ = "empleado"

    id_empleado = db.Column(db.Integer, primary_key=True)
    cargo = db.Column(db.String(50), nullable=False)
    turno_laboral = db.Column(db.String(30))
    fecha_contratacion = db.Column(db.Date, nullable=False, server_default=db.text("CURRENT_DATE"))
    salario = db.Column(db.Numeric(10, 2), nullable=False)
    id_administrador = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"))