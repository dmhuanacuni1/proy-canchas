import { useState } from "react";
import AppLayout from "../components/layout/AppLayout";
import { reportesService } from "../services/reportes";

const TIPOS = [
  { value: "reservas", label: "📋 Reservas por cancha" },
  { value: "ocupacion", label: "📈 Ocupación por cancha" },
  { value: "ingresos", label: "💰 Ingresos por cancha" },
];

const ReportesPage = () => {
  const [tipo, setTipo] = useState("reservas");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [filas, setFilas] = useState([]);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  const [generado, setGenerado] = useState(false);

  const generar = async () => {
    setError("");
    setFilas([]);
    setGenerado(false);

    if (!fechaInicio || !fechaFin) {
      setError("Debe indicar fecha inicio y fecha fin.");
      return;
    }
    if (fechaInicio > fechaFin) {
      setError("La fecha de inicio no puede ser mayor que la fecha fin.");
      return;
    }

    setCargando(true);
    try {
      const data = await reportesService.obtener(tipo, fechaInicio, fechaFin);
      setFilas(data.filas || []);
      setGenerado(true);
    } catch (e) {
      setError(e.response?.data?.error || "No se pudo generar el reporte.");
    } finally {
      setCargando(false);
    }
  };

  const encabezados = filas.length > 0 ? Object.keys(filas[0]) : [];

  return (
    <AppLayout title="Gestión de Reportes" subtitle="Reportes, ocupación e ingresos con exportación">
      <div className="grid mid">
        <div className="panel">
          <div className="panel-head">
            <h3>Filtros del reporte</h3>
            <span className="hint" style={{ margin: 0 }}>Selecciona tipo y rango</span>
          </div>

          <div className="form-group">
            <label>Tipo de informe</label>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
              {TIPOS.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Fecha inicio</label>
              <input
                type="date"
                value={fechaInicio}
                onChange={(e) => setFechaInicio(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Fecha fin</label>
              <input
                type="date"
                value={fechaFin}
                onChange={(e) => setFechaFin(e.target.value)}
              />
            </div>
          </div>

          <button
            className="btn-primary"
            onClick={generar}
            disabled={cargando}
            style={{ width: "100%" }}
          >
            {cargando ? "Generando..." : "🔍 Generar reporte"}
          </button>

          {error && <div className="mensaje error">{error}</div>}
        </div>

        <div className="panel">
          <div className="panel-head">
            <h3>Información</h3>
            <span className="hint" style={{ margin: 0 }}>Disponible para administradores</span>
          </div>
          <ul style={{ paddingLeft: "20px", margin: 0, fontSize: "14px", lineHeight: 1.8 }}>
            <li><b>Reservas por cancha:</b> total, confirmadas, completadas, pendientes y canceladas.</li>
            <li><b>Ocupación por cancha:</b> horas reservadas vs. disponibles (jornada 06:00–23:00).</li>
            <li><b>Ingresos por cancha:</b> pagos, ingresos, pendientes y reembolsos.</li>
            <li>Exporta el resultado en <b>PDF</b> o <b>Excel</b>.</li>
          </ul>
        </div>
      </div>

      {generado && filas.length === 0 && (
        <div className="estado-vacio">
          📭 No se encontraron datos en el rango seleccionado.
        </div>
      )}

      {filas.length > 0 && (
        <div className="panel" style={{ marginTop: "20px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "10px",
              marginBottom: "12px",
            }}
          >
            <div>
              <h3 style={{ margin: 0 }}>
                Resultado ({filas.length} registro{filas.length === 1 ? "" : "s"})
              </h3>
              <span className="hint">
                {fechaInicio} a {fechaFin}
              </span>
            </div>
            <div className="acciones">
              <a
                href={reportesService.urlExportar(tipo, fechaInicio, fechaFin, "pdf")}
                target="_blank"
                rel="noreferrer"
                className="btn-danger btn-sm"
                style={{ textDecoration: "none", display: "inline-block" }}
              >
                📄 Exportar PDF
              </a>
              <a
                href={reportesService.urlExportar(tipo, fechaInicio, fechaFin, "excel")}
                target="_blank"
                rel="noreferrer"
                className="btn-success btn-sm"
                style={{ textDecoration: "none", display: "inline-block" }}
              >
                📊 Exportar Excel
              </a>
            </div>
          </div>

          <div className="tabla-wrapper">
            <table>
              <thead>
                <tr>
                  {encabezados.map((k) => (
                    <th key={k}>{k.replace(/_/g, " ")}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filas.map((fila, i) => (
                  <tr key={i}>
                    {Object.values(fila).map((v, j) => (
                      <td key={j}>{String(v)}</td>
                    ))}
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

export default ReportesPage;