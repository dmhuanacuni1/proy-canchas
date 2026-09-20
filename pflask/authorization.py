from functools import wraps
from flask import jsonify


# ==========================================================
# ROLES DEL SISTEMA
# ==========================================================

ROL_ADMINISTRADOR = "administrador"
ROL_CLIENTE = "cliente"
ROL_EMPLEADO = "empleado"


# ==========================================================
# PERMISOS
# ==========================================================

PERMISOS = {
    # -------------------------
    # CATEGORÍAS
    # -------------------------
    "ver_categorias": {
        ROL_ADMINISTRADOR,
        ROL_CLIENTE,
    },

    "crear_categoria": {
        ROL_ADMINISTRADOR,
    },

    "modificar_categoria": {
        ROL_ADMINISTRADOR,
    },

    "eliminar_categoria": {
        ROL_ADMINISTRADOR,
    },

    # -------------------------
    # CANCHAS
    # -------------------------
    "ver_canchas": {
        ROL_ADMINISTRADOR,
        ROL_CLIENTE,
    },

    "crear_cancha": {
        ROL_ADMINISTRADOR,
    },

    "modificar_cancha": {
        ROL_ADMINISTRADOR,
    },

    "eliminar_cancha": {
        ROL_ADMINISTRADOR,
    },

    "cambiar_estado_cancha": {
        ROL_ADMINISTRADOR,
    },
}


# ==========================================================
# DECORADOR DE AUTORIZACIÓN
# ==========================================================

def requiere_permiso(nombre_permiso):
    """
    Verifica si el rol del usuario actual tiene permiso
    para realizar una operación.

    La obtención del usuario autenticado se conectará
    posteriormente con el sistema JWT.
    """

    if nombre_permiso not in PERMISOS:
        raise ValueError(
            f"El permiso '{nombre_permiso}' no está definido."
        )

    roles_permitidos = PERMISOS[nombre_permiso]

    def decorador(funcion):

        @wraps(funcion)
        def wrapper(*args, **kwargs):

            # ------------------------------------------------
            # TEMPORAL
            #
            # Mientras no integremos autenticación, esta
            # función no obtiene todavía un usuario real.
            #
            # NO se debe utilizar todavía en producción.
            # ------------------------------------------------

            rol_actual = obtener_rol_actual()

            if rol_actual not in roles_permitidos:
                return jsonify({
                    "error": "No tienes permisos para realizar esta operación."
                }), 403

            return funcion(*args, **kwargs)

        return wrapper

    return decorador


# ==========================================================
# USUARIO ACTUAL
# ==========================================================

def obtener_rol_actual():
    """
    Punto de integración con JWT.

    Esta función será conectada posteriormente con
    auth.security.require_auth().
    """

    raise RuntimeError(
        "La autenticación todavía no está integrada."
    )