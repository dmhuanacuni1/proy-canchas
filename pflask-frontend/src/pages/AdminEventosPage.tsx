import React, { useState } from "react";
import { Link } from "react-router-dom";
import type { Evento, CreateEventoDTO } from "../types/evento.types";
import { TablaEventosAdmin } from "../components/admin/TablaEventosAdmin";
import { EventoFormModal } from "../components/admin/EventoFormModal";
import { useEventos } from "../hooks/useEventos";

interface AdminEventosPageProps {
  eventos?: Evento[];
  loading?: boolean;
  error?: string | null;
  onCrearEvento?: (data: CreateEventoDTO) => Promise<void>;
  onActualizarEvento?: (id: number, data: CreateEventoDTO) => Promise<void>;
  onEliminarEvento?: (id: number) => Promise<void>;
}

export const AdminEventosPage: React.FC<AdminEventosPageProps> = (props) => {
  const hookData = useEventos();
  const eventos = props.eventos ?? hookData.eventos;
  const loading = props.loading ?? hookData.loading;
  const error = props.error ?? hookData.error;
  const onCrearEvento = props.onCrearEvento ?? hookData.crearEvento;
  const onActualizarEvento = props.onActualizarEvento ?? hookData.actualizarEvento;
  const onEliminarEvento = props.onEliminarEvento ?? hookData.eliminarEvento;

  const [modalAbierto, setModalAbierto] = useState(false);
  const [eventoEditar, setEventoEditar] = useState<Evento | null>(null);

  const handleNuevoEvento = () => {
    setEventoEditar(null);
    setModalAbierto(true);
  };

  const handleEditar = (evento: Evento) => {
    setEventoEditar(evento);
    setModalAbierto(true);
  };

  const handleEliminar = async (id: number) => {
    if (window.confirm(`¿Estás seguro de que deseas eliminar el evento con ID #${id}?`)) {
      await onEliminarEvento(id);
    }
  };

  const handleSubmit = async (data: CreateEventoDTO) => {
    if (eventoEditar) {
      await onActualizarEvento(eventoEditar.id_evento, data);
    } else {
      await onCrearEvento(data);
    }
  };

  return (
    <div style={{ minHeight: "100vh", padding: "40px 20px", fontFamily: "sans-serif" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto", textAlign: "left" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "25px",
            flexWrap: "wrap",
            gap: "15px",
            borderBottom: "1px solid var(--border, #2e303a)",
            paddingBottom: "15px",
          }}
        >
          <div>
            <Link to="/admin-dashboard" style={{ color: "#007BFF", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "8px", fontWeight: 600 }}>
              &larr; Volver al Panel de Administración
            </Link>
            <h1 style={{ margin: 0, fontSize: "28px", color: "var(--text-h, #f3f4f6)" }}>Gestión de Eventos y Servicios Sociales</h1>
            <p style={{ margin: "6px 0 0 0", color: "var(--text, #9ca3af)", fontSize: "15px" }}>
              Administra, evalúa, programa y modifica los eventos del complejo deportivo.
            </p>
          </div>

          <button
            onClick={handleNuevoEvento}
            style={{
              padding: "10px 20px",
              backgroundColor: "#28a745",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "14px",
            }}
          >
            <span style={{ fontSize: "16px", fontWeight: "bold" }}>+</span> Añadir Evento
          </button>
        </div>

        {loading && <p style={{ color: "var(--text, #9ca3af)" }}>Cargando eventos...</p>}
        {error && <div style={{ padding: "10px", backgroundColor: "#f8d7da", color: "#721c24", border: "1px solid #f5c6cb", borderRadius: "4px", marginBottom: "15px" }}>{error}</div>}

        {!loading && (
          <TablaEventosAdmin
            eventos={eventos}
            onEditar={handleEditar}
            onEliminar={handleEliminar}
          />
        )}

        <EventoFormModal
          isOpen={modalAbierto}
          onClose={() => setModalAbierto(false)}
          onSubmit={handleSubmit}
          eventoEditar={eventoEditar}
        />
      </div>
    </div>
  );
};

export default AdminEventosPage;
