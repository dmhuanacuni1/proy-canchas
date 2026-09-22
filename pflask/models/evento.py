from extensions import db

class Evento(db.Model):
    __tablename__ = "evento"

    id_evento = db.Column(db.Integer, primary_key=True)
    nombre_evento = db.Column(db.String(100), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=True)
    fecha_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    cupo_maximo = db.Column(db.Integer, nullable=True)
    organizador = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    id_cancha = db.Column(db.Integer, db.ForeignKey("cancha.id_cancha"), nullable=False)

    # Relación unidireccional con la cancha donde se realiza el evento
    cancha = db.relationship("Cancha")

    def to_dict(self):
        return {
            "id_evento": self.id_evento,
            "nombre_evento": self.nombre_evento,
            "tipo_evento": self.tipo_evento,
            "fecha_evento": self.fecha_evento.isoformat() if self.fecha_evento else None,
            "hora_inicio": self.hora_inicio.strftime("%H:%M") if self.hora_inicio else None,
            "hora_fin": self.hora_fin.strftime("%H:%M") if self.hora_fin else None,
            "cupo_maximo": self.cupo_maximo,
            "organizador": self.organizador,
            "descripcion": self.descripcion,
            "id_cancha": self.id_cancha,
            "nombre_cancha": self.cancha.nombre_cancha if self.cancha else None
        }
