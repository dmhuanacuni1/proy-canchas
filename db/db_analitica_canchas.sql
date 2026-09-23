-- =====================================================================
-- EXTENSIONES: Analítica de Datos (ADAPTADO)
-- Ejecutar DESPUÉS de gestion_canchas.sql y db_extensiones_canchas.sql
-- NOTA: la seccion de % de ocupacion (fn_reporte_ocupacion) se OMITE
-- porque la tabla `horario_cancha` aun no existe en la BD.
-- =====================================================================

-- ---------------------------------------------------------------
-- 1. Monto de la reserva "congelado" al momento de crearla
ALTER TABLE reserva
    ADD COLUMN monto_total NUMERIC(10,2);

CREATE OR REPLACE FUNCTION fn_calcular_monto_total() RETURNS TRIGGER AS $$
BEGIN
    SELECT precio_hora * (EXTRACT(EPOCH FROM (NEW.hora_fin - NEW.hora_inicio)) / 3600.0)
    INTO NEW.monto_total
    FROM cancha
    WHERE id_cancha = NEW.id_cancha;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_4_calcular_monto_total
    BEFORE INSERT ON reserva
    FOR EACH ROW EXECUTE FUNCTION fn_calcular_monto_total();

-- Backfill de reservas que ya existían antes de esta columna
UPDATE reserva r
SET monto_total = c.precio_hora * (EXTRACT(EPOCH FROM r.duracion) / 3600.0)
FROM cancha c
WHERE c.id_cancha = r.id_cancha AND r.monto_total IS NULL;

-- fn_saldo_pendiente ahora usa el monto congelado, no el precio actual
CREATE OR REPLACE FUNCTION fn_saldo_pendiente(p_id_reserva INTEGER) RETURNS NUMERIC AS $$
DECLARE
    v_monto_total NUMERIC;
    v_pagado      NUMERIC;
BEGIN
    SELECT monto_total INTO v_monto_total FROM reserva WHERE id_reserva = p_id_reserva;

    SELECT COALESCE(SUM(monto), 0) INTO v_pagado
    FROM pago
    WHERE id_reserva = p_id_reserva AND estado_pago = 'pagado';

    RETURN v_monto_total - v_pagado;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------
-- 2. Índices para las agrupaciones que va a usar analítica
CREATE INDEX idx_pago_metodo   ON pago (metodo_pago);
CREATE INDEX idx_pago_fecha    ON pago (fecha_pago);
CREATE INDEX idx_reserva_estado ON reserva (estado_reserva);

-- ---------------------------------------------------------------
-- (Se omite fn_reporte_ocupacion: requiere tabla horario_cancha)

-- ---------------------------------------------------------------
-- 4. Vistas de apoyo
CREATE OR REPLACE VIEW vista_analitica_pagos AS
SELECT p.fecha_pago::DATE AS fecha,
       p.metodo_pago,
       COUNT(*)      AS cantidad_pagos,
       SUM(p.monto)  AS monto_total
FROM pago p
WHERE p.estado_pago = 'pagado'
GROUP BY p.fecha_pago::DATE, p.metodo_pago;

CREATE OR REPLACE VIEW vista_analitica_reservas AS
SELECT r.fecha_reserva,
       c.id_cancha,
       c.nombre_cancha,
       c.tipo_deporte,
       r.estado_reserva,
       COUNT(*) AS cantidad
FROM reserva r
JOIN cancha c ON c.id_cancha = r.id_cancha
GROUP BY r.fecha_reserva, c.id_cancha, c.nombre_cancha, c.tipo_deporte, r.estado_reserva;

CREATE OR REPLACE VIEW vista_analitica_clientes AS
SELECT cl.id_cliente,
       per.nombre || ' ' || per.apellido AS nombre_completo,
       COUNT(r.id_reserva) AS total_reservas,
       COALESCE(SUM(r.monto_total) FILTER (WHERE r.estado_reserva IN ('confirmada', 'completada')), 0) AS total_gastado,
       MIN(r.fecha_reserva) AS primera_reserva,
       MAX(r.fecha_reserva) AS ultima_reserva
FROM cliente cl
JOIN usuario u ON u.id_usuario = cl.id_usuario
JOIN persona per ON per.id_persona = u.id_persona
LEFT JOIN reserva r ON r.id_cliente = cl.id_cliente
GROUP BY cl.id_cliente, per.nombre, per.apellido;