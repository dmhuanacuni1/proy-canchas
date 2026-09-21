import ForgotPasswordPage from './pages/ForgotPasswordPage';
import { Routes, Route, Navigate } from 'react-router-dom';
import ResetPasswordPage from './pages/ResetPasswordPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <Routes>
      {/* Si entran a la raíz, los mandamos al login */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      
      {/* Ruta pública */}
      <Route path="/login" element={<LoginPage />} />

      <Route path="/register" element={<RegisterPage />} />

      {/* Ruta pública para solicitar recuperación */}
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      <Route path="/reset-password/:token" element={<ResetPasswordPage />} />

      
      {/* Ruta protegida: Solo accesible si hay sesión iniciada */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/admin-dashboard" 
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

export default App;