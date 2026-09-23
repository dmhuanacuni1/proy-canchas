import React from "react";
import type { Evento } from "../../types/evento.types";
import { Modal } from "../common/Modal";
import { Badge } from "../common/Badge";

interface EventoDetalleModalProps {
  evento: Evento | null;
  isOpen: boolean;
  onClose: () => void;
}

export const EventoDetalleModal: React.FC<EventoDetalleModalProps> = ({ evento, isOpen, onClose }) => {
  if (!evento) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={evento.nombre_evento}>
      <div style={{ display: "flex", flexDirection: "column", gap: "15px", fontFamily: "sans-serif", textAlign: "left" }}>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <Badge variant="primary">{evento.tipo_evento || "Evento Social"}</Badge>
          {evento.cupo_maximo && (
            <Badge variant="info">Cupo: {evento.cupo_maximo} personas</Badge>
          )}
        </div>

        <div>
          <h4 style={{ margin: "0 0 6px 0", color: "var(--text, #9ca3af)", fontSize: "0.85rem", textTransform: "uppercase" }}>
            Descripción
          </h4>
          <p style={{ margin: 0, color: "var(--text-h, #f3f4f6)", lineHeight: 1.5, fontSize: "0.95rem" }}>
            {evento.descripcion || "No se ha proporcionado una descripción detallada para este evento."}
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "12px",
            backgroundColor: "var(--bg, #16171d)",
            border: "1px solid var(--border, #2e303a)",
            padding: "15px",
            borderRadius: "6px",
          }}
        >
          <div>
            <span style={{ color: "var(--text, #9ca3af)", fontSize: "0.8rem", display: "block" }}>Fecha</span>
            <strong style={{ color: "var(--text-h, #f3f4f6)" }}>{evento.fecha_evento}</strong>
          </div>
          <div>
            <span style={{ color: "var(--text, #9ca3af)", fontSize: "0.8rem", display: "block" }}>Horario</span>
            <strong style={{ color: "var(--text-h, #f3f4f6)" }}>{evento.hora_inicio} - {evento.hora_fin}</strong>
          </div>
          <div>
            <span style={{ color: "var(--text, #9ca3af)", fontSize: "0.8rem", display: "block" }}>Lugar / Cancha</span>
            <strong style={{ color: "var(--text-h, #f3f4f6)" }}>{evento.nombre_cancha || `Cancha #${evento.id_cancha}`}</strong>
          </div>
          <div>
            <span style={{ color: "var(--text, #9ca3af)", fontSize: "0.8rem", display: "block" }}>Organizador</span>
            <strong style={{ color: "var(--text-h, #f3f4f6)" }}>{evento.organizador || "Comunidad / Club"}</strong>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "10px" }}>
          <button
            onClick={onClose}
            style={{
              padding: "8px 20px",
              backgroundColor: "#6b7280",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: "0.9rem",
            }}
          >
            Cerrar
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default EventoDetalleModal;
