# db/

Carpeta para scripts SQL, migraciones y respaldos de la base de datos.

- `schema.sql` — definición de tablas creadas en PostgreSQL.
- `migraciones/` — scripts incremental de cambios (ALTER TABLE, etc.).
- `backups/` — respaldos generados manualmente.

Convención recomendada para migraciones:

```
migraciones/
  001_inicial.sql
  002_agregar_campo.sql
  ...
```

La conexión se define en `pflask/.env` con `DATABASE_URL`.