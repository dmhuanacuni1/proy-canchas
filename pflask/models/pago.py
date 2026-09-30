from extensions import db


class Pago(db.Model):
    __tablename__ = "pago"

    id_pago = db.Column(db.Integer, primary_key=True)
    metodo_pago = db.Column(db.String(50), nullable=False)
    comprobante = db.Column(db.String(100))
    estado_pago = db.Column(db.String(20), nullable=False, default="pendiente")
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False)
    id_reserva = db.Column(
        db.Integer,
        db.ForeignKey("reserva.id_reserva"),
        nullable=False,
    )
    id_empleado = db.Column(
        db.Integer,
        db.ForeignKey("empleado.id_empleado"),
        nullable=True,
    )

    reserva = db.relationship("Reserva")
    empleado = db.relationship("Empleado")

    def to_dict(self):
        return {
            "id_pago": self.id_pago,
            "metodo_pago": self.metodo_pago,
            "comprobante": self.comprobante,
            "estado_pago": self.estado_pago,
            "monto": float(self.monto) if self.monto is not None else None,
            "fecha_pago": (
                self.fecha_pago.isoformat() if self.fecha_pago else None
            ),
            "id_reserva": self.id_reserva,
            "id_empleado": self.id_empleado,
        }