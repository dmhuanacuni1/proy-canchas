import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useParams, useNavigate, Link } from "react-router-dom";

import { authService } from "../services/authService";

const schema = yup
  .object({
    password: yup
      .string()
      .required("La contraseña es obligatoria.")
      .min(8, "Mínimo 8 caracteres.")
      .matches(/[A-Z]/, "Debe tener una mayúscula.")
      .matches(/[^A-Za-z0-9]/, "Debe tener un símbolo."),
    confirmPassword: yup
      .string()
      .oneOf([yup.ref("password")], "Las contraseñas no coinciden.")
      .required("Confirma la contraseña."),
  })
  .required();

const ResetPasswordPage = () => {
  const { token } = useParams();
  const navigate = useNavigate();
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
      await authService.restablecerContrasena(token, data.password);
      setMessage("Contraseña actualizada. Redirigiendo al inicio de sesión...");
      setTimeout(() => navigate("/login"), 3000);
    } catch (error) {
      setErrorMsg(
        !error.response
          ? "No se pudo conectar con el servidor."
          : error.response.data?.error ||
              "El enlace no es válido o ya expiró.",
      );
    }
  };

  return (
    <div className="login-container">
      <Link to="/login" className="back-link">← Volver</Link>
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">C</div>
          <h1>Restablecer contraseña</h1>
          <p>Escribe tu nueva contraseña</p>
        </div>

        {errorMsg && <div className="mensaje error">{errorMsg}</div>}
        {message && <div className="mensaje success">{message}</div>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group">
            <label>Nueva contraseña</label>
            <input
              type="password"
              placeholder="Mínimo 8 caracteres"
              {...register("password")}
            />
            {errors.password && (
              <span className="campo-error">{errors.password.message}</span>
            )}
          </div>

          <div className="form-group">
            <label>Confirmar contraseña</label>
            <input
              type="password"
              placeholder="Repite la contraseña"
              {...register("confirmPassword")}
            />
            {errors.confirmPassword && (
              <span className="campo-error">
                {errors.confirmPassword.message}
              </span>
            )}
          </div>

          <button type="submit" className="btn-primary btn-block">
            Restablecer contraseña
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

export default ResetPasswordPage;