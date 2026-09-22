import React from "react";
import type { Evento } from "../../types/evento.types";
import { Badge } from "../common/Badge";

interface EventoCardProps {
  evento: Evento;
  onVerDetalles: (evento: Evento) => void;
}

export const EventoCard: React.FC<EventoCardProps> = ({ evento, onVerDetalles }) => {
  return (
    <div
      style={{
        backgroundColor: "var(--code-bg, #1f2028)",
        borderRadius: "8px",
        border: "1px solid var(--border, #2e303a)",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        boxShadow: "0 2px 5px rgba(0, 0, 0, 0.2)",
        fontFamily: "sans-serif",
        textAlign: "left",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Badge variant="primary">{evento.tipo_evento || "Evento Social"}</Badge>
        <span style={{ fontSize: "0.85rem", color: "var(--text, #9ca3af)" }}>
          Fecha: {evento.fecha_evento}
        </span>
      </div>

      <h4 style={{ margin: 0, fontSize: "1.2rem", color: "var(--text-h, #f3f4f6)", fontWeight: 600 }}>
        {evento.nombre_evento}
      </h4>

      <p style={{ margin: 0, fontSize: "0.95rem", color: "var(--text, #9ca3af)", lineHeight: 1.5 }}>
        {evento.descripcion
          ? evento.descripcion.length > 90
            ? evento.descripcion.substring(0, 90) + "..."
            : evento.descripcion
          : "Sin descripción disponible."}
      </p>

      <div style={{ fontSize: "0.85rem", color: "var(--text, #9ca3af)", marginTop: "auto", display: "flex", flexDirection: "column", gap: "4px" }}>
        <div>Horario: <strong style={{ color: "var(--text-h, #f3f4f6)" }}>{evento.hora_inicio} - {evento.hora_fin}</strong></div>
        {evento.nombre_cancha && <div>Cancha: <strong style={{ color: "var(--text-h, #f3f4f6)" }}>{evento.nombre_cancha}</strong></div>}
      </div>

      <button
        onClick={() => onVerDetalles(evento)}
        style={{
          marginTop: "8px",
          padding: "10px 15px",
          backgroundColor: "#007BFF",
          color: "#ffffff",
          border: "none",
          borderRadius: "4px",
          fontWeight: 600,
          cursor: "pointer",
          fontSize: "0.9rem",
          transition: "background-color 0.2s",
        }}
      >
        Ver Más Detalles
      </button>
    </div>
  );
};

export default EventoCard;
