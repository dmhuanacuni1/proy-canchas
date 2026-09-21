=========================
===== PARA INSTALAR =====
=========================

-En la carpeta pflask, con el entorno virtual activado, instala lo nuevo de esta rama:

pip install -r requirements.txt

(Eso instala PyJWT, que es lo unico extra respecto a lo que ya tenian. No hace falta npm install).

Reinicia Flask y el frontend como siempre.


====================================
===== PARA PROBAR LOS USUARIOS =====
====================================

-Si quieren probar los tres roles, ejecuten esto en PostgreSQL (un administrador, un cliente y un empleado). El empleado necesita un administrador, por eso el admin va primero.

INSERT INTO persona (nombre, apellido, ci, celular, email) VALUES 
('Juan', 'Perez', '1234567', '77712345', 'juan@example.com'), 
('Carlos', 'Lopez', '1122334', '77711223', 'carlos@example.com'), 
('Luis', 'Ramirez', '3344556', '77733445', 'luis@example.com');

INSERT INTO usuario (username, contrasena, rol, id_persona) VALUES 
('admin1', 'pass1', 'administrador', (SELECT id_persona FROM persona WHERE ci='1234567')), 
('cliente1', 'pass3', 'cliente', (SELECT id_persona FROM persona WHERE ci='1122334')), 
('empleado1', 'pass5', 'empleado', (SELECT id_persona FROM persona WHERE ci='3344556'));

INSERT INTO administrador (nivel_acceso, fecha_designado, area_responsabilidad, id_usuario) VALUES 
('total', '2024-01-01', 'General', (SELECT id_usuario FROM usuario WHERE username='admin1'));

INSERT INTO cliente (fecha_afiliacion, deporte_pref, historial_reservas, id_usuario) VALUES 
('2024-03-01', 'Futbol', 'Sin reservas', (SELECT id_usuario FROM usuario WHERE username='cliente1'));

INSERT INTO empleado (cargo, turno_laboral, fecha_contratacion, salario, id_administrador, id_usuario) VALUES 
('Mantenimiento', 'Manana', '2024-04-01', 2500.00, (SELECT id_administrador FROM administrador WHERE id_usuario=(SELECT id_usuario FROM usuario WHERE username='admin1')), (SELECT id_usuario FROM usuario WHERE username='empleado1'));


Para entrar:
Administrador: juan@example.com o admin1 / pass1 Cliente: carlos@example.com o cliente1 / pass3 Empleado: luis@example.com o empleado1 / pass5
El registro por la web solo crea clientes. El panel de editar y borrar usuarios sale con la cuenta de administrador.


=====================================================
===== Para probar la recuperacion de contraseña =====
=====================================================
-Recuperar contraseña no pide instalar nada mas. Usen un correo que exista en persona. El enlace aparece en la consola de Flask. Si quieren que llegue un Gmail de verdad, 

1. Crear el archivo pflask/auth/config/correo.env (si no existe).
2. Pegar exactamente este contenido en la carpeta correo.env:

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=canchasrecuperar@gmail.com
SMTP_PASSWORD=wwiy vadd ousl dmwd
SMTP_FROM=canchasrecuperar@gmail.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
FRONTEND_URL=http://localhost:5173
SECRET_KEY=dev-secret-canchas-local

3. Guardar y reiniciar Flask.
