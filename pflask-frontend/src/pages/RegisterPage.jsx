import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Link } from "react-router-dom";

import { authService } from "../services/authService";

const schema = yup
  .object({
    nombre: yup.string().required("El nombre es obligatorio."),
    apellido: yup.string().required("El apellido es obligatorio."),
    ci: yup.string().required("El CI es obligatorio."),
    celular: yup.string().required("El celular es obligatorio."),
    email: yup
      .string()
      .required("El correo es obligatorio.")
      .email("Debe ser un correo válido."),
    username: yup.string().required("El nombre de usuario es obligatorio."),
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

const RegisterPage = () => {
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
      await authService.registro(data);
      setMessage(
        "¡Cuenta creada exitosamente! Serás redirigido al inicio de sesión...",
      );
      setTimeout(() => {
        window.location.href = "/login";
      }, 3000);
    } catch (error) {
      setErrorMsg(
        error.response?.data?.error ||
          error.response?.data?.message ||
          "No se pudo crear la cuenta. Verifica el servidor backend.",
      );
    }
  };

  return (
    <div className="login-container">
      <Link to="/login" className="back-link">← Volver</Link>
      <div className="login-card login-card-wide">
        <div className="login-header">
          <div className="login-logo">C</div>
          <h1>Crear cuenta</h1>
          <p>Regístrate para reservar canchas</p>
        </div>

        {errorMsg && <div className="mensaje error">{errorMsg}</div>}
        {message && <div className="mensaje success">{message}</div>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-row">
            <div className="form-group">
              <label>Nombre</label>
              <input type="text" placeholder="Juan" {...register("nombre")} />
              {errors.nombre && (
                <span className="campo-error">{errors.nombre.message}</span>
              )}
            </div>
            <div className="form-group">
              <label>Apellido</label>
              <input
                type="text"
                placeholder="Pérez"
                {...register("apellido")}
              />
              {errors.apellido && (
                <span className="campo-error">{errors.apellido.message}</span>
              )}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>CI</label>
              <input type="text" placeholder="1234567" {...register("ci")} />
              {errors.ci && (
                <span className="campo-error">{errors.ci.message}</span>
              )}
            </div>
            <div className="form-group">
              <label>Celular</label>
              <input
                type="text"
                placeholder="+591 70000000"
                {...register("celular")}
              />
              {errors.celular && (
                <span className="campo-error">{errors.celular.message}</span>
              )}
            </div>
          </div>

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

          <div className="form-group">
            <label>Nombre de usuario</label>
            <input
              type="text"
              placeholder="juanp123"
              {...register("username")}
            />
            {errors.username && (
              <span className="campo-error">{errors.username.message}</span>
            )}
          </div>

          <div className="form-group">
            <label>Contraseña</label>
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
            Crear cuenta
          </button>
        </form>

        <div className="login-links">
          <p>
            ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;