from extensions import db


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