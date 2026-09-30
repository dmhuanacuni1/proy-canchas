from extensions import db


class Reporte(db.Model):
    __tablename__ = "reporte"

    id_reporte = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)
    fecha_generado = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text)
    id_administrador = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_administrador"),
        nullable=False,
    )

    def to_dict(self):
        return {
            "id_reporte": self.id_reporte,
            "tipo": self.tipo,
            "fecha_generado": (
                self.fecha_generado.isoformat() if self.fecha_generado else None
            ),
            "descripcion": self.descripcion,
            "id_administrador": self.id_administrador,
        }