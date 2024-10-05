from flask import Blueprint, request, jsonify
from database import db
from modelos.tabla_surf import TablaDeSurfModelo
from modelos.tipo_quillas import QuillaModelo
from rutas.func_aux import normalizar_datos, normalizar_string

# Crear un Blueprint para las rutas de tablas
tablas_bp = Blueprint('tablas', __name__)

# Métodos CRUD
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
    tipo = normalizar_string(tipo, 'lower')
    tablas = TablaDeSurfModelo.query.filter_by(tipo=tipo).all()
    if not tablas:
        return {'message': 'No se encontraron tablas de surf con ese tipo'}, 404
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Obtener tablas filtradas por marca.
@tablas_bp.route('/tablas/marca/<string:marca>', methods=['GET'])
def get_tablas_por_marca(marca):
    marca = normalizar_string(marca, 'lower')
    tablas = TablaDeSurfModelo.query.filter_by(marca=marca).all()
    if not tablas:
        return {'message': 'No se encontraron tablas de surf con esa marca'}, 404
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Obtener tablas filtradas por quillas.
@tablas_bp.route('/tablas/quillas/<string:quilla>', methods=['GET'])
def get_tablas_por_quillas(quilla):
    quilla = normalizar_string(quilla, 'lower')
    tablas = TablaDeSurfModelo.query.join(QuillaModelo).filter(QuillaModelo.tipo == quilla).all()
    if not tablas:
        return {'message': 'No se encontraron tablas de surf con ese ajuste de quillas'}, 404
    return jsonify([tabla.to_dict() for tabla in tablas]), 200


#Crear una nueva tabla de surf.
@tablas_bp.route('/tablas', methods=['POST'])
def create_tabla():
    data = request.json

    # Verificar que el cuerpo de la solicitud sea un diccionario
    if not isinstance(data, dict):
        return {'message': 'El cuerpo de la solicitud debe ser un objeto JSON (diccionario)'}, 400

    try:
        # Normalizar y validar datos
        valido, datosFormateados = normalizar_datos(data)
        if not valido:
            return datosFormateados  # Devolver error de validación si lo hay

        nueva_tabla = TablaDeSurfModelo(
            nombre = datosFormateados['nombre'],
            marca = datosFormateados['marca'],
            longitud = datosFormateados['longitud'],
            ancho = datosFormateados['ancho'],
            espesor = datosFormateados['espesor'],
            volumen = datosFormateados['volumen'],
            tipo = datosFormateados['tipo'],
            material = datosFormateados['material'],
            precio = datosFormateados['precio'],
            estado = datosFormateados['estado'],
            descripcion = datosFormateados.get('descripcion', '')
        )
        
        db.session.add(nueva_tabla)
        db.session.flush()  # Asegura que nueva_tabla obtenga un ID antes de asociar las quillas

        # Manejar el campo 'quillas', si está presente
        quillas_data = datosFormateados.get('quillas', [])

        for quilla in quillas_data:
            tipo = quilla['tipo']
            material = quilla.get('material', '')
            longitud = quilla.get('longitud', '')

            # Creamos el objeto quilla
            quilla_obj = QuillaModelo(
                tipo = tipo,
                material = material,
                longitud = longitud,
                tabla_de_surf_id = nueva_tabla.id
            )

            nueva_tabla.quillas.append(quilla_obj)  # Agregar la quilla a la relación

        db.session.commit()
        return {'message': 'Tabla de surf creada correctamente', 'data': nueva_tabla.to_dict()}, 201
    
    except KeyError as e:
        db.session.rollback()
        return {'error': f'Campo requerido faltante: {str(e)}'}, 400
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error interno del servidor: {str(e)}'}, 500
    


#Actualizar una tabla de surf existente.
@tablas_bp.route('/tablas/<int:tabla_id>', methods=['PUT'])
def update_tabla(tabla_id):
    
    tabla = TablaDeSurfModelo.query.get(tabla_id)
    if not tabla:
        return {'message': 'Tabla de surf no encontrada'}, 404

    data = request.json

    try:
        # Normalizar y validar datos
        valido, datosFormateados = normalizar_datos(data)
        if not valido:
            return datosFormateados  # Devolver error de validación si lo hay

        # Manejar el campo 'quillas', si está presente
        if 'quillas' in datosFormateados:
            quillas_data = datosFormateados['quillas']
            quillas_existentes = {quilla.tipo: quilla for quilla in tabla.quillas}

            quillas_nuevas = []
            tipos_procesados = set()

            for quilla in quillas_data:
                tipo = quilla['tipo']
                material = quilla.get('material', '')
                longitud = quilla.get('longitud', '')

                if tipo in quillas_existentes:
                    # Actualizar la quilla existente si los datos son diferentes
                    quilla_existente = quillas_existentes[tipo]
                    if quilla_existente.material != material:
                        quilla_existente.material = material

                    if quilla_existente.longitud != longitud:
                        quilla_existente.longitud = longitud
                else:
                    # Crear una nueva quilla
                    quilla_nueva = QuillaModelo(
                        tabla_de_surf_id = tabla.id,
                        tipo = tipo,
                        material = material,
                        longitud = longitud
                    )
                    quillas_nuevas.append(quilla_nueva)

                tipos_procesados.add(tipo)

            # Eliminar las quillas que ya no están en la nueva lista
            for tipo_existente, quilla_existente in quillas_existentes.items():
                if tipo_existente not in tipos_procesados:
                    db.session.delete(quilla_existente)

            # Añadir las nuevas quillas
            if quillas_nuevas:
                db.session.add_all(quillas_nuevas)

            # Actualizar la relación entre la tabla de surf y las quillas
            tabla.quillas = [quilla for quilla in tabla.quillas if quilla.tipo in tipos_procesados] + quillas_nuevas

        # Actualizar los campos normalizados
        for clave, valor in datosFormateados.items():
            if clave != 'quillas' and hasattr(tabla, clave):
                setattr(tabla, clave, valor)

        db.session.commit()
        return {'message': 'Tabla de surf actualizada correctamente', 'data': tabla.to_dict()}, 200
    
    except KeyError as e:
        db.session.rollback()
        return {'error': f'Campo requerido faltante: {str(e)}'}, 400
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error interno del servidor: {str(e)}'}, 500
    


#Eliminar una tabla de surf.
@tablas_bp.route('/tablas/<int:tabla_id>', methods=['DELETE'])
def delete_tabla(tabla_id):
    # Buscar la tabla de surf
    tabla = TablaDeSurfModelo.query.get(tabla_id)
    
    if not tabla:
        return {'message': 'Tabla de surf no encontrada'}, 404

    try:
        # Eliminar la tabla de surf (SQLAlchemy se encargará de eliminar las quillas asociadas automáticamente)
        db.session.delete(tabla)
        db.session.commit()

        return {'message': 'Tabla de surf eliminada correctamente'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al eliminar la tabla de surf: {str(e)}'}, 500
