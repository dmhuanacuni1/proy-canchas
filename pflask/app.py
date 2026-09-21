import os
import threading
import time
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["*"])

# ============================================================
# CONSTANTES DE NEGOCIO
# ============================================================
HORA_APERTURA = datetime.strptime("06:00", "%H:%M").time()
HORA_CIERRE = datetime.strptime("23:00", "%H:%M").time()

# ============================================================
# MODELOS (Eliminado Auditoria)
# ============================================================
class Persona(db.Model):
    __tablename__ = "persona"
    id_persona = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    ci = db.Column(db.String(20), nullable=False, unique=True)
    celular = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    id_persona = db.Column(db.Integer, nullable=False)

class Cliente(db.Model):
    __tablename__ = "cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False, unique=True)

class Administrador(db.Model):
    __tablename__ = "administrador"
    id_administrador = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False, unique=True)

class Empleado(db.Model):
    __tablename__ = "empleado"
    id_empleado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, unique=True)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)

class Cancha(db.Model):
    __tablename__ = "cancha"
    id_cancha = db.Column(db.Integer, primary_key=True)
    nombre_cancha = db.Column(db.String(80), nullable=False)
    tipo_deporte = db.Column(db.String(50), nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    techada = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.String(20), nullable=False, default="disponible")
    ubicacion = db.Column(db.String(150))
    superficie = db.Column(db.String(50))
    id_categoria = db.Column(db.Integer, nullable=False)
    id_administrador = db.Column(db.Integer, nullable=False)

