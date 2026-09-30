import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useNavigate, Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { authService } from "../services/authService";

const schema = yup
  .object({
    email: yup.string().required("El correo es obligatorio."),
    password: yup.string().required("La contraseña es obligatoria."),
  })
  .required();

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
  });

  const [errorMsg, setErrorMsg] = useState("");

  const onSubmit = async (data) => {
    setErrorMsg("");
    try {
      const userData = await authService.login(data);
      login(userData);
      navigate("/dashboard");
    } catch (error) {
      if (!error.response) {
        setErrorMsg(
          "No se pudo conectar con el servidor. ¿Está Flask corriendo en el puerto 5000?",
        );
      } else if (error.response.status === 401) {
        setErrorMsg("Credenciales inválidas. Inténtalo de nuevo.");
      } else {
        setErrorMsg(
          error.response.data?.error || "Error al iniciar sesión.",
        );
      }
    }
  };

  return (
    <div className="login-container">
      <Link to="/" className="back-link">← Volver</Link>
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">C</div>
          <h1>Iniciar sesión</h1>
          <p>Accede al sistema de gestión de canchas</p>
        </div>

        {errorMsg && <div className="mensaje error">{errorMsg}</div>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group">
            <label>Correo o usuario</label>
            <input type="text" placeholder="correo@ejemplo.com" {...register("email")} />
            {errors.email && <span className="campo-error">{errors.email.message}</span>}
          </div>

          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              placeholder="••••••••"
              {...register("password")}
            />
            {errors.password && (
              <span className="campo-error">{errors.password.message}</span>
            )}
          </div>

          <button type="submit" className="btn-primary btn-block">
            Iniciar sesión
          </button>
        </form>

        <div className="login-links">
          <Link to="/forgot-password">¿Olvidaste tu contraseña?</Link>
          <p style={{ marginTop: "6px" }}>
            ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;