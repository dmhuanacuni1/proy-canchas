# Proyecto Canchas



## IMPORTANTE: ¡siempre reinstalar dependencias!

`node_modules` y el entorno virtual **no viajan por git**. Después de cada `git pull` (o al clonar la primera vez), ejecutar:

```
cd pflask-frontend
npm install
```

y en el backend:

```
cd pflask
pip install -r requirements.txt
```

Si no lo haces, el frontend muestra errores tipo `Failed to resolve import "..."` (por ejemplo `react-hook-form`, `yup`, `@hookform/resolvers`) y el backend `ModuleNotFoundError` (por ejemplo `jwt`).

