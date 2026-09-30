"""
Seed de datos de demostración con sentido para el complejo de canchas.
Ejecutar con el Python del venv del backend:

    pflask\\Scripts\\python.exe db\\seed_demo_data.py

- No toma acciones destructivas: solo INSERTa si las tablas están vacías
  (cancha, categoria, evento, reserva, pago). Si ya hay canchas, no hace nada.
- Respeta el trigger fn_calcular_monto_total (monto_total se calcula solo),
  el índice único ux_reserva_sin_choque y los CHECK de estado.
- Contraseñas demo: demo1234 (hash pbkdf2:sha256, igual que auth_service).
"""
import random
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pflask"))

import sqlalchemy as sa
from werkzeug.security import generate_password_hash

DB_URL = "postgresql://postgres:123456@localhost:5432/proyectoCanchas"
PWD = generate_password_hash("demo1234", method="pbkdf2:sha256")
HOY = date.today()
random.seed(42)


def main():
    engine = sa.create_engine(DB_URL)

    with engine.begin() as conn:
        existentes = conn.execute(sa.text("SELECT COUNT(*) FROM cancha")).scalar()
        if existentes:
            print(f"Ya hay {existentes} canchas: el seed no se ejecuta para no duplicar datos.")
            return

        # ---------------------------------------------------------- personas
        personas = [
            # (id, nombre, apellido, ci, celular, email)
            (5, "María", "Quispe Salazar", "6543210", "71234567", "maria.quispe@example.com"),
            (6, "Jorge", "Mamani Cruz", "7654321", "72345678", "jorge.mamani@example.com"),
            (7, "Lucía", "Vargas Poma", "8765432", "73456789", "lucia.vargas@example.com"),
            (8, "Diego", "Condori Ramos", "9876543", "74567890", "diego.condori@example.com"),
            (9, "Ana", "Flores Ticona", "1928374", "75678901", "ana.flores@example.com"),
            (10, "Pablo", "Rojas Nina", "2837465", "76789012", "pablo.rojas@example.com"),
            (11, "Rosa", "Aguilar Huamán", "3746584", "77890123", "rosa.aguilar@example.com"),
            (12, "Marco", "Pillco Apaza", "4657483", "78901234", "marco.pillco@example.com"),
            (13, "Elena", "Soto Valdez", "5748392", "79012345", "elena.soto@example.com"),
            (14, "Andrés", "Valencia Roque", "6859201", "70123456", "andres.valencia@example.com"),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO persona (id_persona, nombre, apellido, ci, celular, email)
                VALUES (:id, :nombre, :apellido, :ci, :celular, :email)
            """),
            [dict(id=i, nombre=n, apellido=a, ci=ci, celular=c, email=e)
             for i, n, a, ci, c, e in personas],
        )

        # usuarios demo (6 clientes, 3 empleados, 1 admin extra)
        usuarios = [
            (5, "cliente2", "cliente"),
            (6, "cliente3", "cliente"),
            (7, "cliente4", "cliente"),
            (8, "cliente5", "cliente"),
            (9, "cliente6", "cliente"),
            (10, "cliente7", "cliente"),
            (11, "empleado2", "empleado"),
            (12, "empleado3", "empleado"),
            (13, "empleado4", "empleado"),
            (14, "admin2", "administrador"),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO usuario (id_usuario, username, contrasena, rol, id_persona)
                VALUES (:id, :username, :pwd, :rol, :id)
            """),
            [dict(id=i, username=u, rol=r, pwd=PWD) for i, u, r in usuarios],
        )

        # clientes: existentes id 1,2; nuevos 3..8 (usuarios 5..10)
        clientes = [
            (3, 5, "Futbol", "2025-02-14"),
            (4, 6, "Tenis", "2025-05-03"),
            (5, 7, "Voleibol", "2025-08-21"),
            (6, 8, "Basquet", "2025-11-09"),
            (7, 9, "Futbol", "2026-01-17"),
            (8, 10, "Padel", "2026-03-28"),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO cliente (id_cliente, id_usuario, fecha_afiliacion, deporte_pref)
                VALUES (:id, :uid, :fecha, :deporte)
            """),
            [dict(id=i, uid=u, fecha=f, deporte=d) for i, u, d, f in clientes],
        )

        # empleados: existente id 1 (usuario 4); nuevos 2..4 (usuarios 11..13)
        empleados = [
            (2, 11, "Cajero", "Tarde", "2024-06-01", 2300.00),
            (3, 12, "Auxiliar de canchas", "Noche", "2025-02-10", 2100.00),
            (4, 13, "Mantenimiento", "Noche", "2025-07-15", 2200.00),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO empleado (id_empleado, id_usuario, cargo, turno_laboral,
                                      fecha_contratacion, salario, id_administrador)
                VALUES (:id, :uid, :cargo, :turno, :fecha, :salario, 1)
            """),
            [dict(id=i, uid=u, cargo=c, turno=t, fecha=f, salario=s)
             for i, u, c, t, f, s in empleados],
        )

        # segundo administrador para poder probar login admin demo
        conn.execute(
            sa.text("""
                INSERT INTO administrador (id_administrador, id_usuario, nivel_acceso,
                                           fecha_designado, area_responsabilidad)
                VALUES (2, 14, 'total', :fecha, 'Operaciones')
            """),
            {"fecha": HOY.isoformat()},
        )

        # ---------------------------------------------------------- categorías
        categorias = [
            (1, "Futbol", "Canchas de futbol 5, 7 y 11"),
            (2, "Tenis", "Canchas de tenis de polvo de ladrillo y laje"),
            (3, "Basquet", "Canchas de basquetbol techadas"),
            (4, "Voleibol", "Canchas de voleibol playa y césped"),
            (5, "Padel", "Canchas de pádel cerradas"),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO categoria (id_categoria, nombre, descripcion)
                VALUES (:id, :nombre, :desc)
            """),
            [dict(id=i, nombre=n, desc=d) for i, n, d in categorias],
        )

        # ---------------------------------------------------------- canchas
        canchas = [
            # id, nombre, deporte, precio, ubicacion, estado, techada, superficie, cat
            (1, "Cancha Central", "Futbol", 80.00, "Zona A", "disponible", False, "Cesped sintetico", 1),
            (2, "Cancha Norte", "Futbol", 60.00, "Zona A", "disponible", False, "Cesped sintetico", 1),
            (3, "Cancha Sur", "Futbol", 60.00, "Zona B", "mantenimiento", False, "Cesped sintetico", 1),
            (4, "Tenis 1", "Tenis", 45.00, "Zona C", "disponible", False, "Polvo de ladrillo", 2),
            (5, "Tenis 2", "Tenis", 45.00, "Zona C", "disponible", False, "Polvo de ladrillo", 2),
            (6, "Basquet A", "Basquet", 50.00, "Zona D", "disponible", True, "Madera", 3),
            (7, "Voleibol A", "Voleibol", 40.00, "Zona D", "disponible", False, "Arena", 4),
            (8, "Padel 1", "Padel", 70.00, "Zona E", "disponible", True, "Cesped sintetico", 5),
            (9, "Padel 2", "Padel", 70.00, "Zona E", "fuera_servicio", True, "Cesped sintetico", 5),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO cancha (id_cancha, nombre_cancha, tipo_deporte, precio_hora,
                                    ubicacion, estado, techada, superficie,
                                    id_categoria, id_administrador)
                VALUES (:id, :nombre, :deporte, :precio, :ubic, :estado, :techada,
                        :superficie, :cat, 1)
            """),
            [dict(id=i, nombre=n, deporte=d, precio=p, ubic=u, estado=e,
                  techada=t, superficie=s, cat=c)
             for i, n, d, p, u, e, t, s, c in canchas],
        )

        # ---------------------------------------------------------- eventos
        # offsets relativos a hoy para cubrir todos los días de la semana
        eventos = [
            # nombre, tipo, offset_dias, inicio, fin, cupo, organizador, cancha, desc
            ("Torneo Interescolar", "Torneo", -6, "09:00", "13:00", 32, "Municipalidad", 1, "Fase clasificatoria de escuelas de la zona."),
            ("Liga Departamental", "Liga", -2, "18:00", "21:00", 40, "Liga de Futbol", 1, "Fecha 8 de la liga local."),
            ("Noche de Padel", "Amistoso", -1, "19:00", "22:00", 16, "Club Padel Bol", 8, "Torneo relámpago iluminado."),
            ("Capacitación de Árbitros", "Capacitación", 1, "15:00", "18:00", 25, "Colegio de Árbitros", 6, "Curso de recertificación."),
            ("Torneo de Tenis", "Torneo", 2, "08:00", "12:00", 20, "Federación de Tenis", 4, "Abierto mensual por categorías."),
            ("Festival Deportivo", "Festival", 3, "10:00", "16:00", 60, "Comité Deportivo", 7, "Jornada familiar con muestras de cada deporte."),
            ("Entrenamiento Juvenil", "Entrenamiento", 4, "16:00", "18:00", 18, "Academia juvenil", 2, "Práctica sub-15 y sub-17."),
            ("Copa Municipal", "Torneo", 5, "09:00", "17:00", 48, "Municipalidad", 1, "Copa eliminatoria a domicilio de trofeo."),
            ("Clínica de Básquet", "Clínica", 6, "17:00", "19:30", 22, "Club Atenas", 6, "Taller de técnica individual."),
            ("Liga Universitaria", "Liga", 8, "18:30", "21:30", 36, "Universidad Mayor", 2, "Fixture inter-universitario."),
            ("Torneo Relámpago", "Torneo", 10, "14:00", "18:00", 24, "Club Local", 8, "Eliminación directa en parejas."),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO evento (id_evento, nombre_evento, tipo_evento, fecha_evento,
                                    hora_inicio, hora_fin, cupo_maximo, organizador,
                                    descripcion, id_cancha)
                VALUES (:id, :nombre, :tipo, :fecha, :inicio, :fin, :cupo,
                        :org, :desc, :cancha)
            """),
            [dict(id=i + 1, nombre=n, tipo=t, fecha=(HOY + timedelta(days=off)).isoformat(),
                  inicio=ini, fin=f, cupo=c, org=o, desc=d, cancha=ca)
             for i, (n, t, off, ini, f, c, o, ca, d) in enumerate(eventos)],
        )

        # ---------------------------------------------------------- reservas
        precios = {c[0]: c[3] for c in canchas}
        clientes_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        slots_usados = set()
        reservas = []
        rid = 1

        def nuevo_slot(cancha, fecha, dur_h):
            for _ in range(60):
                hora = random.choice([8, 9, 10, 11, 14, 15, 16, 17, 18, 19])
                inicio = time(hora, 0)
                fin = time(hora + dur_h, 0)
                clave = (cancha, fecha, inicio)
                if clave not in slots_usados:
                    slots_usados.add(clave)
                    return inicio, fin
            return None

        # 30 pasadas (últimas 6 semanas) + 14 futuras (próximas 2 semanas)
        planes = []
        for _ in range(30):
            offset = -random.randint(1, 42)
            planes.append(offset)
        for _ in range(14):
            offset = random.randint(1, 14)
            planes.append(offset)

        for offset in planes:
            fecha = HOY + timedelta(days=offset)
            cancha = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
            dur = random.choice([1, 2])
            slot = nuevo_slot(cancha, fecha, dur)
            if not slot:
                continue
            inicio, fin = slot
            cliente = random.choice(clientes_ids)
            es_pasada = offset < 0
            if es_pasada:
                estado = random.choices(["completada", "cancelada"], weights=[78, 22])[0]
            else:
                estado = random.choices(["confirmada", "pendiente"], weights=[70, 30])[0]
            motivo = None
            if estado == "cancelada":
                motivo = random.choice([
                    "Cancelada por el cliente",
                    "Lluvia",
                    "Problemas de agenda",
                    "Emergencia familiar",
                ])
            fecha_creacion = datetime.combine(
                fecha - timedelta(days=random.randint(1, 10)),
                time(random.randint(8, 20), random.choice([0, 15, 30, 45])),
            )
            reservas.append(dict(
                id=rid, fecha=fecha.isoformat(), inicio=inicio.strftime("%H:%M"),
                fin=fin.strftime("%H:%M"), duracion=f"{dur} hours",
                creacion=fecha_creacion.isoformat(timespec="seconds"),
                estado=estado, motivo=motivo, cliente=cliente, cancha=cancha,
            ))
            rid += 1

        conn.execute(
            sa.text("""
                INSERT INTO reserva (id_reserva, fecha_reserva, hora_inicio, hora_fin,
                                     duracion, fecha_creacion, estado_reserva,
                                     motivo_cancelacion, id_cliente, id_cancha, monto_total)
                VALUES (:id, :fecha, :inicio, :fin, :duracion, :creacion, :estado,
                        :motivo, :cliente, :cancha, NULL)
            """),
            reservas,
        )

        # monto_total lo calcula el trigger; leerlo para los pagos
        filas = conn.execute(sa.text("""
            SELECT id_reserva, fecha_reserva, hora_fin, estado_reserva, monto_total
            FROM reserva ORDER BY id_reserva
        """)).mappings().all()

        pagos = []
        pid = 1
        for r in filas:
            monto = float(r["monto_total"] or 0)
            if monto <= 0:
                monto = 50.0
            metodo = random.choice(["efectivo", "tarjeta", "transferencia", "qr"])
            emp = random.choice([1, 2, 3, 4])
            fecha_hora = datetime.combine(
                r["fecha_reserva"] + timedelta(days=random.choice([0, 0, -1])),
                time(random.randint(8, 20), random.choice([0, 20, 40])),
            )
            if r["estado_reserva"] == "completada":
                estado = "pagado"
            elif r["estado_reserva"] == "confirmada":
                estado = "pagado" if random.random() < 0.5 else "pendiente"
            elif r["estado_reserva"] == "pendiente":
                estado = "pendiente" if random.random() < 0.7 else None
            else:  # cancelada
                estado = "reembolsado" if random.random() < 0.2 else None
            if estado is None:
                continue
            comp = None if metodo == "efectivo" else f"REC-{pid:05d}"
            pagos.append(dict(
                id=pid, metodo=metodo, comp=comp, estado=estado,
                monto=monto, fecha=fecha_hora.isoformat(timespec="seconds"),
                reserva=r["id_reserva"], emp=emp,
            ))
            pid += 1

        # garantizar al menos 3 pagos pendientes (recordatorios del dashboard)
        pendientes = sum(1 for p in pagos if p["estado"] == "pendiente")
        if pendientes < 3:
            for p in pagos:
                if pendientes >= 3:
                    break
                if p["estado"] == "pagado" and p["fecha"][:10] >= HOY.isoformat():
                    p["estado"] = "pendiente"
                    pendientes += 1

        conn.execute(
            sa.text("""
                INSERT INTO pago (id_pago, metodo_pago, comprobante, estado_pago,
                                  monto, fecha_pago, id_reserva, id_empleado)
                VALUES (:id, :metodo, :comp, :estado, :monto, :fecha, :reserva, :emp)
            """),
            pagos,
        )

        # ---------------------------------------------------------- elige / supervisa
        elige = [
            (1, 1), (1, 8), (2, 4), (2, 5), (3, 7), (4, 6),
            (5, 2), (6, 1), (7, 8), (8, 9), (3, 1), (6, 6),
        ]
        conn.execute(
            sa.text("INSERT INTO elige (id_cliente, id_cancha) VALUES (:c, :k)"),
            [dict(c=c, k=k) for c, k in elige],
        )

        supervisas = [
            (1, 1, "2023-03-01"), (1, 3, "2023-03-01"), (1, 4, "2024-01-10"),
            (2, 1, "2024-06-01"), (2, 6, "2024-06-01"),
            (3, 4, "2025-02-10"), (3, 5, "2025-02-10"), (3, 8, "2025-02-10"),
            (4, 2, "2025-07-15"), (4, 7, "2025-07-15"), (4, 9, "2025-07-15"),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO supervisa (id_empleado, id_cancha, fecha_asignacion)
                VALUES (:e, :c, :f)
            """),
            [dict(e=e, c=c, f=f) for e, c, f in supervisas],
        )

        # ---------------------------------------------------------- secuencias
        for tabla, col in [
            ("persona", "id_persona"), ("usuario", "id_usuario"),
            ("cliente", "id_cliente"), ("empleado", "id_empleado"),
            ("administrador", "id_administrador"), ("categoria", "id_categoria"),
            ("cancha", "id_cancha"), ("evento", "id_evento"),
            ("reserva", "id_reserva"), ("pago", "id_pago"),
        ]:
            seq = conn.execute(sa.text(
                "SELECT pg_get_serial_sequence(:t, :c)"
            ), {"t": tabla, "c": col}).scalar()
            if seq:
                conn.execute(sa.text(
                    f"SELECT setval('{seq}', COALESCE((SELECT MAX({col}) FROM {tabla}), 1))"
                ))

    # resumen
    with engine.connect() as conn:
        print("=== Seed completado ===")
        for tabla in ["persona", "usuario", "cliente", "empleado", "categoria",
                      "cancha", "evento", "reserva", "pago", "elige", "supervisa"]:
            n = conn.execute(sa.text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            print(f"  {tabla}: {n}")
        resumen = conn.execute(sa.text("""
            SELECT estado_reserva, COUNT(*) FROM reserva GROUP BY estado_reserva ORDER BY 1
        """)).fetchall()
        print("  reservas por estado:", dict(resumen))
        resumen = conn.execute(sa.text("""
            SELECT estado_pago, COUNT(*) FROM pago GROUP BY estado_pago ORDER BY 1
        """)).fetchall()
        print("  pagos por estado:", dict(resumen))
        ingresos = conn.execute(sa.text(
            "SELECT COALESCE(SUM(monto),0) FROM pago WHERE estado_pago='pagado'"
        )).scalar()
        print(f"  ingresos pagados: Bs {float(ingresos):.2f}")


if __name__ == "__main__":
    main()