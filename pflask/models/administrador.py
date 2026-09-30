from extensions import db


class Administrador(db.Model):
    __tablename__ = "administrador"
    __table_args__ = {"extend_existing": True}

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