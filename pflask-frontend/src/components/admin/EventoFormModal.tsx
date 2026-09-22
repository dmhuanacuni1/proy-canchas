import React, { useState, useEffect } from "react";
import type { Evento, CreateEventoDTO } from "../../types/evento.types";
import { Modal } from "../common/Modal";

interface EventoFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateEventoDTO) => Promise<void>;
  eventoEditar: Evento | null;
}

export const EventoFormModal: React.FC<EventoFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  eventoEditar,
}) => {
  const [formData, setFormData] = useState<CreateEventoDTO>({
    nombre_evento: "",
    tipo_evento: "Social",
    fecha_evento: "",
    hora_inicio: "09:00",
    hora_fin: "11:00",
    cupo_maximo: 20,
    organizador: "",
    descripcion: "",
    id_cancha: 1,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (eventoEditar) {
      setFormData({
        nombre_evento: eventoEditar.nombre_evento,
        tipo_evento: eventoEditar.tipo_evento || "Social",
        fecha_evento: eventoEditar.fecha_evento,
        hora_inicio: eventoEditar.hora_inicio,
        hora_fin: eventoEditar.hora_fin,
        cupo_maximo: eventoEditar.cupo_maximo || 0,
        organizador: eventoEditar.organizador || "",
        descripcion: eventoEditar.descripcion || "",
        id_cancha: eventoEditar.id_cancha,
      });
    } else {
      setFormData({
        nombre_evento: "",
        tipo_evento: "Social",
        fecha_evento: new Date().toISOString().split("T")[0],
        hora_inicio: "09:00",
        hora_fin: "11:00",
        cupo_maximo: 20,
        organizador: "",
        descripcion: "",
        id_cancha: 1,
      });
    }
    setError(null);
  }, [eventoEditar, isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "id_cancha" || name === "cupo_maximo" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const hoy = new Date().toISOString().split("T")[0];
    if (formData.fecha_evento < hoy) {
      setError("La fecha del evento no puede ser anterior a la fecha actual.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      const errData = err?.response?.data;
      const errMsg = errData?.detalles
        ? Array.isArray(errData.detalles)
          ? errData.detalles.join(" ")
          : String(errData.detalles)
        : errData?.error || "Ocurrió un error al guardar el evento.";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const labelStyle = { display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: 600, color: "var(--text-h, #f3f4f6)" };
  const inputStyle = {
    width: "100%",
    padding: "8px 10px",
    borderRadius: "4px",
    border: "1px solid var(--border, #2e303a)",
    backgroundColor: "var(--bg, #16171d)",
    color: "var(--text-h, #f3f4f6)",
    boxSizing: "border-box" as const,
    fontSize: "14px",
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={eventoEditar ? "Modificar Evento" : "Añadir Nuevo Evento"}
    >
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px", fontFamily: "sans-serif", textAlign: "left" }}>
        {error && (
          <div style={{ padding: "10px", backgroundColor: "#f8d7da", color: "#721c24", border: "1px solid #f5c6cb", borderRadius: "4px", fontSize: "14px" }}>
            {error}
          </div>
        )}

        <div>
          <label style={labelStyle}>Nombre del Evento *</label>
          <input
            type="text"
            name="nombre_evento"
            value={formData.nombre_evento}
            onChange={handleChange}
            required
            style={inputStyle}
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
          <div>
            <label style={labelStyle}>Tipo de Evento</label>
            <input
              type="text"
              name="tipo_evento"
              value={formData.tipo_evento}
              onChange={handleChange}
              placeholder="Social, Torneo, Taller..."
              style={inputStyle}
            />
          </div>

          <div>
            <label style={labelStyle}>Fecha *</label>
            <input
              type="date"
              name="fecha_evento"
              value={formData.fecha_evento}
              onChange={handleChange}
              required
              min={new Date().toISOString().split("T")[0]}
              style={inputStyle}
            />
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
          <div>
            <label style={labelStyle}>Hora Inicio (HH:MM) *</label>
            <input
              type="time"
              name="hora_inicio"
              value={formData.hora_inicio}
              onChange={handleChange}
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label style={labelStyle}>Hora Fin (HH:MM) *</label>
            <input
              type="time"
              name="hora_fin"
              value={formData.hora_fin}
              onChange={handleChange}
              required
              style={inputStyle}
            />
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
          <div>
            <label style={labelStyle}>ID Cancha *</label>
            <input
              type="number"
              name="id_cancha"
              value={formData.id_cancha}
              onChange={handleChange}
              required
              min={1}
              style={inputStyle}
            />
          </div>

          <div>
            <label style={labelStyle}>Cupo Máximo</label>
            <input
              type="number"
              name="cupo_maximo"
              value={formData.cupo_maximo || ""}
              onChange={handleChange}
              min={1}
              style={inputStyle}
            />
          </div>
        </div>

        <div>
          <label style={labelStyle}>Organizador</label>
          <input
            type="text"
            name="organizador"
            value={formData.organizador}
            onChange={handleChange}
            placeholder="Nombre de la institución o encargado"
            style={inputStyle}
          />
        </div>

        <div>
          <label style={labelStyle}>Descripción</label>
          <textarea
            name="descripcion"
            value={formData.descripcion}
            onChange={handleChange}
            rows={3}
            style={{ ...inputStyle, fontFamily: "inherit" }}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "10px" }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: "8px 16px",
              backgroundColor: "#6c757d",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
            }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "8px 20px",
              backgroundColor: eventoEditar ? "#007BFF" : "#28a745",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: "14px",
            }}
          >
            {loading ? "Guardando..." : eventoEditar ? "Actualizar Evento" : "Crear Evento"}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default EventoFormModal;
