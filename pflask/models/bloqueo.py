from extensions import db


class Bloqueo(db.Model):
    __tablename__ = "bloqueo"

    id_bloqueo = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activo")
    id_cancha = db.Column(
        db.Integer,
        db.ForeignKey("cancha.id_cancha", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    id_administrador = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_administrador", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {
            "id_bloqueo": self.id_bloqueo,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "hora_inicio": self.hora_inicio.strftime("%H:%M") if self.hora_inicio else None,
            "hora_fin": self.hora_fin.strftime("%H:%M") if self.hora_fin else None,
            "motivo": self.motivo,
            "estado": self.estado,
            "id_cancha": self.id_cancha,
            "id_administrador": self.id_administrador,
        }