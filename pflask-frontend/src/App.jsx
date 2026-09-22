import ForgotPasswordPage from './pages/ForgotPasswordPage';
import { Routes, Route, Navigate } from 'react-router-dom';
import ResetPasswordPage from './pages/ResetPasswordPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ReservasPage from './pages/ReservasPage'; // <-- Importante
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password/:token" element={<ResetPasswordPage />} />

      {/* Dashboard de gestión de usuarios (solo admin, ruta secundaria) */}
      <Route 
        path="/usuarios" 
        element={
          <ProtectedRoute allowedRoles={['admin', 'administrador']}>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />

      {/* Dashboard de reservas (todos los roles) - RUTA PRINCIPAL */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <ReservasPage />
          </ProtectedRoute>
        } 
      />
      
      {/* Panel admin/empleado de reservas */}
      <Route 
        path="/admin-dashboard" 
        element={
          <ProtectedRoute allowedRoles={['admin', 'administrador', 'empleado']}>
            <ReservasPage />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

export default App;