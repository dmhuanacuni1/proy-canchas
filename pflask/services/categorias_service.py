from extensions import db
from models.categoria import Categoria
from models.cancha import Cancha


def listar_categorias():
    return Categoria.query.order_by(Categoria.id_categoria.asc()).all()


def obtener_categoria_por_id(id_categoria):
    categoria = db.session.get(Categoria, id_categoria)
    if not categoria:
        raise ValueError("La categoría no existe.")
    return categoria


def crear_categoria(datos):
    if Categoria.query.filter_by(nombre=datos["nombre"]).first():
        raise ValueError("Ya existe una categoría con ese nombre.")

    nueva = Categoria(
        nombre=datos["nombre"],
        descripcion=datos.get("descripcion"),
    )
    db.session.add(nueva)
    db.session.commit()
    return nueva


def modificar_categoria(id_categoria, datos):
    categoria = obtener_categoria_por_id(id_categoria)

    if "nombre" in datos:
        otra = Categoria.query.filter(
            Categoria.nombre == datos["nombre"],
            Categoria.id_categoria != id_categoria,
        ).first()
        if otra:
            raise ValueError("Ya existe otra categoría con ese nombre.")
        categoria.nombre = datos["nombre"]

    if "descripcion" in datos:
        categoria.descripcion = datos["descripcion"]

    db.session.commit()
    return categoria


def eliminar_categoria(id_categoria):
    categoria = obtener_categoria_por_id(id_categoria)

    # PostgreSQL tiene ON DELETE RESTRICT para cancha.id_categoria.
    if Cancha.query.filter_by(id_categoria=id_categoria).first():
        raise ValueError(
            "No se puede eliminar la categoría porque tiene canchas asociadas."
        )

    db.session.delete(categoria)
    db.session.commit()
