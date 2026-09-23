import React from "react";
import type { Evento } from "../../types/evento.types";
import { Badge } from "../common/Badge";

interface TablaEventosAdminProps {
  eventos: Evento[];
  onEditar: (evento: Evento) => void;
  onEliminar: (id: number) => void;
}

export const TablaEventosAdmin: React.FC<TablaEventosAdminProps> = ({ eventos, onEditar, onEliminar }) => {
  return (
    <div style={{ overflowX: "auto", width: "100%", fontFamily: "sans-serif" }}>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          backgroundColor: "var(--code-bg, #1f2028)",
          marginTop: "15px",
        }}
      >
        <thead>
          <tr style={{ backgroundColor: "var(--bg, #16171d)", textAlign: "left", color: "var(--text-h, #f3f4f6)" }}>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>ID</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>Nombre del Evento</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>Tipo</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>Fecha</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>Horario</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>Cancha</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>Cupo</th>
            <th style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", textAlign: "center" }}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {eventos.length === 0 ? (
            <tr>
              <td colSpan={8} style={{ textAlign: "center", padding: "20px", color: "var(--text, #9ca3af)", border: "1px solid var(--border, #2e303a)" }}>
                No hay eventos registrados en este momento.
              </td>
            </tr>
          ) : (
            eventos.map((e) => (
              <tr key={e.id_evento} style={{ borderBottom: "1px solid var(--border, #2e303a)" }}>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", color: "var(--text, #9ca3af)" }}>{e.id_evento}</td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", fontWeight: 600, color: "var(--text-h, #f3f4f6)" }}>
                  {e.nombre_evento}
                </td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)" }}>
                  <Badge variant="primary">{e.tipo_evento || "Social"}</Badge>
                </td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", color: "var(--text, #9ca3af)" }}>{e.fecha_evento}</td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", color: "var(--text, #9ca3af)" }}>
                  {e.hora_inicio} - {e.hora_fin}
                </td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", color: "var(--text, #9ca3af)" }}>
                  {e.nombre_cancha || `Cancha #${e.id_cancha}`}
                </td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", color: "var(--text, #9ca3af)" }}>
                  {e.cupo_maximo || "Sin límite"}
                </td>
                <td style={{ padding: "10px", border: "1px solid var(--border, #2e303a)", textAlign: "center" }}>
                  <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                    <button
                      onClick={() => onEditar(e)}
                      style={{
                        padding: "5px 12px",
                        backgroundColor: "#6366F1",
                        color: "#fff",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                      }}
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => onEliminar(e.id_evento)}
                      style={{
                        padding: "5px 12px",
                        backgroundColor: "#dc3545",
                        color: "#fff",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                      }}
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default TablaEventosAdmin;
