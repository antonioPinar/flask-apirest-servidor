from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from config import Config
from modelos.tabla import db
from rutas.tablas import tablas_bp

def create_app():
    app = Flask(__name__)
    
    # Configuración de la base de datos
    app.config.from_object(Config)

    # Inicializamos SQLAlchemy con la app
    db.init_app(app)

    # Registramos el Blueprint para las rutas de tablas
    app.register_blueprint(tablas_bp)

    return app

# Instanciar la aplicación y la API
app = create_app()
api = Api(app)

# Crear las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
