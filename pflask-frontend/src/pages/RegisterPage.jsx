import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { authService } from '../services/authService';
import { Link, useNavigate } from 'react-router-dom';

const schema = yup.object().shape({
  nombre: yup.string().required('El nombre es obligatorio'),
  email: yup.string().email('Debe ser un correo válido').required('El correo es obligatorio'),
  password: yup.string()
    .required('La contraseña es obligatoria')
    .min(8, 'Debe tener al menos 8 caracteres')
    .matches(/[A-Z]/, 'Debe contener al menos una letra mayúscula')
    .matches(/[!@#$%^&*(),.?":{}|<>]/, 'Debe contener al menos un símbolo'),
  confirmPassword: yup.string()
    .required('Debes confirmar tu contraseña')
    .oneOf([yup.ref('password')], 'Las contraseñas no coinciden')
});

const RegisterPage = () => {
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  const onSubmit = async (data) => {
    try {
      setMessage('');
      setErrorMsg('');
      
      // Enviamos los datos (menos confirmPassword, que solo sirve para el frontend)
      const userData = { nombre: data.nombre, email: data.email, password: data.password };
      await authService.registro(userData);
      
      setMessage('¡Cuenta creada exitosamente! Redirigiendo al login...');
      setTimeout(() => navigate('/login'), 3000);
    } catch (error) {
      setErrorMsg('Error al registrar el usuario. Intenta con otro correo.');
    }
  };

  return (
    <div style={{ padding: '30px', maxWidth: '400px', margin: '40px auto', fontFamily: 'sans-serif', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Crear una Cuenta</h2>

      {message && <div style={{ color: 'white', backgroundColor: '#6366F1', padding: '10px', marginBottom: '15px' }}>{message}</div>}
      {errorMsg && <div style={{ color: 'white', backgroundColor: 'red', padding: '10px', marginBottom: '15px' }}>{errorMsg}</div>}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div style={{ marginBottom: '15px' }}>
          <label>Nombre Completo:</label><br />
          <input type="text" {...register('nombre')} style={{ width: '95%', padding: '8px', marginTop: '5px' }} />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.nombre?.message}</p>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Correo Electrónico:</label><br />
          <input type="email" {...register('email')} style={{ width: '95%', padding: '8px', marginTop: '5px' }} />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.email?.message}</p>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Contraseña:</label><br />
          <input type="password" {...register('password')} style={{ width: '95%', padding: '8px', marginTop: '5px' }} />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.password?.message}</p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label>Confirmar Contraseña:</label><br />
          <input type="password" {...register('confirmPassword')} style={{ width: '95%', padding: '8px', marginTop: '5px' }} />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.confirmPassword?.message}</p>
        </div>

        <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#6366F1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Registrarse
        </button>
      </form>
      
      <div style={{ textAlign: 'center', marginTop: '15px' }}>
        <Link to="/login" style={{ color: '#6366F1', textDecoration: 'none', fontSize: '14px' }}>
          ¿Ya tienes cuenta? Inicia sesión
        </Link>
      </div>
    </div>
  );
};

export default RegisterPage;