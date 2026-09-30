import React, { useState } from "react";
import type { Evento, CreateEventoDTO } from "../types/evento.types";
import { TablaEventosAdmin } from "../components/admin/TablaEventosAdmin";
import { EventoFormModal } from "../components/admin/EventoFormModal";
import { useEventos } from "../hooks/useEventos";
import { AppLayout } from "../components/layout/AppLayout";

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
  const onActualizarEvento =
    props.onActualizarEvento ?? hookData.actualizarEvento;
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
    const confirmar = window.confirm(
      `¿Estás seguro de que deseas eliminar el evento con ID #${id}?`
    );

    if (!confirmar) return;

    try {
      await onEliminarEvento(id);
    } catch (error) {
      console.error("Error al eliminar evento:", error);
    }
  };

  const handleSubmit = async (data: CreateEventoDTO) => {
    try {
      if (eventoEditar) {
        await onActualizarEvento(eventoEditar.id_evento, data);
      } else {
        await onCrearEvento(data);
      }

      setModalAbierto(false);
      setEventoEditar(null);
    } catch (error) {
      console.error("Error al guardar evento:", error);
      throw error;
    }
  };

  return (
    <AppLayout
      title="Gestión de Eventos"
      subtitle="Administra, programa, modifica y elimina los eventos del complejo deportivo."
    >
      <div
        className="header-row"
        style={{ marginTop: "8px", marginBottom: "16px" }}
      >
        <h2 style={{ margin: 0, fontSize: "18px" }}>Eventos registrados</h2>

        <button onClick={handleNuevoEvento} className="btn-success">
          <span style={{ fontSize: "16px", fontWeight: "bold" }}>+</span>
          {"  Añadir Evento"}
        </button>
      </div>

      {loading && <p style={{ color: "var(--color-text-dim)" }}>Cargando eventos...</p>}

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

      {!loading && !error && eventos.length === 0 && (
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

      {!loading && !error && eventos.length > 0 && (
        <TablaEventosAdmin
          eventos={eventos}
          onEditar={handleEditar}
          onEliminar={handleEliminar}
        />
      )}

      <EventoFormModal
        isOpen={modalAbierto}
        onClose={() => {
          setModalAbierto(false);
          setEventoEditar(null);
        }}
        onSubmit={handleSubmit}
        eventoEditar={eventoEditar}
      />
    </AppLayout>
  );
};

export default AdminEventosPage;