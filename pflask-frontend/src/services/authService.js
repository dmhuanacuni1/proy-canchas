import axiosClient from '../api/axiosClient';

export const authService = {
  // Iniciar Sesión (Petición real a Flask)
  login: async (credentials) => {
    const response = await axiosClient.post('/auth/login', credentials);
    return response.data; // Espera { token, role, id, email }
  },

  // Registro de Usuario (Petición real a Flask)
  registro: async (userData) => {
    const response = await axiosClient.post('/auth/register', userData);
    return response.data;
  },
  
  // Recuperar Contraseña (Petición real a Flask)
  solicitarRecuperacion: async (email) => {
    const response = await axiosClient.post('/auth/recover', { email });
    return response.data;
  },
  
  restablecerContrasena: async (token, newPassword) => {
    const response = await axiosClient.post('/auth/reset', { token, newPassword });
    return response.data;
  },

  // Gestión de Usuarios (Admin)
  obtenerUsuarios: async () => {
    const response = await axiosClient.get('/admin/users');
    return response.data;
  },
  
  eliminarUsuario: async (id) => {
    const response = await axiosClient.delete(`/admin/users/${id}`);
    return response.data;
  }
};