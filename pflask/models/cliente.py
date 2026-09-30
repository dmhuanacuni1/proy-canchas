from extensions import db


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