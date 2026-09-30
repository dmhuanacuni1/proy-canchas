def validar_datos_categoria(data, parcial=False):
    """
    Valida y limpia los datos de entrada para crear/modificar una categoría.
    Lanza ValueError con un mensaje claro si algo es inválido.
    Devuelve un diccionario con los datos ya limpios (solo los campos
    presentes, si parcial=True).
    """
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    if not data:
        raise ValueError("El cuerpo de la solicitud no puede estar vacío.")

    resultado = {}

    if not parcial or "nombre" in data:
        nombre = data.get("nombre")

        if not isinstance(nombre, str):
            raise ValueError("El campo nombre debe ser un texto válido.")

        nombre = nombre.strip()

        if not nombre:
            raise ValueError("El campo nombre es obligatorio.")

        if len(nombre) > 50:
            raise ValueError("El nombre de la categoría no puede superar 50 caracteres.")

        resultado["nombre"] = nombre

    if not parcial or "descripcion" in data:
        descripcion = data.get("descripcion")

        if descripcion is not None and not isinstance(descripcion, str):
            raise ValueError("La descripción debe ser un texto válido o null.")

        resultado["descripcion"] = descripcion.strip() if descripcion else None

    return resultado
