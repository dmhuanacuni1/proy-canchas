import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useParams, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

// 1. Reglas de seguridad estrictas del frontend
const schema = yup.object().shape({
  password: yup.string()
    .required('La contraseña es obligatoria')
    .min(8, 'Debe tener al menos 8 caracteres')
    .matches(/[A-Z]/, 'Debe contener al menos una letra mayúscula')
    .matches(/[!@#$%^&*(),.?":{}|<>]/, 'Debe contener al menos un símbolo'),
  confirmPassword: yup.string()
    .required('Debes confirmar tu contraseña')
    .oneOf([yup.ref('password')], 'Las contraseñas no coinciden')
});

const ResetPasswordPage = () => {
  // Extraemos el "token" de la URL (ej: misitio.com/reset-password/12345)
  const { token } = useParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  const onSubmit = async (data) => {
    try {
      setMessage('');
      setErrorMsg('');
      
      // Enviamos el token de la URL y la nueva contraseña al backend
      await authService.restablecerContrasena(token, data.password);
      
      setMessage('Contraseña actualizada. Redirigiendo al login...');
      setTimeout(() => navigate('/login'), 3000);
    } catch (error) {
      setErrorMsg('El enlace es inválido o ha expirado.');
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '400px', margin: '50px auto', fontFamily: 'sans-serif', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Crear Nueva Contraseña</h2>
      
      {message && <div style={{ color: 'white', backgroundColor: '#6366F1', padding: '10px', marginBottom: '15px' }}>{message}</div>}
      {errorMsg && <div style={{ color: 'white', backgroundColor: 'red', padding: '10px', marginBottom: '15px' }}>{errorMsg}</div>}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div style={{ marginBottom: '15px' }}>
          <label>Nueva Contraseña:</label><br />
          <input 
            type="password" 
            {...register('password')} 
            style={{ width: '95%', padding: '8px', marginTop: '5px' }} 
          />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.password?.message}</p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label>Confirmar Contraseña:</label><br />
          <input 
            type="password" 
            {...register('confirmPassword')} 
            style={{ width: '95%', padding: '8px', marginTop: '5px' }} 
          />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.confirmPassword?.message}</p>
        </div>

        <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#6366F1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Guardar Contraseña
        </button>
      </form>
    </div>
  );
};

export default ResetPasswordPage;