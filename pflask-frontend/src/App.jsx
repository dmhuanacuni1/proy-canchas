import ForgotPasswordPage from './pages/ForgotPasswordPage';
import { Routes, Route, Navigate } from 'react-router-dom';
import ResetPasswordPage from './pages/ResetPasswordPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ReservasPage from './pages/ReservasPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import UsuarioEventosPage from './pages/UsuarioEventosPage';
import AdminEventosPage from './pages/AdminEventosPage';

function App() {
  return (
    <Routes>
      {/* Redirección raíz */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Rutas públicas */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password/:token" element={<ResetPasswordPage />} />

      {/* Dashboard principal */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      {/* Módulo de Eventos y Servicios Sociales */}
      <Route
        path="/eventos"
        element={
          <ProtectedRoute>
            <UsuarioEventosPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/eventos"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminEventosPage />
          </ProtectedRoute>
        }
      />

      {/* Reservas */}
      <Route
        path="/reservas"
        element={
          <ProtectedRoute>
            <ReservasPage />
          </ProtectedRoute>
        }
      />

      {/* Gestión de usuarios */}
      <Route
        path="/usuarios"
        element={
          <ProtectedRoute allowedRoles={['admin', 'administrador']}>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;