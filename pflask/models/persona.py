from extensions import db


class Persona(db.Model):
    __tablename__ = "persona"

    id_persona = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    ci = db.Column(db.String(20), nullable=False, unique=True)
    celular = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)