class Reserva(db.Model):
    __tablename__ = "reserva"
    id_reserva = db.Column(db.Integer, primary_key=True)
    fecha_reserva = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    duracion = db.Column(db.Interval, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    estado_reserva = db.Column(db.String(20), nullable=False, default="pendiente")
    motivo_cancelacion = db.Column(db.Text, nullable=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_cancha = db.Column(db.Integer, nullable=False)

class Pago(db.Model):
    __tablename__ = "pago"
    id_pago = db.Column(db.Integer, primary_key=True)
    metodo_pago = db.Column(db.String(20), nullable=False)
    comprobante = db.Column(db.String(100))
    estado_pago = db.Column(db.String(20), nullable=False, default="pendiente")
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    id_reserva = db.Column(db.Integer, nullable=False)
    id_empleado = db.Column(db.Integer, nullable=True)

class Bloqueo(db.Model):
    __tablename__ = "bloqueo"
    id_bloqueo = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activo")
    id_cancha = db.Column(db.Integer, nullable=False)
    id_administrador = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

# ============================================================
# HELPERS
# ============================================================
def validar_horario(hora_inicio, hora_fin):
    if hora_inicio < HORA_APERTURA:
        return False, f"La hora de inicio debe ser después de las {HORA_APERTURA.strftime('%H:%M')}."
    if hora_fin > HORA_CIERRE:
        return False, f"La hora de fin debe ser antes de las {HORA_CIERRE.strftime('%H:%M')}."
    return True, None

def expirar_reservas_vencidas():
    """RF-12: Expira reservas pendientes con más de 15 min."""
    limite = datetime.now() - timedelta(minutes=15)
    vencidas = Reserva.query.filter(
        Reserva.estado_reserva == 'pendiente',
        Reserva.fecha_creacion < limite
    ).all()
    if vencidas:
        for r in vencidas:
            r.estado_reserva = 'expirada'
            r.motivo_cancelacion = 'Expirada por falta de pago (tiempo límite de 15 min)'
        db.session.commit()
    return len(vencidas)

def completar_reservas_pasadas():
    ahora = datetime.now()
    hoy = ahora.date()
    hora_actual = ahora.time()
    completadas = Reserva.query.filter(
        Reserva.estado_reserva == 'confirmada'
    ).filter(
        db.or_(
            Reserva.fecha_reserva < hoy,
            db.and_(Reserva.fecha_reserva == hoy, Reserva.hora_fin < hora_actual)
        )
    ).all()
    if completadas:
        for r in completadas:
            r.estado_reserva = 'completada'
        db.session.commit()
    return len(completadas)

def hay_bloqueo(id_cancha, fecha, hora_inicio, hora_fin):
    return Bloqueo.query.filter(
        Bloqueo.id_cancha == id_cancha,
        Bloqueo.estado == 'activo',
        Bloqueo.fecha_inicio <= fecha,
        Bloqueo.fecha_fin >= fecha,
        Bloqueo.hora_inicio < hora_fin,
        Bloqueo.hora_fin > hora_inicio
    ).first()

def background_worker():
    with app.app_context():
        while True:
            try:
                expirar_reservas_vencidas()
                completar_reservas_pasadas()
            except Exception as e:
                print(f"[WORKER ERROR] {str(e)}")
            time.sleep(60)

# ============================================================
# RUTAS
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
def login():
    datos = request.get_json()
    username = datos.get("username")
    contrasena = datos.get("contrasena")

    if not username or not contrasena:
        return jsonify({"error": "Usuario y contraseña son obligatorios."}), 400

    usuario = Usuario.query.filter_by(username=username, contrasena=contrasena).first()
    if not usuario:
        return jsonify({"error": "Usuario o contraseña incorrectos."}), 401

    persona = Persona.query.get(usuario.id_persona)
    nombre_completo = f"{persona.nombre} {persona.apellido}" if persona else usuario.username

    id_cliente = None
    id_administrador = None
    id_empleado = None

    if usuario.rol == "cliente":
        cliente = Cliente.query.filter_by(id_usuario=usuario.id_usuario).first()
        if cliente: id_cliente = cliente.id_cliente
    elif usuario.rol == "administrador":
        admin = Administrador.query.filter_by(id_usuario=usuario.id_usuario).first()
        if admin: id_administrador = admin.id_administrador
    elif usuario.rol == "empleado":
        emp = Empleado.query.filter_by(id_usuario=usuario.id_usuario).first()
        if emp: id_empleado = emp.id_empleado

    return jsonify({
        "id_usuario": usuario.id_usuario,
        "username": usuario.username,
        "rol": usuario.rol,
        "id_cliente": id_cliente,
        "id_administrador": id_administrador,
        "id_empleado": id_empleado,
        "nombre_completo": nombre_completo
    }), 200

@app.route("/api/canchas")
def get_canchas():
    canchas = db.session.query(Cancha, Categoria).outerjoin(
        Categoria, Cancha.id_categoria == Categoria.id_categoria
    ).all()
    return jsonify([{
        "id": c.id_cancha,
        "nombre": c.nombre_cancha,
        "deporte": c.tipo_deporte,
        "precio_hora": float(c.precio_hora),
        "techada": c.techada,
        "estado": c.estado,
        "ubicacion": c.ubicacion,
        "superficie": c.superficie,
        "id_categoria": c.id_categoria,
        "categoria": cat.nombre if cat else "Sin categoría"
    } for c, cat in canchas])

@app.route("/api/reservas", methods=["POST"])
def crear_reserva():
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    datos = request.get_json()

    try:
        id_cancha = int(datos["id_cancha"])
        id_cliente = int(datos["id_cliente"])
        fecha_str = datos["fecha_reserva"]
        hora_inicio_str = datos["hora_inicio"]
        duracion_horas = float(datos["duracion"])

        fecha_reserva = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()

        hoy = datetime.now().date()
        dias_diferencia = (fecha_reserva - hoy).days
        if dias_diferencia < 1 or dias_diferencia > 15:
            return jsonify({"error": "La fecha debe estar entre 1 y 15 días de anticipación."}), 400

        if duracion_horas < 1 or duracion_horas > 4:
            return jsonify({"error": "La duración debe ser entre 1 y 4 horas."}), 400

        hora_fin_dt = datetime.combine(fecha_reserva, hora_inicio) + timedelta(hours=duracion_horas)
        hora_fin = hora_fin_dt.time()

        ok, err = validar_horario(hora_inicio, hora_fin)
        if not ok: return jsonify({"error": err}), 400

        bloqueo = hay_bloqueo(id_cancha, fecha_reserva, hora_inicio, hora_fin)
        if bloqueo: return jsonify({"error": f"La cancha está bloqueada: {bloqueo.motivo}"}), 400

        choque = Reserva.query.filter(
            Reserva.id_cancha == id_cancha,
            Reserva.fecha_reserva == fecha_reserva,
            Reserva.estado_reserva.notin_(['cancelada', 'expirada', 'completada']),
            Reserva.hora_inicio < hora_fin,
            Reserva.hora_fin > hora_inicio
        ).first()
        if choque: return jsonify({"error": "La cancha no está disponible en ese horario."}), 400

        cancha = Cancha.query.get(id_cancha)
        if not cancha: return jsonify({"error": "Cancha no encontrada."}), 404

        monto_total = float(cancha.precio_hora) * duracion_horas

        nueva_reserva = Reserva(
            fecha_reserva=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion=timedelta(hours=duracion_horas),
            estado_reserva="pendiente",
            id_cliente=id_cliente,
            id_cancha=id_cancha
        )
        db.session.add(nueva_reserva)
        db.session.commit()

        return jsonify({
            "mensaje": "Reserva creada. Tienes 15 minutos para pagar antes de que expire.",
            "id_reserva": nueva_reserva.id_reserva,
            "monto_total": monto_total,
            "estado": "pendiente"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al procesar la reserva: {str(e)}"}), 500

@app.route("/api/empleado/reservas", methods=["POST"])
def crear_reserva_presencial():
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    datos = request.get_json()

    try:
        id_cancha = int(datos["id_cancha"])
        id_cliente = int(datos["id_cliente"])
        fecha_str = datos["fecha_reserva"]
        hora_inicio_str = datos["hora_inicio"]
        duracion_horas = float(datos["duracion"])
        metodo_pago = datos.get("metodo_pago", "efectivo")
        id_empleado = datos.get("id_empleado")

        if metodo_pago not in ("efectivo", "tarjeta", "transferencia", "qr"):
            return jsonify({"error": "Método de pago inválido."}), 400

        fecha_reserva = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()

        hoy = datetime.now().date()
        dias = (fecha_reserva - hoy).days
        if dias < 1 or dias > 15: return jsonify({"error": "La fecha debe estar entre 1 y 15 días de anticipación."}), 400
        if duracion_horas < 1 or duracion_horas > 4: return jsonify({"error": "La duración debe ser entre 1 y 4 horas."}), 400

        hora_fin_dt = datetime.combine(fecha_reserva, hora_inicio) + timedelta(hours=duracion_horas)
        hora_fin = hora_fin_dt.time()

        ok, err = validar_horario(hora_inicio, hora_fin)
        if not ok: return jsonify({"error": err}), 400

        bloqueo = hay_bloqueo(id_cancha, fecha_reserva, hora_inicio, hora_fin)
        if bloqueo: return jsonify({"error": f"La cancha está bloqueada: {bloqueo.motivo}"}), 400

        choque = Reserva.query.filter(
            Reserva.id_cancha == id_cancha,
            Reserva.fecha_reserva == fecha_reserva,
            Reserva.estado_reserva.notin_(['cancelada', 'expirada', 'completada']),
            Reserva.hora_inicio < hora_fin,
            Reserva.hora_fin > hora_inicio
        ).first()
        if choque: return jsonify({"error": "La cancha no está disponible en ese horario."}), 400

        cancha = Cancha.query.get(id_cancha)
        if not cancha: return jsonify({"error": "Cancha no encontrada."}), 404

        monto_total = float(cancha.precio_hora) * duracion_horas

        nueva_reserva = Reserva(
            fecha_reserva=fecha_reserva, hora_inicio=hora_inicio, hora_fin=hora_fin,
            duracion=timedelta(hours=duracion_horas), estado_reserva="confirmada",
            id_cliente=id_cliente, id_cancha=id_cancha
        )
        db.session.add(nueva_reserva)
        db.session.flush()

        nuevo_pago = Pago(
            metodo_pago=metodo_pago,
            comprobante=f"PRESENCIAL-{nueva_reserva.id_reserva}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            estado_pago="pagado", monto=monto_total,
            id_reserva=nueva_reserva.id_reserva, id_empleado=id_empleado
        )
        db.session.add(nuevo_pago)
        db.session.commit()

        return jsonify({
            "mensaje": "Reserva presencial creada y confirmada.",
            "id_reserva": nueva_reserva.id_reserva,
            "monto_total": monto_total, "estado": "confirmada", "metodo_pago": metodo_pago
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al procesar la reserva: {str(e)}"}), 500

@app.route("/api/reservas/<int:id_cliente>", methods=["GET"])
def get_reservas_cliente(id_cliente):
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    reservas = db.session.query(Reserva, Cancha).join(
        Cancha, Reserva.id_cancha == Cancha.id_cancha
    ).filter(Reserva.id_cliente == id_cliente).order_by(
        Reserva.fecha_reserva.desc(), Reserva.hora_inicio.desc()
    ).all()

    resultado = []
    for reserva, cancha in reservas:
        resultado.append({
            "id_reserva": reserva.id_reserva, "cancha": cancha.nombre_cancha,
            "id_cancha": cancha.id_cancha, "fecha": str(reserva.fecha_reserva),
            "hora_inicio": str(reserva.hora_inicio)[:5], "hora_fin": str(reserva.hora_fin)[:5],
            "duracion": str(reserva.duracion), "estado": reserva.estado_reserva,
            "precio_hora": float(cancha.precio_hora), "motivo_cancelacion": reserva.motivo_cancelacion
        })
    return jsonify(resultado)

@app.route("/api/reservas/<int:id_cliente>/vigentes", methods=["GET"])
def get_reservas_vigentes(id_cliente):
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    hoy = datetime.now().date()
    reservas = db.session.query(Reserva, Cancha).join(
        Cancha, Reserva.id_cancha == Cancha.id_cancha
    ).filter(
        Reserva.id_cliente == id_cliente,
        Reserva.fecha_reserva >= hoy,
        Reserva.estado_reserva.in_(['pendiente', 'confirmada'])
    ).order_by(Reserva.fecha_reserva.asc(), Reserva.hora_inicio.asc()).all()

    resultado = []
    for reserva, cancha in reservas:
        resultado.append({
            "id_reserva": reserva.id_reserva, "cancha": cancha.nombre_cancha,
            "id_cancha": cancha.id_cancha, "fecha": str(reserva.fecha_reserva),
            "hora_inicio": str(reserva.hora_inicio)[:5], "hora_fin": str(reserva.hora_fin)[:5],
            "duracion": str(reserva.duracion), "estado": reserva.estado_reserva,
            "precio_hora": float(cancha.precio_hora), "motivo_cancelacion": None
        })
    return jsonify(resultado)

@app.route("/api/reservas/<int:id_reserva>/cancelar", methods=["PUT"])
def cancelar_reserva(id_reserva):
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    reserva = Reserva.query.get(id_reserva)

    if not reserva: return jsonify({"error": "Reserva no encontrada."}), 404
    if reserva.estado_reserva in ("cancelada", "completada", "expirada"):
        return jsonify({"error": f"No se puede cancelar una reserva en estado '{reserva.estado_reserva}'."}), 400

    # User Story 2: Cancelar hasta 1 hora antes
    fecha_hora_reserva = datetime.combine(reserva.fecha_reserva, reserva.hora_inicio)
    if datetime.now() > (fecha_hora_reserva - timedelta(hours=1)):
        return jsonify({"error": "Solo se puede cancelar hasta 1 hora antes de la reserva."}), 400

    reserva.estado_reserva = "cancelada"
    reserva.motivo_cancelacion = "Cancelada por el cliente"
    
    # User Story 2: Simulación de reembolso
    pago = Pago.query.filter_by(id_reserva=id_reserva, estado_pago='pagado').first()
    if pago:
        pago.estado_pago = 'reembolsado'
        # Aquí iría la lógica real de la pasarela de pago para devolver el dinero

    db.session.commit()
    return jsonify({
        "mensaje": "Reserva cancelada exitosamente. Si realizó un pago, el reembolso ha sido procesado.",
        "id_reserva": reserva.id_reserva, "estado": "cancelada"
    }), 200

@app.route("/api/reservas/<int:id_reserva>/pagar", methods=["POST"])
def pagar_reserva(id_reserva):
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    datos = request.get_json()
    reserva = Reserva.query.get(id_reserva)

    if not reserva: return jsonify({"error": "Reserva no encontrada."}), 404
    if reserva.estado_reserva != "pendiente":
        return jsonify({"error": f"La reserva no está pendiente de pago (estado actual: '{reserva.estado_reserva}')."}), 400

    metodo = datos.get("metodo_pago")
    if metodo not in ("efectivo", "tarjeta", "transferencia", "qr"):
        return jsonify({"error": "Método de pago inválido."}), 400

    cancha = Cancha.query.get(reserva.id_cancha)
    duracion_horas = reserva.duracion.total_seconds() / 3600 if reserva.duracion else 1
    monto = float(cancha.precio_hora) * duracion_horas

    try:
        nuevo_pago = Pago(
            metodo_pago=metodo, comprobante=f"PAGO-{id_reserva}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            estado_pago="pagado", monto=monto, id_reserva=id_reserva
        )
        db.session.add(nuevo_pago)
        reserva.estado_reserva = "confirmada"
        db.session.commit()

        return jsonify({
            "mensaje": "Pago registrado. Reserva confirmada.",
            "id_pago": nuevo_pago.id_pago, "id_reserva": reserva.id_reserva,
            "monto_pagado": monto, "metodo_pago": metodo, "estado_reserva": "confirmada"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al procesar el pago: {str(e)}"}), 500

@app.route("/api/admin/reservas", methods=["GET"])
def get_todas_las_reservas():
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    filtro_fecha = request.args.get("fecha")
    filtro_estado = request.args.get("estado")
    filtro_cancha = request.args.get("id_cancha")

    query = db.session.query(Reserva, Cancha, Cliente, Persona).join(
        Cancha, Reserva.id_cancha == Cancha.id_cancha
    ).join(
        Cliente, Reserva.id_cliente == Cliente.id_cliente
    ).join(
        Usuario, Cliente.id_usuario == Usuario.id_usuario
    ).join(
        Persona, Usuario.id_persona == Persona.id_persona
    )

    if filtro_fecha: query = query.filter(Reserva.fecha_reserva == filtro_fecha)
    if filtro_estado: query = query.filter(Reserva.estado_reserva == filtro_estado)
    if filtro_cancha: query = query.filter(Reserva.id_cancha == int(filtro_cancha))

    reservas = query.order_by(Reserva.fecha_reserva.desc(), Reserva.hora_inicio.desc()).all()

    resultado = []
    for reserva, cancha, cliente, persona in reservas:
        resultado.append({
            "id_reserva": reserva.id_reserva, "cancha": cancha.nombre_cancha,
            "id_cancha": cancha.id_cancha, "cliente": f"{persona.nombre} {persona.apellido}",
            "id_cliente": cliente.id_cliente, "fecha": str(reserva.fecha_reserva),
            "hora_inicio": str(reserva.hora_inicio)[:5], "hora_fin": str(reserva.hora_fin)[:5],
            "duracion": str(reserva.duracion), "estado": reserva.estado_reserva,
            "motivo_cancelacion": reserva.motivo_cancelacion
        })
    return jsonify(resultado)

@app.route("/api/admin/reservas/<int:id_reserva>/cancelar-admin", methods=["PUT"])
def cancelar_reserva_admin(id_reserva):
    datos = request.get_json()
    motivo = datos.get("motivo", "Cancelada por administración")
    reserva = Reserva.query.get(id_reserva)
    if not reserva: return jsonify({"error": "Reserva no encontrada."}), 404
    if reserva.estado_reserva in ("cancelada", "completada", "expirada"):
        return jsonify({"error": f"No se puede cancelar una reserva en estado '{reserva.estado_reserva}'."}), 400

    reserva.estado_reserva = "cancelada"
    reserva.motivo_cancelacion = motivo
    db.session.commit()
    return jsonify({"mensaje": "Reserva cancelada por administración.", "id_reserva": reserva.id_reserva, "motivo": motivo}), 200

@app.route("/api/admin/reservas/<int:id_reserva>/modificar-admin", methods=["PUT"])
def modificar_reserva_admin(id_reserva):
    expirar_reservas_vencidas()
    completar_reservas_pasadas()
    datos = request.get_json()
    reserva = Reserva.query.get(id_reserva)

    if not reserva: return jsonify({"error": "Reserva no encontrada."}), 404
    if reserva.estado_reserva in ("cancelada", "completada", "expirada"):
        return jsonify({"error": f"No se puede modificar una reserva en estado '{reserva.estado_reserva}'."}), 400

    try:
        id_cancha = int(datos.get("id_cancha", reserva.id_cancha))
        nueva_fecha = datetime.strptime(datos["fecha_reserva"], "%Y-%m-%d").date()
        nueva_hora = datetime.strptime(datos["hora_inicio"], "%H:%M").time()
        nueva_duracion = float(datos["duracion"])

        hoy = datetime.now().date()
        dias = (nueva_fecha - hoy).days
        if dias < 1 or dias > 15: return jsonify({"error": "La nueva fecha debe estar entre 1 y 15 días de anticipación."}), 400
        if nueva_duracion < 1 or nueva_duracion > 4: return jsonify({"error": "La duración debe ser entre 1 y 4 horas."}), 400

        nueva_hora_fin = (datetime.combine(nueva_fecha, nueva_hora) + timedelta(hours=nueva_duracion)).time()
        ok, err = validar_horario(nueva_hora, nueva_hora_fin)
        if not ok: return jsonify({"error": err}), 400

        bloqueo = hay_bloqueo(id_cancha, nueva_fecha, nueva_hora, nueva_hora_fin)
        if bloqueo: return jsonify({"error": f"La cancha está bloqueada: {bloqueo.motivo}"}), 400

        choque = Reserva.query.filter(
            Reserva.id_cancha == id_cancha, Reserva.id_reserva != id_reserva,
            Reserva.fecha_reserva == nueva_fecha,
            Reserva.estado_reserva.notin_(['cancelada', 'expirada', 'completada']),
            Reserva.hora_inicio < nueva_hora_fin, Reserva.hora_fin > nueva_hora
        ).first()
        if choque: return jsonify({"error": "La cancha no está disponible en el nuevo horario."}), 400

        cancha_nueva = Cancha.query.get(id_cancha)
        if not cancha_nueva: return jsonify({"error": "Cancha no encontrada."}), 404

        reserva.id_cancha = id_cancha
        reserva.fecha_reserva = nueva_fecha
        reserva.hora_inicio = nueva_hora
        reserva.hora_fin = nueva_hora_fin
        reserva.duracion = timedelta(hours=nueva_duracion)
        db.session.commit()

        nuevo_monto = float(cancha_nueva.precio_hora) * nueva_duracion
        return jsonify({
            "mensaje": "Reserva modificada exitosamente", "id_reserva": reserva.id_reserva,
            "nuevo_monto": nuevo_monto, "nueva_fecha": str(reserva.fecha_reserva),
            "nueva_hora_inicio": str(reserva.hora_inicio)[:5], "nueva_hora_fin": str(reserva.hora_fin)[:5],
            "nueva_cancha": cancha_nueva.nombre_cancha, "id_cancha": cancha_nueva.id_cancha
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al modificar la reserva: {str(e)}"}), 500

@app.route("/api/clientes", methods=["GET"])
def get_clientes():
    clientes = db.session.query(Cliente, Persona).join(
        Usuario, Cliente.id_usuario == Usuario.id_usuario
    ).join(Persona, Usuario.id_persona == Persona.id_persona).all()
    return jsonify([{
        "id_cliente": c.id_cliente, "nombre_completo": f"{p.nombre} {p.apellido}",
        "ci": p.ci, "email": p.email
    } for c, p in clientes])

@app.route("/api/admin/clientes", methods=["POST"])
def crear_cliente():
    datos = request.get_json()
    try:
        nombre, apellido, ci = datos.get("nombre", "").strip(), datos.get("apellido", "").strip(), datos.get("ci", "").strip()
        celular, email = datos.get("celular", "").strip() or None, datos.get("email", "").strip() or None
        username, contrasena = datos.get("username", "").strip(), datos.get("contrasena", "").strip()

        if not all([nombre, apellido, ci, username, contrasena]):
            return jsonify({"error": "Nombre, apellido, CI, usuario y contraseña son obligatorios."}), 400
        if Persona.query.filter_by(ci=ci).first(): return jsonify({"error": f"Ya existe una persona con CI '{ci}'."}), 400
        if Usuario.query.filter_by(username=username).first(): return jsonify({"error": f"Ya existe un usuario con username '{username}'."}), 400

        nueva_persona = Persona(nombre=nombre, apellido=apellido, ci=ci, celular=celular, email=email)
        db.session.add(nueva_persona)
        db.session.flush()

        nuevo_usuario = Usuario(username=username, contrasena=contrasena, rol="cliente", id_persona=nueva_persona.id_persona)
        db.session.add(nuevo_usuario)
        db.session.flush()

        nuevo_cliente = Cliente(id_usuario=nuevo_usuario.id_usuario)
        db.session.add(nuevo_cliente)
        db.session.commit()

        return jsonify({
            "mensaje": "Cliente registrado exitosamente.", "id_cliente": nuevo_cliente.id_cliente,
            "nombre_completo": f"{nombre} {apellido}", "ci": ci, "email": email, "username": username
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al registrar cliente: {str(e)}"}), 500

@app.route("/api/bloqueos", methods=["GET"])
def get_bloqueos():
    solo_activos = request.args.get("activos", "true").lower() == "true"
    query = db.session.query(Bloqueo, Cancha).join(Cancha, Bloqueo.id_cancha == Cancha.id_cancha)
    if solo_activos: query = query.filter(Bloqueo.estado == 'activo')
    bloqueos = query.order_by(Bloqueo.fecha_inicio.desc()).all()
    return jsonify([{
        "id_bloqueo": b.id_bloqueo, "cancha": c.nombre_cancha, "id_cancha": c.id_cancha,
        "fecha_inicio": str(b.fecha_inicio), "fecha_fin": str(b.fecha_fin),
        "hora_inicio": str(b.hora_inicio)[:5], "hora_fin": str(b.hora_fin)[:5],
        "motivo": b.motivo, "estado": b.estado
    } for b, c in bloqueos])

@app.route("/api/admin/bloqueos", methods=["POST"])
def crear_bloqueo():
    datos = request.get_json()
    try:
        id_cancha, id_administrador = int(datos["id_cancha"]), int(datos["id_administrador"])
        fecha_inicio, fecha_fin = datetime.strptime(datos["fecha_inicio"], "%Y-%m-%d").date(), datetime.strptime(datos["fecha_fin"], "%Y-%m-%d").date()
        hora_inicio, hora_fin = datetime.strptime(datos["hora_inicio"], "%H:%M").time(), datetime.strptime(datos["hora_fin"], "%H:%M").time()
        motivo = datos["motivo"]

        if fecha_fin < fecha_inicio: return jsonify({"error": "La fecha fin no puede ser antes que la fecha inicio."}), 400
        if hora_fin <= hora_inicio: return jsonify({"error": "La hora fin debe ser mayor que la hora inicio."}), 400
        if not motivo or not motivo.strip(): return jsonify({"error": "El motivo del bloqueo es obligatorio."}), 400

        ok, err = validar_horario(hora_inicio, hora_fin)
        if not ok: return jsonify({"error": err}), 400

        if not Cancha.query.get(id_cancha): return jsonify({"error": "Cancha no encontrada."}), 404

        nuevo_bloqueo = Bloqueo(
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, hora_inicio=hora_inicio,
            hora_fin=hora_fin, motivo=motivo.strip(), estado="activo",
            id_cancha=id_cancha, id_administrador=id_administrador
        )
        db.session.add(nuevo_bloqueo)
        db.session.commit()
        return jsonify({"mensaje": "Bloqueo registrado exitosamente", "id_bloqueo": nuevo_bloqueo.id_bloqueo}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear bloqueo: {str(e)}"}), 500

@app.route("/api/admin/bloqueos/<int:id_bloqueo>", methods=["DELETE"])
def eliminar_bloqueo(id_bloqueo):
    bloqueo = Bloqueo.query.get(id_bloqueo)
    if not bloqueo: return jsonify({"error": "Bloqueo no encontrado."}), 404
    bloqueo.estado = "inactivo"
    db.session.commit()
    return jsonify({"mensaje": "Bloqueo desactivado exitosamente", "id_bloqueo": bloqueo.id_bloqueo}), 200

@app.route("/api/categorias", methods=["GET"])
def get_categorias():
    cats = Categoria.query.order_by(Categoria.nombre).all()
    return jsonify([{"id_categoria": c.id_categoria, "nombre": c.nombre, "descripcion": c.descripcion} for c in cats])

@app.route("/api/admin/categorias", methods=["POST"])
def crear_categoria():
    datos = request.get_json()
    try:
        nombre, descripcion = datos.get("nombre", "").strip(), datos.get("descripcion", "").strip() or None
        if not nombre: return jsonify({"error": "El nombre es obligatorio."}), 400
        if Categoria.query.filter_by(nombre=nombre).first(): return jsonify({"error": f"Ya existe una categoría '{nombre}'."}), 400
        nueva = Categoria(nombre=nombre, descripcion=descripcion)
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"mensaje": "Categoría creada exitosamente", "id_categoria": nueva.id_categoria}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear categoría: {str(e)}"}), 500

@app.route("/api/admin/categorias/<int:id_categoria>", methods=["PUT"])
def editar_categoria(id_categoria):
    datos = request.get_json()
    cat = Categoria.query.get(id_categoria)
    if not cat: return jsonify({"error": "Categoría no encontrada."}), 404
    try:
        nombre, descripcion = datos.get("nombre", "").strip(), datos.get("descripcion", "").strip() or None
        if not nombre: return jsonify({"error": "El nombre es obligatorio."}), 400
        existente = Categoria.query.filter_by(nombre=nombre).first()
        if existente and existente.id_categoria != id_categoria: return jsonify({"error": f"Ya existe otra categoría con ese nombre."}), 400
        cat.nombre = nombre
        cat.descripcion = descripcion
        db.session.commit()
        return jsonify({"mensaje": "Categoría actualizada", "id_categoria": cat.id_categoria}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al editar categoría: {str(e)}"}), 500

@app.route("/api/admin/categorias/<int:id_categoria>", methods=["DELETE"])
def eliminar_categoria(id_categoria):
    cat = Categoria.query.get(id_categoria)
    if not cat: return jsonify({"error": "Categoría no encontrada."}), 404
    if Cancha.query.filter_by(id_categoria=id_categoria).count() > 0:
        return jsonify({"error": f"No se puede eliminar: hay canchas con esta categoría."}), 400
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"mensaje": "Categoría eliminada"}), 200

@app.route("/api/admin/canchas", methods=["POST"])
def crear_cancha():
    datos = request.get_json()
    try:
        nombre, tipo_deporte = datos.get("nombre_cancha", "").strip(), datos.get("tipo_deporte", "").strip()
        precio_hora, techada = float(datos.get("precio_hora", 0)), bool(datos.get("techada", False))
        ubicacion, superficie = datos.get("ubicacion", "").strip() or None, datos.get("superficie", "").strip() or None
        id_categoria, id_administrador = int(datos.get("id_categoria")), int(datos.get("id_administrador"))

        if not all([nombre, tipo_deporte]): return jsonify({"error": "Nombre y tipo de deporte son obligatorios."}), 400
        if precio_hora <= 0: return jsonify({"error": "El precio por hora debe ser mayor a 0."}), 400
        if not Categoria.query.get(id_categoria): return jsonify({"error": "Categoría no encontrada."}), 404

        nueva = Cancha(
            nombre_cancha=nombre, tipo_deporte=tipo_deporte, precio_hora=precio_hora,
            techada=techada, estado="disponible", ubicacion=ubicacion, superficie=superficie,
            id_categoria=id_categoria, id_administrador=id_administrador
        )
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"mensaje": "Cancha creada exitosamente", "id_cancha": nueva.id_cancha}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear cancha: {str(e)}"}), 500

@app.route("/api/admin/canchas/<int:id_cancha>", methods=["PUT"])
def editar_cancha(id_cancha):
    datos = request.get_json()
    cancha = Cancha.query.get(id_cancha)
    if not cancha: return jsonify({"error": "Cancha no encontrada."}), 404
    try:
        cancha.nombre_cancha = datos.get("nombre_cancha", cancha.nombre_cancha).strip()
        cancha.tipo_deporte = datos.get("tipo_deporte", cancha.tipo_deporte).strip()
        precio = datos.get("precio_hora")
        if precio is not None:
            precio_f = float(precio)
            if precio_f <= 0: return jsonify({"error": "El precio debe ser mayor a 0."}), 400
            cancha.precio_hora = precio_f
        if "techada" in datos: cancha.techada = bool(datos["techada"])
        if "ubicacion" in datos: cancha.ubicacion = datos["ubicacion"].strip() or None
        if "superficie" in datos: cancha.superficie = datos["superficie"].strip() or None
        if "estado" in datos:
            if datos["estado"] not in ("disponible", "mantenimiento", "fuera_servicio"):
                return jsonify({"error": "Estado inválido."}), 400
            cancha.estado = datos["estado"]
        if "id_categoria" in datos:
            id_cat = int(datos["id_categoria"])
            if not Categoria.query.get(id_cat): return jsonify({"error": "Categoría no encontrada."}), 404
            cancha.id_categoria = id_cat

        db.session.commit()
        return jsonify({"mensaje": "Cancha actualizada", "id_cancha": cancha.id_cancha}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al editar cancha: {str(e)}"}), 500

@app.route("/api/admin/canchas/<int:id_cancha>", methods=["DELETE"])
def eliminar_cancha(id_cancha):
    cancha = Cancha.query.get(id_cancha)
    if not cancha: return jsonify({"error": "Cancha no encontrada."}), 404
    hoy = datetime.now().date()
    reservas_activas = Reserva.query.filter(
        Reserva.id_cancha == id_cancha, Reserva.fecha_reserva >= hoy,
        Reserva.estado_reserva.in_(['pendiente', 'confirmada'])
    ).count()
    if reservas_activas > 0: return jsonify({"error": f"No se puede eliminar: hay {reservas_activas} reserva(s) activas."}), 400
    cancha.estado = "fuera_servicio"
    db.session.commit()
    return jsonify({"mensaje": "Cancha desactivada (fuera de servicio)"}), 200

if __name__ == "__main__":
    worker = threading.Thread(target=background_worker, daemon=True)
    worker.start()
    print("🚀 Scheduler automático iniciado (cada 60s)")
    app.run(debug=True, use_reloader=False)