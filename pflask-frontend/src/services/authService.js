import axiosClient from '../api/axiosClient';

export const authService = {
  // Caso de Uso 2: Iniciar Sesión (Simulado)
  login: async (credentials) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (credentials.email === 'admin@dytech.com') {
          resolve({ token: 'fake-jwt-token-admin', role: 'admin' });
        } else {
          resolve({ token: 'fake-jwt-token-user', role: 'user' });
        }
      }, 1000);
    });
  },

  // NUEVO: Caso de Uso: Registro de Usuario (Simulado)
  registro: async (userData) => {
    // Simulamos que el backend guarda el usuario exitosamente en 1.5 segundos
    return new Promise((resolve) => setTimeout(resolve, 1500));
    
    // Cuando el backend esté listo, borrarás la línea de arriba y descomentarás esta:
    // return await axiosClient.post('/auth/register', userData);
  },
  
  // Caso de Uso 3: Recuperar Contraseña (Simulados)
  solicitarRecuperacion: async (email) => {
    return new Promise((resolve) => setTimeout(resolve, 1000));
  },
  restablecerContrasena: async (token, newPassword) => {
    return new Promise((resolve) => setTimeout(resolve, 1500));
  },

  // Caso de Uso 1: Gestión de Usuarios (Conectado a Axios real)
  obtenerUsuarios: async () => {
    const response = await axiosClient.get('/admin/users');
    return response.data;
  },
  eliminarUsuario: async (id) => {
    return await axiosClient.delete(`/admin/users/${id}`);
  }
};