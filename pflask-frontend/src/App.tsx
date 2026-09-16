import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

interface Cancha {
  id: number;
  nombre: string;
  deporte: string;
  precio_hora: number;
  techada: boolean;
  estado: string;
}

function App() {
  const [canchas, setCanchas] = useState<Cancha[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get<Cancha[]>("http://127.0.0.1:5000/api/canchas")
      .then((res) => setCanchas(res.data))
      .catch(() =>
        setError("No se pudo conectar con el backend. ¿Está corriendo flask run?")
      )
      .finally(() => setCargando(false));
  }, []);

  if (cargando) return <p>Cargando canchas...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h1>Canchas disponibles</h1>
      <ul>
        {canchas.map((c) => (
          <li key={c.id}>
            {c.nombre} — {c.deporte} — Bs {c.precio_hora}/hora
            {c.techada ? " (techada)" : ""} — {c.estado}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;