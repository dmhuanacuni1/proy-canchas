/**
 * color-theme.js
 * -----------------------------------------------------------
 * Aplica la paleta de colores morado/índigo (estilo panel de
 * administración de "Complejo"): fondo gris claro #F5F5F7,
 * tarjetas blancas, barra superior oscura #1E1E2E y primario
 * índigo #6366F1, inyectando variables CSS y estilos sobre
 * los elementos más comunes (botones, sidebar, badges, etc.)
 *
 * Cómo usarlo:
 * 1. Incluye este archivo antes del cierre de </body>:
 *      <script src="color-theme.js"></script>
 * 2. O pégalo directamente en la consola del navegador para
 *    previsualizar el cambio.
 * 3. Ajusta los selectores CSS de la sección "OVERRIDES" según
 *    las clases reales de tu HTML (ver comentarios).
 * -----------------------------------------------------------
 */

(function () {
  // ---------- 1. PALETA DE COLORES ----------
  const THEME = {
    primary: "#6366F1",       // morado/índigo (botones, activo en menú)
    primaryDark: "#4F46E5",   // hover del primario
    navbarBg: "#1E1E2E",      // barra superior oscura
    bgApp: "#F5F5F7",         // fondo general de la app
    bgCard: "#FFFFFF",        // fondo de tarjetas/paneles

    textPrimary: "#111827",
    textSecondary: "#6B7280",

    // Badges / etiquetas de tarifas
    normalBg: "#DBEAFE",
    normalText: "#2563EB",

    nocturnaBg: "#F3E8FF",
    nocturnaText: "#9333EA",

    finSemanaBg: "#FEF9C3",
    finSemanaText: "#CA8A04",

    border: "#E5E7EB",
  };

  // ---------- 2. INYECTAR VARIABLES CSS ----------
  const root = document.documentElement;
  Object.entries(THEME).forEach(([key, value]) => {
    root.style.setProperty(`--theme-${key}`, value);
  });

  // ---------- 3. OVERRIDES DE ESTILOS ----------
  // Ajusta estos selectores a las clases reales de tu proyecto.
  const css = `
    body {
      background-color: var(--theme-bgApp);
      color: var(--theme-textPrimary);
    }

    /* Barra superior oscura (solo navbar real) */
    .navbar, .topbar {
      background-color: var(--theme-navbarBg) !important;
      color: #FFFFFF;
    }

    /* Cabecera de página (dashboard): blanco del tema */
    header.app-header {
      background-color: var(--theme-bgCard) !important;
      color: var(--theme-textPrimary);
      border-bottom: 2px solid var(--theme-border);
    }

    /* Sidebar */
    .sidebar, .side-menu {
      background-color: var(--theme-bgCard);
      border-right: 1px solid var(--theme-border);
    }
    .sidebar a, .side-menu a {
      color: var(--theme-textSecondary);
    }
    .sidebar a.active, .side-menu a.active,
    .sidebar a:hover, .side-menu a:hover {
      background-color: color-mix(in srgb, var(--theme-primary) 12%, white);
      color: var(--theme-primary) !important;
      border-radius: 8px;
    }

    /* Botones primarios (ej. "Guardar") */
    .btn-primary, button.primary, .btn-guardar {
      background-color: var(--theme-primary) !important;
      border-color: var(--theme-primary) !important;
      color: #FFFFFF !important;
    }
    .btn-primary:hover, button.primary:hover, .btn-guardar:hover {
      background-color: var(--theme-primaryDark) !important;
    }

    /* Tarjetas / paneles */
    .card, .panel, .box {
      background-color: var(--theme-bgCard);
      border: 1px solid var(--theme-border);
      border-radius: 10px;
    }

    /* Avatar / iniciales circulares */
    .avatar, .avatar-circle {
      background-color: var(--theme-primary);
      color: #FFFFFF;
    }

    /* Badges de tarifas */
    .tarifa-normal, .badge-normal {
      background-color: var(--theme-normalBg) !important;
      color: var(--theme-normalText) !important;
    }
    .tarifa-nocturna, .badge-nocturna {
      background-color: var(--theme-nocturnaBg) !important;
      color: var(--theme-nocturnaText) !important;
    }
    .tarifa-finsemana, .badge-finsemana {
      background-color: var(--theme-finSemanaBg) !important;
      color: var(--theme-finSemanaText) !important;
    }

    /* Inputs */
    input, select, textarea {
      border: 1px solid var(--theme-border) !important;
      border-radius: 6px !important;
    }
    input:focus, select:focus, textarea:focus {
      outline: none !important;
      border-color: var(--theme-primary) !important;
      box-shadow: 0 0 0 2px color-mix(in srgb, var(--theme-primary) 25%, white) !important;
    }

    /* Texto secundario (subtítulos, descripciones) */
    .text-muted, .subtitle, .description {
      color: var(--theme-textSecondary) !important;
    }
  `;

  const styleTag = document.createElement("style");
  styleTag.id = "generated-color-theme";
  styleTag.textContent = css;
  document.head.appendChild(styleTag);

  console.log("✅ Tema de colores aplicado (morado/índigo estilo 'Complejo').");
})();