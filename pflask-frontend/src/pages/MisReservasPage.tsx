import { useEffect, useState } from "react";
import { api } from "../services/api";

interface Reserva {
  id: number;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  estado: string;
  motivo_cancelacion: string | null;
  cancha: {
    id: number;
    nombre: string;
    deporte: string;
  };
}

function MisReservasPage() {
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarReservas = () => {
    setCargando(true);
    api
      .get<Reserva[]>("/reservas/historial")
      .then((res: { data: Reserva[] }) => setReservas(res.data))
      .catch(() => setError("Error al cargar el historial de reservas."))
      .finally(() => setCargando(false));
  };

  useEffect(() => {
    cargarReservas();
  }, []);

  const handleCancelar = async (id: number) => {
    const motivo = prompt("¿Por qué deseas cancelar esta reserva?");
    if (motivo === null) return; // Si el usuario cancela el prompt, no hacemos nada

    try {
      await api.put(`/reservas/${id}/cancelar`, { motivo: motivo || "Cancelada por el usuario" });
      alert("Reserva cancelada exitosamente");
      cargarReservas(); // Recargamos la lista para ver el cambio de estado
    } catch (err: any) {
      alert(err.response?.data?.error || "Error al cancelar la reserva.");
    }
  };

  if (cargando) return <p style={{ padding: "20px" }}>Cargando historial...</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h1>Mis Reservas</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      
      {reservas.length === 0 ? (
        <p>No tienes reservas registradas aún.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "15px" }}>
          <thead>
            <tr style={{ background: "#f4f4f4", textAlign: "left" }}>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>Cancha</th>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>Fecha</th>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>Horario</th>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>Estado</th>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {reservas.map((r) => (
              <tr key={r.id}>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {r.cancha.nombre} ({r.cancha.deporte})
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>{r.fecha}</td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {r.hora_inicio.substring(0, 5)} - {r.hora_fin.substring(0, 5)}
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd", fontWeight: "bold" }}>
                  {r.estado.toUpperCase()}
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {(r.estado === "pendiente" || r.estado === "confirmada") && (
                    <button 
                      onClick={() => handleCancelar(r.id)}
                      style={{ padding: "5px 10px", background: "#dc3545", color: "white", border: "none", borderRadius: "3px", cursor: "pointer" }}
                    >
                      Cancelar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default MisReservasPage;