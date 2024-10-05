from database import db
from modelos.tabla_surf import TablaDeSurfModelo
from modelos.tipo_quillas import QuillaModelo

# Constantes para validaciones
TIPOS_VALIDOS = ['Shortboard', 'Longboard', 'Fish', 'Funboard', 'Gun']
QUILLAS_VALIDAS = ['Tri-fin', 'Quad', 'Single']


# Funciones auxiliares
#Normaliza un string según el tipo especificado
def normalizar_string(valor, tipo):
    if not isinstance(valor, str):
        return valor  # Devolver el valor original si no es un string
    if tipo == 'capitalize':
        return valor.strip().capitalize()
    elif tipo == 'title':
        return valor.strip().title()
    elif tipo == 'lower':
        return valor.strip().lower()
    return valor


#Valida si el tipo proporcionado es válido.
def validar_tipo(tipo):
    tipo = normalizar_string(tipo, 'capitalize')
    if tipo not in TIPOS_VALIDOS:
        return False, [{'message': f'Tipo inválido. Los tipos válidos son: {", ".join(TIPOS_VALIDOS)}'}, 400]
    return True, None


#Valida si las quillas proporcionadas son válidas.
def validar_quillas(quillas):
    if not isinstance(quillas, list):
        return False, [{'message': 'El campo quillas debe ser una lista'}, 400]
    
    tiposQuilla = [quilla['tipo'] for quilla in quillas]
    tiposQuilla = [normalizar_string(tipo, 'capitalize') for tipo in tiposQuilla]
    # Verifica si hay elementos duplicados
    if len(tiposQuilla) != len(set(tiposQuilla)):
        return False, [{'message': 'No se permiten opciones de quillas duplicadas'}, 400]
    # Verifica si hay más de 3 quillas
    if len(tiposQuilla) > 3:
        return False, [{'message': 'Solo se permiten hasta 3 opciones de quillas'}, 400]
    # Verifica que las quillas sean válidas
    for tipoQuilla in tiposQuilla:
        if tipoQuilla not in QUILLAS_VALIDAS:
            return False, [{'message': f'Quilla inválida. Las opciones válidas son: {", ".join(QUILLAS_VALIDAS)}'}, 400]
    
    return True, None


#Valida los campos de entrada para normalizar bbdd
def normalizar_datos(data):
    dataFormateada = {}
    quillasFormateadas = []

    # Iterar sobre las columnas del modelo TablaDeSurfModelo
    for columnaTabla in TablaDeSurfModelo.__table__.columns:
        campoTabla = columnaTabla.name  # El nombre de la columna

        # Comprobar si el campo está presente en el diccionario de datos
        if campoTabla in data:
            # Normalizamos el dato si es de tipo string
            if isinstance(columnaTabla.type, db.String):
                dataFormateada[campoTabla] = normalizar_string(data[campoTabla], 'lower' if campoTabla != 'descripcion' else 'capitalize')
            else:
                dataFormateada[campoTabla] = data[campoTabla]

    # Comprobamos si el campo se relaciona con algun modelo (relación One-to-Many o Many-to-Many)
    for relacion in TablaDeSurfModelo.__mapper__.relationships:
        # Comprobamos si se relaciona con el moedlo quillas
        if relacion.mapper.class_ == QuillaModelo and relacion.key in data:
            # Iterar sobre los elementos de la relación (quillas)
            for dataQuillas in data[relacion.key]:
                quillaFormateada = {}
                # Iterar sobre las columnas del modelo QuillaModelo
                for columnaQuilla in QuillaModelo.__table__.columns:
                    campoQuilla = columnaQuilla.name
                    if campoQuilla in dataQuillas:
                        # Normalizamos el dato si es de tipo string
                        if isinstance(columnaQuilla.type, db.String):
                            quillaFormateada[campoQuilla] = normalizar_string(dataQuillas[campoQuilla], 'lower')
                        else:
                            quillaFormateada[campoQuilla] = dataQuillas[campoQuilla]

                quillasFormateadas.append(quillaFormateada)

            dataFormateada[relacion.key] = quillasFormateadas

    # Validar 'tipo'
    if 'tipo' in dataFormateada:
        valido, error = validar_tipo(dataFormateada['tipo'])
        if not valido:
            return False, error

    # Validar 'quillas'
    if 'quillas' in dataFormateada:
        valido, error = validar_quillas(dataFormateada['quillas'])
        if not valido:
            return False, error

    return True, dataFormateada
