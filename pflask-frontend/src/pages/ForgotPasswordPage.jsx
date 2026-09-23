import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { authService } from '../services/authService';
import { Link } from 'react-router-dom';

const schema = yup.object().shape({
  email: yup.string().email('Debe ser un correo válido').required('El correo es obligatorio'),
});

const ForgotPasswordPage = () => {
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  const onSubmit = async (data) => {
    try {
      setMessage('');
      setErrorMsg('');
      
      // Llamamos al servicio para solicitar la recuperación
      await authService.solicitarRecuperacion(data.email);
      
      // Mensaje genérico por seguridad (no confirmar si el correo existe o no)
      setMessage('Si el correo está registrado, recibirás un enlace de recuperación pronto.');
    } catch (error) {
      if (!error.response) {
        setErrorMsg('Error de conexión con el servidor. Inténtalo más tarde.');
      } else {
        setErrorMsg(error.response.data?.error || 'No se pudo enviar el correo de recuperación.');
      }
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '400px', margin: '50px auto', fontFamily: 'sans-serif', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Recuperar Contraseña</h2>
      <p style={{ fontSize: '14px', color: '#6b7280' }}>Ingresa tu correo y te enviaremos las instrucciones para restablecer tu acceso.</p>

      {message && <div style={{ color: 'white', backgroundColor: '#6366F1', padding: '10px', marginBottom: '15px' }}>{message}</div>}
      {errorMsg && <div style={{ color: 'white', backgroundColor: 'red', padding: '10px', marginBottom: '15px' }}>{errorMsg}</div>}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div style={{ marginBottom: '20px' }}>
          <label>Correo Electrónico:</label><br />
          <input 
            type="email" 
            {...register('email')} 
            style={{ width: '95%', padding: '8px', marginTop: '5px' }} 
          />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.email?.message}</p>
        </div>

        <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#6366F1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginBottom: '15px' }}>
          Enviar enlace de recuperación
        </button>
      </form>
      
      <div style={{ textAlign: 'center', marginTop: '10px' }}>
        <Link to="/login" style={{ color: '#6366F1', textDecoration: 'none', fontSize: '14px' }}>
          ← Volver al Login
        </Link>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;