-- =====================================================================
-- EXTENSIONES ANALITICAS 2: TRIGGERS, FUNCIONES Y VISTAS DE
-- PRODUCTIVIDAD / REPORTES / SALDOS
-- Ejecutar DESPUÉS de db_analitica_canchas.sql (y del seed si se usa).
-- =====================================================================

-- ---------------------------------------------------------------
-- A. TRIGGERS AUTOMATIZADOS SOBRE `reserva`
-- ---------------------------------------------------------------

-- A.1 Duración de la reserva automática (si la app no la envía).
CREATE OR REPLACE FUNCTION fn_auto_duracion() RETURNS TRIGGER AS $$
BEGIN
    NEW.duracion := NEW.hora_fin - NEW.hora_inicio;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_1_auto_duracion ON reserva;
CREATE TRIGGER trg_1_auto_duracion
    BEFORE INSERT OR UPDATE OF hora_inicio, hora_fin ON reserva
    FOR EACH ROW EXECUTE FUNCTION fn_auto_duracion();

-- A.2 Estado por defecto y respaldo de fecha de creación.
CREATE OR REPLACE FUNCTION fn_defaults_reserva() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado_reserva IS NULL THEN
        NEW.estado_reserva := 'pendiente';
    END IF;
    IF NEW.fecha_creacion IS NULL THEN
        NEW.fecha_creacion := now();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_2_defaults_reserva ON reserva;
CREATE TRIGGER trg_2_defaults_reserva
    BEFORE INSERT ON reserva
    FOR EACH ROW EXECUTE FUNCTION fn_defaults_reserva();

-- A.3 Mantener el historial textual del cliente actualizado (cantidad + total).
CREATE OR REPLACE FUNCTION fn_historial_cliente() RETURNS TRIGGER AS $$
DECLARE
    v_cliente   INTEGER;
    v_total     INTEGER;
    v_gastado   NUMERIC;
BEGIN
    v_cliente := COALESCE(NEW.id_cliente, OLD.id_cliente);

    SELECT COUNT(*), COALESCE(SUM(monto_total), 0)
      INTO v_total, v_gastado
      FROM reserva
     WHERE id_cliente = v_cliente;

    UPDATE cliente
       SET historial_reservas = v_total || ' reservas; gasto total Bs ' || v_gastado
     WHERE id_cliente = v_cliente;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_3_historial_cliente ON reserva;
CREATE TRIGGER trg_3_historial_cliente
    AFTER INSERT OR UPDATE OR DELETE ON reserva
    FOR EACH ROW EXECUTE FUNCTION fn_historial_cliente();

-- A.4 Motivo por defecto al cancelar (evita cancelaciones "sin razón").
CREATE OR REPLACE FUNCTION fn_cancelacion_por_defecto() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado_reserva = 'cancelada' AND
       (NEW.motivo_cancelacion IS NULL OR NEW.motivo_cancelacion = '') THEN
        NEW.motivo_cancelacion := 'Cancelada por default del sistema';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_5_cancelacion_por_defecto ON reserva;
CREATE TRIGGER trg_5_cancelacion_por_defecto
    BEFORE UPDATE OF estado_reserva ON reserva
    FOR EACH ROW EXECUTE FUNCTION fn_cancelacion_por_defecto();

-- ---------------------------------------------------------------
-- B. TRIGGERS SOBRE `pago`
-- ---------------------------------------------------------------

-- B.1 Fecha de pago automática al confirmar un pago.
CREATE OR REPLACE FUNCTION fn_auto_fecha_pago() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado_pago = 'pagado' AND NEW.fecha_pago IS NULL THEN
        NEW.fecha_pago := now();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_6_auto_fecha_pago ON pago;
CREATE TRIGGER trg_6_auto_fecha_pago
    BEFORE INSERT OR UPDATE OF estado_pago ON pago
    FOR EACH ROW EXECUTE FUNCTION fn_auto_fecha_pago();

-- B.2 Referencia de comprobante auto-generada para cobros por ticket.
CREATE OR REPLACE FUNCTION fn_comprobante_auto() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.comprobante IS NULL OR NEW.comprobante = '' THEN
        NEW.comprobante := 'AUTO-' || to_char(now(), 'YYYYMMDD') || '-' || NEW.id_pago;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_7_comprobante_auto ON pago;
CREATE TRIGGER trg_7_comprobante_auto
    BEFORE INSERT ON pago
    FOR EACH ROW EXECUTE FUNCTION fn_comprobante_auto();

-- ---------------------------------------------------------------
-- C. VISTAS ANALÍTICAS NUEVAS
-- ---------------------------------------------------------------

-- C.1 Productividad de empleados (pagos procesados y recaudación).
CREATE OR REPLACE VIEW vista_analitica_empleados AS
SELECT e.id_empleado,
       per.nombre || ' ' || per.apellido AS nombre_empleado,
       e.cargo,
       e.turno_laboral,
       e.fecha_contratacion,
       e.salario,
       COUNT(p.id_pago) FILTER (WHERE p.estado_pago = 'pagado') AS pagos_procesados,
       COALESCE(SUM(p.monto) FILTER (WHERE p.estado_pago = 'pagado'), 0) AS total_recaudado,
       COALESCE(SUM(p.monto) FILTER (WHERE p.estado_pago = 'pendiente'), 0) AS por_cobrar
