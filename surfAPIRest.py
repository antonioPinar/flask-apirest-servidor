from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tablas_de_surf.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos SQLAlchemy
db = SQLAlchemy(app)
api = Api(app)

# Definir las opciones válidas para los campos 'tipo' y 'quillas'
TIPOS_VALIDOS = ['Shortboard', 'Longboard', 'Fish', 'Funboard', 'Gun']
QUILLAS_VALIDAS = ['Tri-fin', 'Quad', 'Single']

# Modelo de la tabla de surf
class TablaDeSurfModelo(db.Model):
    __tablename__ = 'tablas_de_surf'
    
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    nombre = db.Column(db.String(80), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    longitud = db.Column(db.String(10), nullable=False)
    ancho = db.Column(db.String(10), nullable=False)
    espesor = db.Column(db.String(10), nullable=False)
    volumen = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    material = db.Column(db.String(20), nullable=False)
    quillas = db.Column(db.String(50), nullable=False)  # Modificado para aceptar hasta 3 opciones de quillas
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        """Convertir el objeto a un diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'marca': self.marca,
            'longitud': self.longitud,
            'ancho': self.ancho,
            'espesor': self.espesor,
            'volumen': self.volumen,
            'tipo': self.tipo,
            'material': self.material,
            'quillas': self.quillas.split(','),  # Convertir de string a lista de quillas
            'precio': self.precio,
            'estado': self.estado,
            'descripcion': self.descripcion
        }

# Clase Tabla de Surf
class TablaDeSurf(Resource):
    def get(self, tabla_id=None):
        """ Obtener una tabla de surf por ID o todas las tablas """
        if tabla_id is None:
            tablas = TablaDeSurfModelo.query.all()
            return jsonify([tabla.to_dict() for tabla in tablas])
        else:
            tabla = TablaDeSurfModelo.query.get(tabla_id)
            if tabla:
                return jsonify(tabla.to_dict())
            return {'message': 'Tabla de surf no encontrada'}, 404

    def post(self):
        """ Crear una nueva tabla de surf """
        data = request.json
        
        # Validación del campo 'tipo'
        tipo = data.get('tipo')
        if tipo not in TIPOS_VALIDOS:
            return {'message': f'Tipo inválido. Los tipos válidos son: {", ".join(TIPOS_VALIDOS)}'}, 400
        
        # Validación del campo 'quillas'
        quillas = data.get('quillas', [])
        if len(quillas) > 3:
            return {'message': 'Solo se permiten hasta 3 opciones de quillas'}, 400
        for quilla in quillas:
            if quilla not in QUILLAS_VALIDAS:
                return {'message': f'Distribución de quilla inválida. Las opciones válidas son: {", ".join(QUILLAS_VALIDAS)}'}, 400

        nueva_tabla = TablaDeSurfModelo(
            nombre=data['nombre'],
            marca=data['marca'],
            longitud=data['longitud'],
            ancho=data['ancho'],
            espesor=data['espesor'],
            volumen=data['volumen'],
            tipo=tipo,  # Solo se asigna si es válido
            material=data['material'],
            quillas=",".join(quillas),  # Guardamos como una cadena separada por comas
            precio=data['precio'],
            estado=data['estado'],
            descripcion=data.get('descripcion')  # Puede ser opcional
        )

        db.session.add(nueva_tabla)
        db.session.commit()
        return {'message': 'Tabla de surf creada correctamente', 'data': nueva_tabla.to_dict()}, 201

    def put(self, tabla_id):
        """ Actualizar una tabla de surf existente """
        tabla = TablaDeSurfModelo.query.get(tabla_id)
        if not tabla:
            return {'message': 'Tabla de surf no encontrada'}, 404

        data = request.json

        # Validación del campo 'tipo'
        tipo = data.get('tipo', tabla.tipo)
        if tipo not in TIPOS_VALIDOS:
            return {'message': f'Tipo inválido. Los tipos válidos son: {", ".join(TIPOS_VALIDOS)}'}, 400
        
        # Validación del campo 'quillas'
        quillas = data.get('quillas', tabla.quillas.split(','))
        if len(quillas) > 3:
            return {'message': 'Solo es posible que tenga 3 opciones de quillas'}, 400
        for quilla in quillas:
            if quilla not in QUILLAS_VALIDAS:
                return {'message': f'Distribución de quilla inválida. Las opciones válidas son: {", ".join(QUILLAS_VALIDAS)}'}, 400

        tabla.nombre = data.get('nombre', tabla.nombre)
        tabla.marca = data.get('marca', tabla.marca)
        tabla.longitud = data.get('longitud', tabla.longitud)
        tabla.ancho = data.get('ancho', tabla.ancho)
        tabla.espesor = data.get('espesor', tabla.espesor)
        tabla.volumen = data.get('volumen', tabla.volumen)
        tabla.tipo = tipo  # Actualizar el tipo solo si es válido
        tabla.material = data.get('material', tabla.material)
        tabla.quillas = ",".join(quillas)  # Guardar como cadena separada por comas
        tabla.precio = data.get('precio', tabla.precio)
        tabla.estado = data.get('estado', tabla.estado)
        tabla.descripcion = data.get('descripcion', tabla.descripcion)

        db.session.commit()
        return {'message': 'Tabla de surf actualizada correctamente', 'data': tabla.to_dict()}, 200

    def delete(self, tabla_id):
        """ Eliminar una tabla de surf """
        tabla = TablaDeSurfModelo.query.get(tabla_id)
        if not tabla:
            return {'message': 'Tabla de surf no encontrada'}, 404

        db.session.delete(tabla)
        db.session.commit()
        return {'message': 'Tabla de surf eliminada correctamente'}, 200

# Definir las rutas de la API
api.add_resource(TablaDeSurf, '/tablas', '/tablas/<int:tabla_id>')

# Crear las tablas en la base de datos (si no existen)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
