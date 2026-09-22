import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';

// 1. Definimos las reglas de validación (Yup)
const schema = yup.object().shape({
  email: yup.string().required('El correo o usuario es obligatorio'),
  password: yup.string().required('La contraseña es obligatoria')
});

const LoginPage = () => {
  const { login } = useAuth(); // Traemos la función para guardar la sesión global
  const navigate = useNavigate(); // Herramienta para cambiar de página
  const [errorMsg, setErrorMsg] = useState('');

  // 2. Configuramos React Hook Form con nuestro esquema de Yup
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  // 3. Función que se ejecuta al enviar el formulario
  const onSubmit = async (data) => {
    try {
      setErrorMsg('');
      // Llamamos a nuestra Capa de Lógica (authService)
      const userData = await authService.login(data);
      
      // Guardamos al usuario en el Contexto Global
      login(userData);
      
      // Redirigimos según el rol (Caso de uso 2)
      navigate('/dashboard');
    } catch (error) {
      if (!error.response) {
        setErrorMsg('No se pudo conectar con el servidor. ¿Está Flask corriendo en el puerto 5000?');
      } else if (error.response.status === 401) {
        setErrorMsg(error.response.data?.error || 'Credenciales incorrectas');
      } else {
        setErrorMsg(error.response.data?.error || 'Error al iniciar sesión');
      }
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '400px', margin: '50px auto', fontFamily: 'sans-serif', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Iniciar Sesión</h2>
      
      {/* Mensaje de error general si falla el backend */}
      {errorMsg && <div style={{ color: 'white', backgroundColor: 'red', padding: '10px', marginBottom: '15px' }}>{errorMsg}</div>}
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div style={{ marginBottom: '15px' }}>
          <label>Correo o usuario:</label><br />
          <input 
            type="text" 
            {...register('email')}
            style={{ width: '95%', padding: '8px', marginTop: '5px' }} 
          />
          {/* Mensaje de error de validación */}
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.email?.message}</p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label>Contraseña:</label><br />
          <input 
            type="password" 
            {...register('password')} 
            style={{ width: '95%', padding: '8px', marginTop: '5px' }} 
          />
          <p style={{ color: 'red', margin: '5px 0 0 0', fontSize: '14px' }}>{errors.password?.message}</p>
        </div>

        <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#007BFF', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Ingresar
        </button>
        <div style={{ textAlign: 'center', marginTop: '15px' }}>
          <Link to="/forgot-password" style={{ color: '#007BFF', textDecoration: 'none', fontSize: '14px' }}>
            ¿Olvidaste tu contraseña?
          </Link>
        </div>
        <div style={{ textAlign: 'center', marginTop: '10px' }}>
            <Link to="/register" style={{ color: '#28a745', textDecoration: 'none', fontSize: '14px', fontWeight: 'bold' }}>
            ¿No tienes cuenta? Regístrate aquí
            </Link>
        </div>
      </form>
    </div>
  );
};

export default LoginPage;