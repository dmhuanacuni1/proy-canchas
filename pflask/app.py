import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from extensions import db

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
CORS(app)


class Cancha(db.Model):
    __tablename__ = "cancha"
    id_cancha = db.Column(db.Integer, primary_key=True)
    nombre_cancha = db.Column(db.String(80), nullable=False)
    tipo_deporte = db.Column(db.String(50), nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    techada = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.String(20), nullable=False, default="disponible")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/canchas")
def get_canchas():
    canchas = Cancha.query.all()
    return jsonify([{
        "id": c.id_cancha,
        "nombre": c.nombre_cancha,
        "deporte": c.tipo_deporte,
        "precio_hora": float(c.precio_hora),
        "techada": c.techada,
        "estado": c.estado
    } for c in canchas])


# Ver auth/LEEME.txt
from auth import register_auth
register_auth(app)


if __name__ == "__main__":
    app.run(debug=True)
