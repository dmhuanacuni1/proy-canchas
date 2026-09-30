from extensions import db


class Cancha(db.Model):
    __tablename__ = "cancha"

    id_cancha = db.Column(db.Integer, primary_key=True)
    nombre_cancha = db.Column(db.String(80), nullable=False)
    tipo_deporte = db.Column(db.String(50), nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    ubicacion = db.Column(db.String(150))
    estado = db.Column(db.String(20), nullable=False, default="disponible")
    techada = db.Column(db.Boolean, nullable=False, default=False)
    superficie = db.Column(db.String(50))

    id_categoria = db.Column(
        db.Integer,
        db.ForeignKey("categoria.id_categoria"),
        nullable=False,
    )

    id_administrador = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_administrador"),
        nullable=False,
    )

    categoria = db.relationship("Categoria", lazy=True)

    def to_dict(self):
        nombre_categoria = (
            self.categoria.nombre if self.categoria else None
        )
        return {
            "id": self.id_cancha,
            "id_cancha": self.id_cancha,
            "nombre": self.nombre_cancha,
            "nombre_cancha": self.nombre_cancha,
            "deporte": self.tipo_deporte,
            "tipo_deporte": self.tipo_deporte,
            "precio_hora": float(self.precio_hora),
            "ubicacion": self.ubicacion,
            "estado": self.estado,
            "techada": bool(self.techada),
            "superficie": self.superficie,
            "id_categoria": self.id_categoria,
            "nombre_categoria": nombre_categoria,
            "categoria": nombre_categoria,
            "id_administrador": self.id_administrador,
        }
