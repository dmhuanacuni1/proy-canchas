import React, { useState } from "react";
import { Link } from "react-router-dom";
import type { Evento } from "../types/evento.types";
import { EventoCard } from "../components/eventos/EventoCard";
import { EventoDetalleModal } from "../components/eventos/EventoDetalleModal";
import { useEventos } from "../hooks/useEventos";

interface UsuarioEventosPageProps {
  eventos?: Evento[];
  loading?: boolean;
  error?: string | null;
}

export const UsuarioEventosPage: React.FC<UsuarioEventosPageProps> = (props) => {
  const hookData = useEventos();
  const eventos = props.eventos ?? hookData.eventos;
  const loading = props.loading ?? hookData.loading;
  const error = props.error ?? hookData.error;

  const [eventoSeleccionado, setEventoSeleccionado] = useState<Evento | null>(null);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [filtroTipo, setFiltroTipo] = useState<string>("todos");

  const tiposUnicos = Array.from(
    new Set(eventos.map((e) => e.tipo_evento).filter(Boolean))
  ) as string[];

  const eventosFiltrados = eventos.filter((e) => {
    if (filtroTipo === "todos") return true;
    return e.tipo_evento === filtroTipo;
  });

  const handleVerDetalles = (evento: Evento) => {
    setEventoSeleccionado(evento);
    setModalAbierto(true);
  };

  return (
    <div style={{ minHeight: "100vh", padding: "40px 20px", fontFamily: "sans-serif" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto", textAlign: "left" }}>
        {/* Navegación y encabezado */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "25px", flexWrap: "wrap", gap: "15px", borderBottom: "1px solid var(--border, #2e303a)", paddingBottom: "15px" }}>
          <div>
            <Link to="/dashboard" style={{ color: "#007BFF", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "8px", fontWeight: 600 }}>
              &larr; Volver al Panel
            </Link>
            <h1 style={{ margin: 0, fontSize: "28px", color: "var(--text-h, #f3f4f6)" }}>Catálogo de Eventos y Servicios Sociales</h1>
            <p style={{ margin: "6px 0 0 0", color: "var(--text, #9ca3af)", fontSize: "15px" }}>
              Explora las actividades, torneos y jornadas comunitarias en nuestras canchas.
            </p>
          </div>

          {tiposUnicos.length > 0 && (
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              <span style={{ fontSize: "14px", color: "var(--text, #9ca3af)" }}>Filtrar por:</span>
              <select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                style={{
                  backgroundColor: "var(--code-bg, #1f2028)",
                  color: "var(--text-h, #f3f4f6)",
                  border: "1px solid var(--border, #2e303a)",
                  borderRadius: "4px",
                  padding: "6px 10px",
                  fontSize: "14px",
                }}
              >
                <option value="todos">Todos los tipos</option>
                {tiposUnicos.map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {loading && <p style={{ color: "var(--text, #9ca3af)" }}>Cargando eventos disponibles...</p>}
        {error && <div style={{ padding: "10px", backgroundColor: "#f8d7da", color: "#721c24", border: "1px solid #f5c6cb", borderRadius: "4px", marginBottom: "15px" }}>{error}</div>}

        {!loading && !error && eventosFiltrados.length === 0 && (
          <div
            style={{
              backgroundColor: "var(--code-bg, #1f2028)",
              border: "1px solid var(--border, #2e303a)",
              padding: "40px",
              borderRadius: "8px",
              textAlign: "center",
              color: "var(--text, #9ca3af)",
            }}
          >
            No hay eventos registrados en este momento.
          </div>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            gap: "20px",
          }}
        >
          {eventosFiltrados.map((evento) => (
            <EventoCard key={evento.id_evento} evento={evento} onVerDetalles={handleVerDetalles} />
          ))}
        </div>

        <EventoDetalleModal
          evento={eventoSeleccionado}
          isOpen={modalAbierto}
          onClose={() => setModalAbierto(false)}
        />
      </div>
    </div>
  );
};

export default UsuarioEventosPage;
