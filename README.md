=========================
===== PARA INSTALAR =====
=========================

-En la carpeta pflask, con el entorno virtual activado, instala lo nuevo de esta rama:

pip install -r requirements.txt

(Eso instala PyJWT, que es lo unico extra respecto a lo que ya tenian. No hace falta npm install).

Reinicia Flask y el frontend como siempre.


====================================
===== PARA PROBAR LOS USUARIOS =====
====================================

-Si quieren probar los tres roles, ejecuten esto en PostgreSQL (un administrador, un cliente y un empleado). El empleado necesita un administrador, por eso el admin va primero.

INSERT INTO persona (nombre, apellido, ci, celular, email) VALUES 
('Juan', 'Perez', '1234567', '77712345', 'juan@example.com'), 
('Carlos', 'Lopez', '1122334', '77711223', 'carlos@example.com'), 
('Luis', 'Ramirez', '3344556', '77733445', 'luis@example.com');

INSERT INTO usuario (username, contrasena, rol, id_persona) VALUES 
('admin1', 'pass1', 'administrador', (SELECT id_persona FROM persona WHERE ci='1234567')), 
('cliente1', 'pass3', 'cliente', (SELECT id_persona FROM persona WHERE ci='1122334')), 
('empleado1', 'pass5', 'empleado', (SELECT id_persona FROM persona WHERE ci='3344556'));

INSERT INTO administrador (nivel_acceso, fecha_designado, area_responsabilidad, id_usuario) VALUES 
('total', '2024-01-01', 'General', (SELECT id_usuario FROM usuario WHERE username='admin1'));

INSERT INTO cliente (fecha_afiliacion, deporte_pref, historial_reservas, id_usuario) VALUES 
('2024-03-01', 'Futbol', 'Sin reservas', (SELECT id_usuario FROM usuario WHERE username='cliente1'));

INSERT INTO empleado (cargo, turno_laboral, fecha_contratacion, salario, id_administrador, id_usuario) VALUES 
('Mantenimiento', 'Manana', '2024-04-01', 2500.00, (SELECT id_administrador FROM administrador WHERE id_usuario=(SELECT id_usuario FROM usuario WHERE username='admin1')), (SELECT id_usuario FROM usuario WHERE username='empleado1'));


Para entrar:
Administrador: juan@example.com o admin1 / pass1 Cliente: carlos@example.com o cliente1 / pass3 Empleado: luis@example.com o empleado1 / pass5
El registro por la web solo crea clientes. El panel de editar y borrar usuarios sale con la cuenta de administrador.


=====================================================
===== Para probar la recuperacion de contraseña =====
=====================================================
-Recuperar contraseña no pide instalar nada mas. Usen un correo que exista en persona. El enlace aparece en la consola de Flask. Si quieren que llegue un Gmail de verdad, 

1. Crear el archivo pflask/auth/config/correo.env (si no existe).
2. Pegar exactamente este contenido en la carpeta correo.env:

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=canchasrecuperar@gmail.com
SMTP_PASSWORD=wwiy vadd ousl dmwd
SMTP_FROM=canchasrecuperar@gmail.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
FRONTEND_URL=http://localhost:5173
SECRET_KEY=dev-secret-canchas-local

3. Guardar y reiniciar Flask.








Iteracion: Gestion de Reservas
se modifico la base de datos por motivos de necesidad


-- =====================================================================
-- SCRIPT DE ACTUALIZACIÓN
-- Iteración: Gestión de Reservas
-- Ejecutar sobre la BD ya existente (NO recrea nada)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. CREAR TABLA BLOQUEO
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bloqueo (
    id_bloqueo       SERIAL PRIMARY KEY,
    fecha_inicio     DATE NOT NULL,
    fecha_fin        DATE NOT NULL,
    hora_inicio      TIME NOT NULL,
    hora_fin         TIME NOT NULL,
    motivo           TEXT NOT NULL,
    estado           VARCHAR(20) NOT NULL DEFAULT 'activo',
    id_cancha        INTEGER NOT NULL 
        REFERENCES cancha(id_cancha) ON DELETE CASCADE ON UPDATE CASCADE,
    id_administrador INTEGER NOT NULL 
        REFERENCES administrador(id_administrador) ON DELETE RESTRICT ON UPDATE CASCADE,
    fecha_creacion   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_bloqueo_horas  CHECK (hora_fin > hora_inicio),
    CONSTRAINT chk_bloqueo_fechas CHECK (fecha_fin >= fecha_inicio),
    CONSTRAINT chk_bloqueo_estado CHECK (estado IN ('activo', 'inactivo'))
);

CREATE INDEX IF NOT EXISTS idx_bloqueo_cancha_fecha 
    ON bloqueo (id_cancha, fecha_inicio, fecha_fin);

CREATE INDEX IF NOT EXISTS idx_bloqueo_estado 
    ON bloqueo (estado);

-- ---------------------------------------------------------------------
-- 2. ACTUALIZAR EL CHECK DE ESTADOS DE RESERVA
-- ---------------------------------------------------------------------
ALTER TABLE reserva DROP CONSTRAINT IF EXISTS chk_reserva_estado;

ALTER TABLE reserva ADD CONSTRAINT chk_reserva_estado 
    CHECK (estado_reserva IN (
        'pendiente', 
        'confirmada', 
        'cancelada', 
        'completada',
        'expirada'     
    ));

-- ---------------------------------------------------------------------
-- 3. ACTUALIZAR EL CHECK DE ESTADOS DE CANCHA
-- ---------------------------------------------------------------------
ALTER TABLE cancha DROP CONSTRAINT IF EXISTS chk_cancha_estado;

ALTER TABLE cancha ADD CONSTRAINT chk_cancha_estado 
    CHECK (estado IN ('disponible', 'fuera_servicio'));

-- Convertir cualquier cancha con estado antiguo 'mantenimiento' a 'disponible'
-- (los mantenimientos ahora son bloqueos con fecha de fin)
UPDATE cancha SET estado = 'disponible' WHERE estado = 'mantenimiento';

-- ---------------------------------------------------------------------
-- 4. ÍNDICES ADICIONALES PARA RESERVA
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_reserva_cancha_fecha 
    ON reserva (id_cancha, fecha_reserva);

CREATE INDEX IF NOT EXISTS idx_reserva_estado 
    ON reserva (estado_reserva);

CREATE INDEX IF NOT EXISTS idx_reserva_fecha_creacion 
    ON reserva (fecha_creacion);

-- =====================================================================
-- VERIFICACIÓN FINAL
-- =====================================================================
SELECT 
    table_name AS "Tabla",
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_name = t.table_name AND table_schema = 'public') AS "Columnas"
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name IN ('bloqueo', 'reserva', 'cancha', 'categoria', 'pago')
ORDER BY table_name;