from flask import Blueprint, request, jsonify
from modelos.tabla import TablaDeSurfModelo, db

# Crear un Blueprint para las rutas de tablas
tablas_bp = Blueprint('tablas', __name__)

# Constantes para validaciones
TIPOS_VALIDOS = ['shortboard', 'longboard', 'fish', 'funboard', 'gun']
QUILLAS_VALIDAS = ['tri-fin', 'quad', 'single']


# Funciones auxiliares
#Valida si el tipo proporcionado es válido.
def validar_tipo(tipo):
    tipo = tipo.lower()
    if tipo not in TIPOS_VALIDOS:
        return False, [{'message': f'Tipo inválido. Los tipos válidos son: {", ".join(TIPOS_VALIDOS)}'}, 400]
    return True, None


#Valida si las quillas proporcionadas son válidas.
def validar_quillas(quillas):
    if not isinstance(quillas, list):
        return False, [{'message': 'El campo quillas debe ser una lista'}, 400]
    # Limpiar la lista: eliminar espacios y convertir a minúsculas
    quillas = [quilla.lower() for quilla in quillas]
    # Verifica si hay elementos duplicados
    if len(quillas) != len(set(quillas)):
        return False, [{'message': 'No se permiten opciones de quillas duplicadas'}, 400]
    # Verifica si hay más de 3 quillas
    if len(quillas) > 3:
        return False, [{'message': 'Solo se permiten hasta 3 opciones de quillas'}, 400]
    # Verifica que las quillas sean válidas
    for quilla in quillas:
        if quilla not in QUILLAS_VALIDAS:
            return False, [{'message': f'Quilla inválida. Las opciones válidas son: {", ".join(QUILLAS_VALIDAS)}'}, 400]
    
    return True, None


# Rutas

#Obtener todas las tablas o una por ID.
@tablas_bp.route('/tablas', methods=['GET'])
@tablas_bp.route('/tablas/<int:tabla_id>', methods=['GET'])
def get_tablas(tabla_id=None):
    if tabla_id:
        tabla = TablaDeSurfModelo.query.get(tabla_id)
        if tabla:
            return jsonify(tabla.to_dict()), 200
        return {'message': 'Tabla de surf no encontrada'}, 404
    tablas = TablaDeSurfModelo.query.all()
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Obtener tablas filtradas por tipo.
@tablas_bp.route('/tablas/tipo/<string:tipo>', methods=['GET'])
def get_tablas_por_tipo(tipo):
    valido, error = validar_tipo(tipo)
    if not valido:
        return error

    tablas = TablaDeSurfModelo.query.filter_by(tipo=tipo).all()
    if not tablas:
        return {'message': 'No se encontraron tablas de surf con ese tipo'}, 404
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Obtener tablas filtradas por marca.
@tablas_bp.route('/tablas/marca/<string:marca>', methods=['GET'])
def get_tablas_por_marca(marca):
    tablas = TablaDeSurfModelo.query.filter_by(marca=marca).all()
    if not tablas:
        return {'message': 'No se encontraron tablas de surf con esa marca'}, 404
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Obtener tablas filtradas por quillas.
@tablas_bp.route('/tablas/quillas/<string:quillas>', methods=['GET'])
def get_tablas_por_quillas(quillas):
    if quillas not in QUILLAS_VALIDAS:
        return {'message': f'Quillas inválidas. Las opciones válidas son: {", ".join(QUILLAS_VALIDAS)}'}, 400

    tablas = TablaDeSurfModelo.query.filter(TablaDeSurfModelo.quillas.contains(quillas)).all()
    if not tablas:
        return {'message': 'No se encontraron tablas de surf con esas quillas'}, 404
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Crear una nueva tabla de surf.
@tablas_bp.route('/tablas', methods=['POST'])
def create_tabla():
    data = request.json

    # Validar tipo
    tipo = data.get('tipo')
    valido, error = validar_tipo(tipo)
    if not valido:
        return error

    # Validar quillas
    quillas = data.get('quillas', [])
    valido, error = validar_quillas(quillas)
    if not valido:
        return error

    nueva_tabla = TablaDeSurfModelo(
        nombre=data['nombre'],
        marca=data['marca'],
        longitud=data['longitud'],
        ancho=data['ancho'],
        espesor=data['espesor'],
        volumen=data['volumen'],
        tipo=tipo,
        material=data['material'],
        quillas=",".join(quillas),
        precio=data['precio'],
        estado=data['estado'],
        descripcion=data.get('descripcion')
    )

    db.session.add(nueva_tabla)
    db.session.commit()
    return {'message': 'Tabla de surf creada correctamente', 'data': nueva_tabla.to_dict()}, 201

#Actualizar una tabla de surf existente.
@tablas_bp.route('/tablas/<int:tabla_id>', methods=['PUT'])
def update_tabla(tabla_id):
    tabla = TablaDeSurfModelo.query.get(tabla_id)
    if not tabla:
        return {'message': 'Tabla de surf no encontrada'}, 404

    data = request.json

    # Validar tipo si se proporciona
    tipo = data.get('tipo', tabla.tipo)
    valido, error = validar_tipo(tipo)
    if not valido:
        return error

    # Validar quillas si se proporcionan
    quillas = data.get('quillas', tabla.quillas.split(','))
    valido, error = validar_quillas(quillas)
    if not valido:
        return error

    # Actualizar los campos de la tabla
    tabla.nombre = data.get('nombre', tabla.nombre)
    tabla.marca = data.get('marca', tabla.marca)
    tabla.longitud = data.get('longitud', tabla.longitud)
    tabla.ancho = data.get('ancho', tabla.ancho)
    tabla.espesor = data.get('espesor', tabla.espesor)
    tabla.volumen = data.get('volumen', tabla.volumen)
    tabla.tipo = tipo
    tabla.material = data.get('material', tabla.material)
    tabla.quillas = ",".join(quillas)
    tabla.precio = data.get('precio', tabla.precio)
    tabla.estado = data.get('estado', tabla.estado)
    tabla.descripcion = data.get('descripcion', tabla.descripcion)

    db.session.commit()
    return {'message': 'Tabla de surf actualizada correctamente', 'data': tabla.to_dict()}, 200

#Eliminar una tabla de surf.
@tablas_bp.route('/tablas/<int:tabla_id>', methods=['DELETE'])
def delete_tabla(tabla_id):
    tabla = TablaDeSurfModelo.query.get(tabla_id)
    if not tabla:
        return {'message': 'Tabla de surf no encontrada'}, 404

    db.session.delete(tabla)
    db.session.commit()
    return {'message': 'Tabla de surf eliminada correctamente'}, 200
