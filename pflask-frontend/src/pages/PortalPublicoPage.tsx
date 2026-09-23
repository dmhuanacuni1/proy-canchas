import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Evento } from "../types/evento.types";
import { EventoCard } from "../components/eventos/EventoCard";
import { EventoDetalleModal } from "../components/eventos/EventoDetalleModal";
import { useEventos } from "../hooks/useEventos";
import "../App.css";

const PortalPublicoPage: React.FC = () => {
  const navigate = useNavigate();

  const {
    eventos,
    loading,
    error,
  } = useEventos();

  const [eventoSeleccionado, setEventoSeleccionado] =
    useState<Evento | null>(null);

  const [modalAbierto, setModalAbierto] =
    useState(false);

  /*
   * El portal público muestra únicamente
   * eventos de tipo Servicio Social.
   */
  const eventosPublicos = eventos.filter(
    (evento) =>
      evento.tipo_evento?.trim().toLowerCase() ===
      "servicio social"
  );

  const handleVerDetalles = (evento: Evento) => {
    setEventoSeleccionado(evento);
    setModalAbierto(true);
  };

  const handleCerrarModal = () => {
    setModalAbierto(false);
    setEventoSeleccionado(null);
  };

  return (
    <div className="portal-publico">

      {/* ============================================
          ENCABEZADO PÚBLICO
          ============================================ */}
      <header className="portal-header">
        <div className="portal-header-contenido">

          <div className="portal-logo">
            <h1>
              RESERVA DE CANCHAS
            </h1>

            <p>
              Eventos, actividades deportivas y servicios
              sociales para nuestra comunidad.
            </p>
          </div>

          <div className="portal-auth-buttons">
            <button
              className="btn-secondary"
              onClick={() => navigate("/login")}
            >
              Iniciar sesión
            </button>

            <button
              className="btn-primary"
              onClick={() => navigate("/register")}
            >
              Registrarse
            </button>
          </div>

        </div>
      </header>

      {/* ============================================
          PRESENTACIÓN
          ============================================ */}
      <main className="portal-contenido">

        <section className="portal-hero">
          <div className="portal-hero-texto">

            <span className="portal-etiqueta">
              COMUNIDAD Y DEPORTE
            </span>

            <h2>
              Eventos y Servicios Sociales
            </h2>

            <p>
              Conoce las actividades comunitarias,
              jornadas solidarias y eventos sociales
              organizados en nuestras instalaciones
              deportivas.
            </p>

            <div className="portal-hero-acciones">

              <button
                className="btn-primary"
                onClick={() => {
                  document
                    .getElementById("eventos-publicos")
                    ?.scrollIntoView({
                      behavior: "smooth",
                    });
                }}
              >
                Ver eventos
              </button>

              <button
                className="btn-secondary"
                onClick={() => navigate("/login")}
              >
                Acceder al sistema
              </button>

            </div>
          </div>

          <div className="portal-hero-icono">
            🏟️
          </div>
        </section>

        {/* ============================================
            EVENTOS SOCIALES
            ============================================ */}
        <section
          id="eventos-publicos"
          className="portal-eventos"
        >
          <div className="portal-seccion-header">
            <div>
              <h2 className="section-title">
                Próximos Servicios Sociales
              </h2>

              <p>
                Actividades abiertas a la comunidad
                organizadas en nuestras canchas.
              </p>
            </div>
          </div>

          {loading && (
            <div className="cargando">
              Cargando eventos...
            </div>
          )}

          {error && (
            <div className="mensaje error">
              {error}
            </div>
          )}

          {!loading &&
            !error &&
            eventosPublicos.length === 0 && (
              <div className="estado-vacio">
                No existen servicios sociales
                programados actualmente.
              </div>
            )}

          {!loading &&
            !error &&
            eventosPublicos.length > 0 && (
              <div className="portal-eventos-grid">

                {eventosPublicos.map((evento) => (
                  <EventoCard
                    key={evento.id_evento}
                    evento={evento}
                    onVerDetalles={handleVerDetalles}
                  />
                ))}

              </div>
            )}
        </section>

        {/* ============================================
            LLAMADO A REGISTRO
            ============================================ */}
        <section className="portal-registro">

          <div>
            <h2>
              ¿Quieres reservar una cancha?
            </h2>

            <p>
              Regístrate para consultar canchas
              disponibles y realizar tus reservas.
            </p>
          </div>

          <div className="portal-registro-botones">

            <button
              className="btn-primary"
              onClick={() => navigate("/register")}
            >
              Crear una cuenta
            </button>

            <button
              className="btn-secondary"
              onClick={() => navigate("/login")}
            >
              Ya tengo una cuenta
            </button>

          </div>

        </section>

      </main>

      {/* ============================================
          FOOTER
          ============================================ */}
      <footer className="portal-footer">
        <p>
            RESERVA DE CANCHAS © 2026. Todos los derechos reservados.
        </p>

        <span>
            Plataforma para reservas, eventos y servicios sociales.
        </span>
      </footer>

      {/* ============================================
          DETALLE DEL EVENTO
          ============================================ */}
      <EventoDetalleModal
        evento={eventoSeleccionado}
        isOpen={modalAbierto}
        onClose={handleCerrarModal}
      />

    </div>
  );
};

export default PortalPublicoPage;