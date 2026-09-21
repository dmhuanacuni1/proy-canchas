from flask_sqlalchemy import SQLAlchemy

# Instancia compartida. El modelo Cancha sigue en app.py; usuarios/login están en auth/.
db = SQLAlchemy()
