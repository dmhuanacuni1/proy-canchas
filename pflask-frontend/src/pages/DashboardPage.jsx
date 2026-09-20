import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // Estados para manejar la lista de usuarios y los errores
  const [users, setUsers] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');

  // useEffect hace que esta carga ocurra automáticamente al entrar a la página
  useEffect(() => {
    // Solo intentamos pedir la lista de usuarios si quien entró tiene el rol de 'admin'
    if (user?.role === 'admin') {
      cargarUsuarios();
    }
  }, [user]);

  const cargarUsuarios = async () => {
    try {
      const data = await authService.obtenerUsuarios();
      setUsers(data);
    } catch (error) {
      // Como el backend de tu compañero está apagado, veremos este mensaje por ahora
      setErrorMsg('No se pudieron cargar los usuarios. Verifica que el servidor backend de Flask esté encendido.');
    }
  };

  const handleEliminar = async (id) => {
    // Pedimos confirmación antes de borrar
    if (window.confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      try {
        await authService.eliminarUsuario(id);
        // Si el backend borra al usuario con éxito, lo quitamos de la tabla en pantalla
        setUsers(users.filter(u => u.id !== id));
      } catch (error) {
        alert('Error al intentar eliminar el usuario. El backend no responde.');
      }
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>Bienvenido al Sistema</h1>
      <p>Has iniciado sesión correctamente. Tu rol es: <strong>{user?.role}</strong></p>
      
      <button 
        onClick={handleLogout} 
        style={{ padding: '10px 20px', backgroundColor: 'red', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginBottom: '20px' }}
      >
        Cerrar Sesión
      </button>

      {/* Esta sección SOLO se dibuja en pantalla si el rol es 'admin' */}
      {user?.role === 'admin' && (
        <div style={{ marginTop: '30px', borderTop: '2px solid #ccc', paddingTop: '20px' }}>
          <h2>Gestión de Usuarios</h2>
          
          {errorMsg && <div style={{ color: 'white', backgroundColor: '#dc3545', padding: '10px', marginBottom: '15px' }}>{errorMsg}</div>}

          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                <th style={{ padding: '10px', border: '1px solid #ddd' }}>ID</th>
                <th style={{ padding: '10px', border: '1px solid #ddd' }}>Correo</th>
                <th style={{ padding: '10px', border: '1px solid #ddd' }}>Rol</th>
                <th style={{ padding: '10px', border: '1px solid #ddd' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.length > 0 ? (
                users.map(u => (
                  <tr key={u.id}>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>{u.id}</td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>{u.email}</td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>{u.role}</td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      <button 
                        onClick={() => handleEliminar(u.id)}
                        style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center', color: '#555' }}>
                    No hay usuarios para mostrar o esperando respuesta del servidor...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;