# Flask API REST Server

Este proyecto es un servidor API RESTful construido con Flask, diseñado para gestionar modelos y rutas sobre tablas de surf en una arquitectura de microservicios. Proporciona una base para desarrollar APIs ligeras y escalables.

## Características

- **Flask Framework**: Usa Flask como microframework para manejar las peticiones HTTP.
- **Modularización**: Separación clara de modelos, rutas y configuración para facilitar la escalabilidad y el mantenimiento.
- **Base de datos**: Configuración de base de datos manejada con SQLAlchemy (u otro ORM según lo requerido).
- **Configuración personalizada**: El archivo `config.py` permite ajustar variables como el entorno (desarrollo, producción) y las conexiones de base de datos.
  
## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```bash
flask-apirest-servidor/
│
├── app.py                # Punto de entrada de la aplicación
├── config.py             # Configuración global de la aplicación
├── database.py           # Configuración de la conexión a la base de datos
├── modelos/              # Definición de modelos de datos
│   └── modelo_ejemplo.py
├── rutas/                # Definición de rutas de la API
│   └── rutas_ejemplo.py
└── __init__.py           # Inicialización de la aplicación Flask
