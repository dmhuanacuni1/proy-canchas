import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Link } from "react-router-dom";

import { authService } from "../services/authService";

const schema = yup
  .object({
    email: yup
      .string()
      .required("El correo es obligatorio.")
      .email("Debe ser un correo válido."),
  })
  .required();

const ForgotPasswordPage = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: yupResolver(schema) });

  const [message, setMessage] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const onSubmit = async (data) => {
    setMessage("");
    setErrorMsg("");
    try {
      await authService.solicitarRecuperacion(data.email);
      setMessage(
        "Si el correo existe, se envió un enlace de recuperación. Revisa tu bandeja de entrada.",
      );
    } catch (error) {
      if (!error.response) {
        setErrorMsg(
          "No se pudo conectar con el servidor. ¿Está Flask corriendo en el puerto 5000?",
        );
      } else {
        setErrorMsg(
          error.response.data?.error || "Error al solicitar la recuperación.",
        );
      }
    }
  };

  return (
    <div className="login-container">
      <Link to="/login" className="back-link">← Volver</Link>
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">C</div>
          <h1>Recuperar contraseña</h1>
          <p>Te enviaremos un enlace para restablecer tu contraseña</p>
        </div>

        {errorMsg && <div className="mensaje error">{errorMsg}</div>}
        {message && <div className="mensaje success">{message}</div>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group">
            <label>Correo</label>
            <input
              type="email"
              placeholder="correo@ejemplo.com"
              {...register("email")}
            />
            {errors.email && (
              <span className="campo-error">{errors.email.message}</span>
            )}
          </div>

          <button type="submit" className="btn-primary btn-block">
            Enviar enlace
          </button>
        </form>

        <div className="login-links">
          <p>
            <Link to="/login">← Volver al inicio de sesión</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;