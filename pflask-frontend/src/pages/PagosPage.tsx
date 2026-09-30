import { useEffect, useState } from "react";
import AppLayout from "../components/layout/AppLayout";
import { pagosService } from "../services/pagos";
import type { Pago, ReservaParaPago } from "../services/pagos";

const METODOS = [
  { value: "efectivo", label: "Efectivo" },
  { value: "tarjeta", label: "Tarjeta" },
  { value: "transferencia", label: "Transferencia" },
  { value: "qr", label: "QR" },
];

const ESTADOS = {
  pendiente: "Pendiente",
  pagado: "Pagado",
  reembolsado: "Reembolsado",
};

const ESTADO_CLASES = {
  pendiente: "pendiente",
  pagado: "pagado",
  reembolsado: "reembolsado",
};

const PagosPage = () => {
  const [pagos, setPagos] = useState<Pago[]>([]);
  const [reservas, setReservas] = useState<ReservaParaPago[]>([]);
  const [filtro, setFiltro] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  // Formulario nuevo pago
  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState({
    id_reserva: "",
    metodo_pago: "qr",
    monto: "",
  });
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");

  const cargar = async (estado = filtro) => {
    setCargando(true);
    setError("");
    try {
      const datos = await pagosService.listar({ estado: estado || undefined, detalle: true });
      setPagos(datos);
    } catch (e: any) {
      setError(e.response?.data?.error || "No se pudieron cargar los pagos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
    pagosService
      .listarReservasParaPago()
      .then(setReservas)
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const aplicarFiltro = (estado: string) => {
    setFiltro(estado);
    cargar(estado);
  };

  const totalMonto = pagos.reduce((acc, p) => acc + Number(p.monto || 0), 0);

  const cambiarEstado = async (id: number, estado: string) => {
    setError("");
    try {
      await pagosService.cambiarEstado(id, estado);
      await cargar();
    } catch (e: any) {
      setError(e.response?.data?.error || "No se pudo actualizar el estado.");
    }
  };

  const eliminarPago = async (id: number) => {
    if (!window.confirm("¿Eliminar este pago?")) return;
    setError("");
    try {
      await pagosService.eliminar(id);
      await cargar();
    } catch (e: any) {
      setError(e.response?.data?.error || "No se pudo eliminar el pago.");
    }
  };

  const seleccionarReserva = (id: string) => {
    const reserva = reservas.find((r) => String(r.id_reserva) === id);
    setForm((f) => ({
      ...f,
      id_reserva: id,
      monto: reserva ? String(reserva.monto_total ?? "") : f.monto,
    }));
  };

  const guardar = async (ev: React.FormEvent) => {
    ev.preventDefault();
    setGuardando(true);
    setMensaje("");
    setError("");
    try {
      const data = await pagosService.crear({
        id_reserva: Number(form.id_reserva),
        metodo_pago: form.metodo_pago,
        monto: Number(form.monto),
        estado_pago: "pendiente",
      });
      setMensaje(data.mensaje);
      setMostrarForm(false);
      setForm({ id_reserva: "", metodo_pago: "qr", monto: "" });
      await cargar();
    } catch (e: any) {
      setError(e.response?.data?.error || "No se pudo registrar el pago.");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <AppLayout title="Gestión de Pagos" subtitle="Pagos de reservas, pendientes y procesados">
      {/* Filtros y acciones */}
      <div
        className="panel"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          marginBottom: "20px",
        }}
      >
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {["", "pendiente", "pagado", "reembolsado"].map((estado) => (
            <button
              key={estado}
              className={filtro === estado ? "btn-primary btn-sm" : "btn-secondary btn-sm"}
              onClick={() => aplicarFiltro(estado)}
            >
              {estado === "" ? "Todos" : ESTADOS[estado as keyof typeof ESTADOS]}
            </button>
          ))}
        </div>
        <button className="btn-success" onClick={() => setMostrarForm((v) => !v)}>
          {mostrarForm ? "Cerrar" : "➕ Registrar pago"}
        </button>
      </div>

      {error && <div className="mensaje error">{error}</div>}
      {mensaje && <div className="mensaje success">{mensaje}</div>}

      {/* Formulario registrar pago */}
      {mostrarForm && (
        <div className="panel" style={{ marginBottom: "20px" }}>
          <div className="panel-head">
            <h3>Registrar nueva pago</h3>
            <span className="hint" style={{ margin: 0 }}>Asocia el pago a una reserva</span>
          </div>
          <form onSubmit={guardar}>
            <div className="form-row">
              <div className="form-group">
                <label>Reserva</label>
                <select
                  required
                  value={form.id_reserva}
                  onChange={(e) => seleccionarReserva(e.target.value)}
                >
                  <option value="">Selecciona una reserva</option>
                  {reservas.map((r) => (
                    <option key={r.id_reserva} value={r.id_reserva}>
                      #{r.id_reserva} · {r.cancha} · {r.cliente}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Método de pago</label>
                <select
                  value={form.metodo_pago}
                  onChange={(e) => setForm({ ...form, metodo_pago: e.target.value })}
                >
                  {METODOS.map((m) => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Monto (Bs)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={form.monto}
                  onChange={(e) => setForm({ ...form, monto: e.target.value })}
                />
              </div>
            </div>
            <button type="submit" className="btn-primary" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar pago"}
            </button>
          </form>
        </div>
      )}

      {/* Resumen */}
      <div className="grid mid" style={{ marginBottom: "20px" }}>
        <div className="panel">
          <h3>Pagos en la vista</h3>
          <div className="big-number">{pagos.length}</div>
        </div>
        <div className="panel">
          <h3>Total (Bs)</h3>
          <div className="big-number">
            {totalMonto.toLocaleString("es-BO", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>
        <div className="panel">
          <h3>Pendientes</h3>
          <div className="big-number">
            {pagos.filter((p) => p.estado_pago === "pendiente").length}
          </div>
        </div>
      </div>

      {/* Tabla */}
      {cargando ? (
        <div className="estado-vacio">Cargando pagos...</div>
      ) : pagos.length === 0 ? (
        <div className="estado-vacio">
          📭 No hay pagos {filtro ? `en estado ${filtro}` : "registrados"}.
        </div>
      ) : (
        <div className="panel">
          <div className="panel-head">
            <h3>Listado de pagos</h3>
            <span className="hint" style={{ margin: 0 }}>{pagos.length} registro(s)</span>
          </div>
          <div className="tabla-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Reserva</th>
                  <th>Cliente / Cancha</th>
                  <th>Fecha</th>
                  <th>Método</th>
                  <th>Monto</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pagos.map((p) => (
                  <tr key={p.id_pago}>
                    <td>{p.id_pago}</td>
                    <td>
                      #{p.id_reserva}
                      {p.reserva?.estado_reserva && (
                        <div className="hint">
                          {p.reserva.fecha_reserva?.slice(0, 10)}
                          {p.reserva.hora_inicio ? ` · ${p.reserva.hora_inicio.slice(0, 5)}` : ""}
                        </div>
                      )}
                    </td>
                    <td>
                      {p.reserva?.cliente || "-"}
                      {p.reserva?.cancha && (
                        <div className="hint">{p.reserva.cancha}</div>
                      )}
                    </td>
                    <td>
                      {p.fecha_pago
                        ? new Date(p.fecha_pago).toLocaleDateString("es-BO")
                        : "-"}
                    </td>
                    <td className="capitalize">{p.metodo_pago}</td>
                    <td>
                      Bs {Number(p.monto || 0).toLocaleString("es-BO", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </td>
                    <td>
                      <span className={`badge ${ESTADO_CLASES[p.estado_pago as keyof typeof ESTADO_CLASES] || ""}`}>
                        {ESTADOS[p.estado_pago as keyof typeof ESTADOS] || p.estado_pago}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: "6px" }}>
                        {p.estado_pago === "pendiente" && (
                          <button
                            className="btn-success btn-sm"
                            onClick={() => cambiarEstado(p.id_pago, "pagado")}
                          >
                            Pagado
                          </button>
                        )}
                        {p.estado_pago !== "reembolsado" && (
                          <button
                            className="btn-warning btn-sm"
                            onClick={() => cambiarEstado(p.id_pago, "reembolsado")}
                          >
                            Reembolsar
                          </button>
                        )}
                        <button className="btn-danger btn-sm" onClick={() => eliminarPago(p.id_pago)}>
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppLayout>
  );
};

export default PagosPage;