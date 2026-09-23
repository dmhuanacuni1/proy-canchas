import React, { useState } from "react";
import type { Evento } from "../types/evento.types";
import { EventoCard } from "../components/eventos/EventoCard";
import { EventoDetalleModal } from "../components/eventos/EventoDetalleModal";
import { useEventos } from "../hooks/useEventos";
import { AppHeader } from "../components/common/AppHeader";
import "../App.css";

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

  const [eventoSeleccionado, setEventoSeleccionado] =
    useState<Evento | null>(null);

  const [modalAbierto, setModalAbierto] = useState(false);

  const [filtroTipo, setFiltroTipo] =
    useState<string>("todos");

  const tiposUnicos = Array.from(
    new Set(
      eventos
        .map((evento) => evento.tipo_evento)
        .filter(Boolean)
    )
  ) as string[];

  const eventosFiltrados = eventos.filter((evento) => {
    if (filtroTipo === "todos") {
      return true;
    }

    return evento.tipo_evento === filtroTipo;
  });

  const handleVerDetalles = (evento: Evento) => {
    setEventoSeleccionado(evento);
    setModalAbierto(true);
  };

  const handleCerrarModal = () => {
    setModalAbierto(false);
    setEventoSeleccionado(null);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "35px 40px",
        fontFamily: "sans-serif",
        background: "var(--color-bg)",
        color: "var(--color-text)",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
          textAlign: "left",
        }}
      >
        <AppHeader titulo="Eventos y Servicios Sociales" />

        <section
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "25px",
            flexWrap: "wrap",
            gap: "15px",
          }}
        >
          <div>
            <h2
              style={{
                margin: 0,
                fontSize: "24px",
                color: "var(--color-text)",
              }}
            >
              Catálogo de Eventos y Servicios Sociales
            </h2>

            <p
              style={{
                margin: "6px 0 0 0",
                color: "var(--color-text-dim)",
                fontSize: "15px",
              }}
            >
              Explora las actividades, torneos y jornadas comunitarias
              disponibles en nuestras canchas.
            </p>
          </div>

          {tiposUnicos.length > 0 && (
            <div
              style={{
                display: "flex",
                gap: "8px",
                alignItems: "center",
              }}
            >
              <span
                style={{
                  fontSize: "14px",
                  color: "var(--color-text-dim)",
                }}
              >
                Filtrar por:
              </span>

              <select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                style={{
                  backgroundColor: "var(--color-bg-elevated)",
                  color: "var(--color-text)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "8px 12px",
                  fontSize: "14px",
                  cursor: "pointer",
                }}
              >
                <option value="todos">
                  Todos los tipos
                </option>

                {tiposUnicos.map((tipo) => (
                  <option
                    key={tipo}
                    value={tipo}
                  >
                    {tipo}
                  </option>
                ))}
              </select>
            </div>
          )}
        </section>

        {loading && (
          <p
            style={{
              color: "var(--color-text-dim)",
            }}
          >
            Cargando eventos disponibles...
          </p>
        )}

        {error && (
          <div
            style={{
              padding: "12px",
              backgroundColor: "rgba(220, 53, 69, 0.15)",
              color: "#c62828",
              border: "1px solid rgba(220, 53, 69, 0.5)",
              borderRadius: "6px",
              marginBottom: "15px",
            }}
          >
            {error}
          </div>
        )}

        {!loading &&
          !error &&
          eventosFiltrados.length === 0 && (
            <div
              style={{
                backgroundColor: "var(--color-bg-elevated)",
                border: "1px solid var(--color-border)",
                padding: "40px",
                borderRadius: "8px",
                textAlign: "center",
                color: "var(--color-text-dim)",
              }}
            >
              No hay eventos registrados en este momento.
            </div>
          )}

        {!loading &&
          !error &&
          eventosFiltrados.length > 0 && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fill, minmax(300px, 1fr))",
                gap: "20px",
              }}
            >
              {eventosFiltrados.map((evento) => (
                <EventoCard
                  key={evento.id_evento}
                  evento={evento}
                  onVerDetalles={handleVerDetalles}
                />
              ))}
            </div>
          )}

        <EventoDetalleModal
          evento={eventoSeleccionado}
          isOpen={modalAbierto}
          onClose={handleCerrarModal}
        />
      </div>
    </div>
  );
};

export default UsuarioEventosPage;