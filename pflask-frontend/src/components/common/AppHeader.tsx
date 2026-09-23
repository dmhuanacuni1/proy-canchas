import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "../../App.css";

interface AppHeaderProps {
  titulo?: string;
  mostrarVolver?: boolean;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  titulo = "Sistema de Gestión de Canchas",
  mostrarVolver = true,
}) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const nombreCompleto =
    user?.nombre_completo ||
    `${user?.nombre || ""} ${user?.apellido || ""}`.trim() ||
    user?.username ||
    "Usuario";

  const rolOriginal = user?.rol || user?.role || "";

  const rolNormalizado =
    rolOriginal === "admin"
      ? "administrador"
      : rolOriginal === "user"
      ? "cliente"
      : rolOriginal;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const mostrarRol = () => {
    if (rolNormalizado === "administrador") return "ADMINISTRADOR";
    if (rolNormalizado === "empleado") return "EMPLEADO";
    if (rolNormalizado === "cliente") return "CLIENTE";

    return rolNormalizado.toUpperCase();
  };

  return (
    <header className="app-header">
      <div className="header-top">
        <div style={{ textAlign: "left" }}>
          <h1>
            🏟️ {titulo}
          </h1>

          {mostrarVolver && (
            <button
              className="btn-secondary btn-sm"
              onClick={() => navigate("/dashboard")}
              style={{ marginTop: "8px" }}
            >
              ← Volver al panel
            </button>
          )}
        </div>

        <div className="user-info">
          <div className="user-details">
            <span className="user-name">
              👤 {nombreCompleto}
            </span>

            <span
              className={`rol-badge rol-${rolNormalizado}`}
            >
              {mostrarRol()}
            </span>
          </div>

          <button
            className="btn-secondary btn-sm"
            onClick={handleLogout}
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </header>
  );
};

export default AppHeader;