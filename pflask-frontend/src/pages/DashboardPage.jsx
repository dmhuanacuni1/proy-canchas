import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/authService";


const emptyForm = {
  nombre: "",
  apellido: "",
  ci: "",
  celular: "",
  email: "",
  username: "",
  rol: "cliente",
  password: "",
};

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.role === "admin") {
      cargarUsuarios();
    }
  }, [user]);

  const cargarUsuarios = async () => {
    try {
      const data = await authService.obtenerUsuarios();
      setUsers(data);
    } catch (error) {
      setErrorMsg(
        "No se pudieron cargar los usuarios. Verifica que el servidor backend de Flask esté encendido.",
      );
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm("¿Estás seguro de que deseas eliminar este usuario?")) {
      try {
        await authService.eliminarUsuario(id);
        setUsers(users.filter((u) => u.id !== id));
        if (editing?.id === id) {
          setEditing(null);
        }
      } catch (error) {
        alert(
          error.response?.data?.error ||
            "Error al intentar eliminar el usuario.",
        );
      }
    }
  };

  const handleEditar = (u) => {
    setErrorMsg("");
    setSuccessMsg("");
    setEditing(u);
    setForm({
      nombre: u.nombre || "",
      apellido: u.apellido || "",
      ci: u.ci || "",
      celular: u.celular || "",
      email: u.email || "",
      username: u.username || "",
      rol: u.rol || "cliente",
      password: "",
    });
  };

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleGuardar = async (event) => {
    event.preventDefault();
    if (!editing) return;
    setSaving(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const payload = {
        nombre: form.nombre,
        apellido: form.apellido,
        ci: form.ci,
        celular: form.celular,
        email: form.email,
        username: form.username,
        rol: form.rol,
      };
      if (form.password.trim()) {
        payload.password = form.password;
        payload.contrasena = form.password;
      }
      const updated = await authService.actualizarUsuario(editing.id, payload);
      setUsers(users.map((u) => (u.id === updated.id ? updated : u)));
      setSuccessMsg("Usuario actualizado correctamente.");
      setEditing(null);
      setForm(emptyForm);
    } catch (error) {
      setErrorMsg(
        error.response?.data?.error || "No se pudo actualizar el usuario.",
      );
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const inputStyle = { width: "95%", padding: "8px", marginTop: "5px" };
  const labelBlock = { marginBottom: "12px" };

  return (
    <div style={{ padding: "40px", fontFamily: "sans-serif" }}>
      <h1>Bienvenido al Sistema</h1>
      
      <p>
        Has iniciado sesión correctamente. Tu rol es:{" "}
        <strong>{user?.role}</strong>
      </p>

      {/* BOTONES DE NAVEGACIÓN */}
      <div
        style={{
          marginTop: "20px",
          marginBottom: "20px",
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
        }}
      >
        {/* EVENTOS - todos los usuarios autenticados */}
        <button
          onClick={() => navigate("/eventos")}
          style={{
            padding: "12px 24px",
            backgroundColor: "#6366F1",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          Ver Catálogo de Eventos
        </button>

        {/* CLIENTE */}
        {(user?.role === "cliente" || user?.role === "user") && (
          <button
            onClick={() => navigate("/reservas")}
            style={{
              padding: "12px 24px",
              backgroundColor: "#6366F1",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            Ver Canchas y Reservar
          </button>
        )}

        {/* EMPLEADO */}
        {user?.role === "empleado" && (
          <button
            onClick={() => navigate("/reservas")}
            style={{
              padding: "12px 24px",
              backgroundColor: "#6366F1",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            Gestionar Reservas
          </button>
        )}

        {/* ADMINISTRADOR */}
        {user?.role === "admin" && (
          <>
            <button
              onClick={() => navigate("/reservas")}
              style={{
                padding: "12px 24px",
                backgroundColor: "#6366F1",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "16px",
              }}
            >
              Ver Reservas
            </button>

            <button
              onClick={() => navigate("/admin/eventos")}
              style={{
                padding: "12px 24px",
                backgroundColor: "#6366F1",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "16px",
              }}
            >
              Gestión de Eventos
            </button>

            <button
              onClick={() => {
                const el = document.getElementById("gestion-usuarios");
                if (el) {
                  el.scrollIntoView({ behavior: "smooth" });
                }
              }}
              style={{
                padding: "12px 24px",
                backgroundColor: "#6366F1",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "16px",
              }}
            >
              Gestionar Usuarios
            </button>
          </>
        )}

        {/* CERRAR SESIÓN */}
        <button
          onClick={handleLogout}
          style={{
            padding: "12px 24px",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          Cerrar Sesión
        </button>
      </div>

      {user?.role === "admin" && (
        <div
          id="gestion-usuarios"
          style={{
            marginTop: "30px",
            borderTop: "2px solid #ccc",
            paddingTop: "20px",
          }}
        >
          <h2>Gestión de Usuarios</h2>

          {errorMsg && (
            <div
              style={{
                color: "white",
                backgroundColor: "#dc3545",
                padding: "10px",
                marginBottom: "15px",
              }}
            >
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div
              style={{
                color: "white",
                backgroundColor: "#6366F1",
                padding: "10px",
                marginBottom: "15px",
              }}
            >
              {successMsg}
            </div>
          )}

          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginTop: "10px",
            }}
          >
            <thead>
              <tr style={{ backgroundColor: "#f4f4f4", textAlign: "left" }}>
                <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                  ID
                </th>
                <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                  Nombre
                </th>
                <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                  Usuario
                </th>
                <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                  Correo
                </th>
                <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                  Rol
                </th>
                <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody>
              {users.length > 0 ? (
                users.map((u) => (
                  <tr
                    key={u.id}
                    style={
                      editing?.id === u.id
                        ? { backgroundColor: "#ede9fe" }
                        : undefined
                    }
                  >
                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                      {u.id}
                    </td>
                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                      {u.nombre} {u.apellido}
                    </td>
                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                      {u.username}
                    </td>
                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                      {u.email}
                    </td>
                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                      {u.rol}
                    </td>
                    <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                      <button
                        onClick={() => handleEditar(u)}
                        style={{
                          backgroundColor: "#6366F1",
                          color: "white",
                          border: "none",
                          padding: "5px 10px",
                          borderRadius: "4px",
                          cursor: "pointer",
                          marginRight: "8px",
                        }}
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleEliminar(u.id)}
                        style={{
                          backgroundColor: "#dc3545",
                          color: "white",
                          border: "none",
                          padding: "5px 10px",
                          borderRadius: "4px",
                          cursor: "pointer",
                        }}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="6"
                    style={{
                      padding: "10px",
                      border: "1px solid #ddd",
                      textAlign: "center",
                      color: "#6b7280",
                    }}
                  >
                    No hay usuarios para mostrar o esperando respuesta del
                    servidor...
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {editing && (
            <form
              onSubmit={handleGuardar}
              style={{
                marginTop: "25px",
                padding: "20px",
                border: "1px solid #ccc",
                borderRadius: "8px",
                maxWidth: "520px",
              }}
            >
              <h3>Editar usuario #{editing.id}</h3>
              <div style={labelBlock}>
                <label>Nombre:</label>
                <br />
                <input
                  name="nombre"
                  value={form.nombre}
                  onChange={handleFormChange}
                  style={inputStyle}
                  required
                />
              </div>
              <div style={labelBlock}>
                <label>Apellido:</label>
                <br />
                <input
                  name="apellido"
                  value={form.apellido}
                  onChange={handleFormChange}
                  style={inputStyle}
                  required
                />
              </div>
              <div style={labelBlock}>
                <label>CI:</label>
                <br />
                <input
                  name="ci"
                  value={form.ci}
                  onChange={handleFormChange}
                  style={inputStyle}
                  required
                />
              </div>
              <div style={labelBlock}>
                <label>Celular:</label>
                <br />
                <input
                  name="celular"
                  value={form.celular}
                  onChange={handleFormChange}
                  style={inputStyle}
                />
              </div>
              <div style={labelBlock}>
                <label>Correo:</label>
                <br />
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleFormChange}
                  style={inputStyle}
                />
              </div>
              <div style={labelBlock}>
                <label>Username:</label>
                <br />
                <input
                  name="username"
                  value={form.username}
                  onChange={handleFormChange}
                  style={inputStyle}
                  required
                />
              </div>
              <div style={labelBlock}>
                <label>Rol:</label>
                <br />
                <select
                  name="rol"
                  value={form.rol}
                  onChange={handleFormChange}
                  style={inputStyle}
                >
                  <option value="cliente">cliente</option>
                  <option value="administrador">administrador</option>
                  <option value="empleado">empleado</option>
                </select>
              </div>
              <div style={{ marginBottom: "20px" }}>
                <label>Nueva contraseña (opcional):</label>
                <br />
                <input
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleFormChange}
                  style={inputStyle}
                  placeholder="Dejar vacío para no cambiarla"
                />
              </div>
              <button
                type="submit"
                disabled={saving}
                style={{
                  padding: "10px 16px",
                  backgroundColor: "#6366F1",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginRight: "8px",
                }}
              >
                {saving ? "Guardando..." : "Guardar cambios"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setEditing(null);
                  setForm(emptyForm);
                }}
                style={{
                  padding: "10px 16px",
                  backgroundColor: "#6b7280",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Cancelar
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
