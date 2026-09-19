import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)

# --- MODELO CANCHA (Ya lo tenías) ---
class Cancha(db.Model):
    __tablename__ = "cancha"
    id_cancha = db.Column(db.Integer, primary_key=True)
    nombre_cancha = db.Column(db.String(80), nullable=False)
    tipo_deporte = db.Column(db.String(50), nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    techada = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.String(20), nullable=False, default="disponible")

# --- NUEVO MODELO RESERVA ---
class Reserva(db.Model):
    __tablename__ = "reserva"
    id_reserva = db.Column(db.Integer, primary_key=True)
    fecha_reserva = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    estado_reserva = db.Column(db.String(20), nullable=False, default="pendiente")
    motivo_cancelacion = db.Column(db.Text)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_cancha = db.Column(db.Integer, db.ForeignKey('cancha.id_cancha'), nullable=False)
    
    # Relación para poder obtener los datos de la cancha si es necesario
    cancha = db.relationship('Cancha', backref='reservas')

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

# --- NUEVOS ENDPOINTS PARA RESERVAS ---

# 1. Crear una reserva (Validando choque de horarios)
@app.route("/api/reservas", methods=["POST"])
def crear_reserva():
    data = request.json
    
    # Validación básica de datos
    if not all(k in data for k in ("id_cancha", "fecha", "hora_inicio", "hora_fin")):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    # Convertir strings a objetos de fecha/hora de Python
    fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
    hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
    hora_fin = datetime.strptime(data["hora_fin"], "%H:%M").time()

    if hora_fin <= hora_inicio:
        return jsonify({"error": "La hora de fin debe ser mayor a la hora de inicio"}), 400

    # Lógica de choque de horarios (¡El núcleo de su iteración!)
    # Buscamos si hay alguna reserva que se cruce en la misma cancha y fecha
    choque = Reserva.query.filter(
        Reserva.id_cancha == data["id_cancha"],
        Reserva.fecha_reserva == fecha,
        Reserva.estado_reserva != 'cancelada', # Las canceladas no bloquean
        Reserva.hora_inicio < hora_fin,
        Reserva.hora_fin > hora_inicio
    ).first()

    if choque:
        return jsonify({"error": "La cancha ya está ocupada en ese horario. Por favor elija otro."}), 400

    # Si no hay choque, creamos la reserva
    # NOTA: id_cliente=1 está hardcodeado porque la gestión de usuarios es otra iteración
    nueva_reserva = Reserva(
        fecha_reserva=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        id_cancha=data["id_cancha"],
        id_cliente=1, 
        estado_reserva="pendiente"
    )
    
    db.session.add(nueva_reserva)
    db.session.commit()

    return jsonify({
        "mensaje": "Reserva creada exitosamente",
        "id_reserva": nueva_reserva.id_reserva
    }), 201


# 2. Obtener historial de reservas del cliente (simulado)
@app.route("/api/reservas/historial", methods=["GET"])
def historial_reservas():
    # Filtramos por el cliente 1 (simulado)
    reservas = Reserva.query.filter_by(id_cliente=1).order_by(Reserva.fecha_reserva.desc()).all()
    
    resultado = []
    for r in reservas:
        resultado.append({
            "id": r.id_reserva,
            "fecha": str(r.fecha_reserva),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "estado": r.estado_reserva,
            "motivo_cancelacion": r.motivo_cancelacion,
            "cancha": {
                "id": r.cancha.id_cancha,
                "nombre": r.cancha.nombre_cancha,
                "deporte": r.cancha.tipo_deporte
            }
        })
    return jsonify(resultado)


# 3. Cancelar una reserva
@app.route("/api/reservas/<int:id_reserva>/cancelar", methods=["PUT"])
def cancelar_reserva(id_reserva):
    data = request.json
    reserva = Reserva.query.get(id_reserva)

    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    if reserva.estado_reserva == 'cancelada':
        return jsonify({"error": "La reserva ya está cancelada"}), 400

    # Actualizamos el estado y guardamos el motivo
    reserva.estado_reserva = 'cancelada'
    reserva.motivo_cancelacion = data.get("motivo", "Cancelada por el usuario")
    
    db.session.commit()

    return jsonify({"mensaje": "Reserva cancelada exitosamente"})


if __name__ == "__main__":
    app.run(debug=True)