FROM empleado e
JOIN usuario u   ON u.id_usuario = e.id_usuario
JOIN persona per ON per.id_persona = u.id_persona
LEFT JOIN pago p ON p.id_empleado = e.id_empleado
GROUP BY e.id_empleado, per.nombre, per.apellido, e.cargo, e.turno_laboral,
         e.fecha_contratacion, e.salario;

-- C.2 Ganancias mensuales (ingresos vs por cobrar vs reembolsos).
CREATE OR REPLACE VIEW vista_ganancias_mensuales AS
SELECT date_trunc('month', fecha_pago)::date AS mes,
       COUNT(*) FILTER (WHERE estado_pago = 'pagado')   AS cantidad_pagados,
       COALESCE(SUM(monto) FILTER (WHERE estado_pago = 'pagado'), 0)   AS ingresos,
       COALESCE(SUM(monto) FILTER (WHERE estado_pago = 'pendiente'), 0) AS por_cobrar,
       COALESCE(SUM(monto) FILTER (WHERE estado_pago = 'reembolsado'), 0) AS reembolsos
FROM pago
GROUP BY 1
ORDER BY 1;

-- C.3 Saldo pendiente por cliente (comprometido - pagado).
CREATE OR REPLACE VIEW vista_saldos_clientes AS
SELECT cl.id_cliente,
       per.nombre || ' ' || per.apellido AS nombre_cliente,
       cl.fecha_afiliacion,
       COALESCE(SUM(r.monto_total), 0) AS total_comprometido,
       COALESCE((
           SELECT SUM(p.monto)
             FROM pago p
             JOIN reserva r2 ON r2.id_reserva = p.id_reserva
            WHERE r2.id_cliente = cl.id_cliente AND p.estado_pago = 'pagado'
       ), 0) AS total_pagado,
       COALESCE(SUM(r.monto_total), 0) - COALESCE((
           SELECT SUM(p.monto)
             FROM pago p
             JOIN reserva r2 ON r2.id_reserva = p.id_reserva
            WHERE r2.id_cliente = cl.id_cliente AND p.estado_pago = 'pagado'
       ), 0) AS saldo_pendiente
FROM cliente cl
JOIN usuario u   ON u.id_usuario = cl.id_usuario
JOIN persona per ON per.id_persona = u.id_persona
LEFT JOIN reserva r ON r.id_cliente = cl.id_cliente
GROUP BY cl.id_cliente, per.nombre, per.apellido, cl.fecha_afiliacion;

-- ---------------------------------------------------------------
-- D. FUNCIONES DE CONSULTA
-- ---------------------------------------------------------------

-- D.1 Resumen diario del complejo (reservas, horas, ingresos).
CREATE OR REPLACE FUNCTION fn_resumen_diario(p_fecha DATE)
RETURNS TABLE (
    total_reservas      BIGINT,
    horas_reservadas    INTERVAL,
    ingresos_pagados    NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)::BIGINT,
           COALESCE(SUM(r.hora_fin - r.hora_inicio), INTERVAL '0'),
           COALESCE((
               SELECT SUM(p.monto)
                 FROM pago p
                WHERE p.fecha_pago::DATE = p_fecha AND p.estado_pago = 'pagado'
           ), 0)
    FROM reserva r
    WHERE r.fecha_reserva = p_fecha;
END;
$$ LANGUAGE plpgsql;

-- D.2 Horas efectivas reservadas por cancha en un rango (para ocupación).
CREATE OR REPLACE FUNCTION fn_horas_cancha(
    p_id_cancha INTEGER, p_desde DATE, p_hasta DATE
)
RETURNS TABLE (
    fecha_dia          DATE,
    horas_reservadas   NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.fecha_reserva,
           COALESCE(SUM(
               EXTRACT(EPOCH FROM (r.hora_fin - r.hora_inicio)) / 3600.0
           ), 0)
    FROM reserva r
    WHERE r.id_cancha = p_id_cancha
      AND r.fecha_reserva BETWEEN p_desde AND p_hasta
      AND r.estado_reserva <> 'cancelada'
    GROUP BY r.fecha_reserva
    ORDER BY r.fecha_reserva;
END;
$$ LANGUAGE plpgsql;

-- D.3 Monto total comprometido vs pagado de una reserva (reutiliza el congelado).
CREATE OR REPLACE FUNCTION fn_estado_financiero_reserva(p_id_reserva INTEGER)
RETURNS TABLE (
    monto_total      NUMERIC,
    monto_pagado     NUMERIC,
    saldo_pendiente  NUMERIC,
    estado_reserva   VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.monto_total,
           COALESCE((
               SELECT SUM(p.monto)
                 FROM pago p
                WHERE p.id_reserva = r.id_reserva AND p.estado_pago = 'pagado'
           ), 0),
           r.monto_total - COALESCE((
               SELECT SUM(p.monto)
                 FROM pago p
                WHERE p.id_reserva = r.id_reserva AND p.estado_pago = 'pagado'
           ), 0),
           r.estado_reserva
    FROM reserva r
    WHERE r.id_reserva = p_id_reserva;
END;
$$ LANGUAGE plpgsql;