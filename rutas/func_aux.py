from database import db
from sqlalchemy.orm import joinedload
from modelos.tabla_surf import TablaDeSurfModelo
from modelos.tipo_quillas import QuillaModelo

# Constantes para validaciones
TIPOS_VALIDOS = ['Shortboard', 'Longboard', 'Fish', 'Funboard', 'Gun']
QUILLAS_VALIDAS = ['Tri-fin', 'Quad', 'Single']


# Funciones auxiliares
# Normaliza un string según el tipo especificado
def normalizar_string(valor, tipo='lower'):
    if not isinstance(valor, str):
        return valor  # Devolver el valor original si no es un string
    
    valor = valor.strip()
    if tipo == 'capitalize':
        return valor.capitalize()
    elif tipo == 'title':
        return valor.title()
    elif tipo == 'lower':
        return valor.lower()
    else:
        raise ValueError(f"Tipo de normalización '{tipo}' no soportado")


#Valida si el tipo proporcionado es válido.
def validar_tipo(tipo):
    tipo = normalizar_string(tipo, 'capitalize')

    if tipo not in TIPOS_VALIDOS:
        return False, {'message': f'Tipo inválido. Los tipos válidos son: {", ".join(TIPOS_VALIDOS)}'}
    
    return True, None


#Valida si las quillas proporcionadas son válidas.
def validar_quillas(quillas):
    if not isinstance(quillas, list):
        return False, {'message': 'El campo quillas debe ser una lista'}
    
    tiposQuilla = [normalizar_string(quilla['tipo'], 'capitalize') for quilla in quillas]
    # Verifica si hay elementos duplicados
    if len(tiposQuilla) != len(set(tiposQuilla)):
        return False, {'message': 'No se permiten opciones de quillas duplicadas'}
    # Verifica si hay más de 3 quillas
    if len(tiposQuilla) > 3:
        return False, {'message': 'Solo se permiten hasta 3 opciones de quillas'}
    # Verifica que las quillas sean válidas
    for tipoQuilla in tiposQuilla:
        if tipoQuilla not in QUILLAS_VALIDAS:
            return False, {'message': f'Quilla inválida. Las opciones válidas son: {", ".join(QUILLAS_VALIDAS)}'}
    
    return True, None


#Valida los campos de entrada para normalizar bbdd
def normalizar_datos(data):
    dataFormateada = {}
    quillasFormateadas = []

    # Primero normalizamos los campos clave
    data = {normalizar_string(clave, 'lower'): valor for clave, valor in data.items()}

    # Obtener las columnas del modelo TablaDeSurfModelo y sus columnas relacion
    columnasTabla = {columna.name: columna for columna in TablaDeSurfModelo.__table__.columns}
    relacionesTabla = {relacion.key: relacion for relacion in TablaDeSurfModelo.__mapper__.relationships}

    # Iterar sobre el diccionario de datos
    for campoTabla, valorTabla in data.items():
        # Verificar si el campo existe como una columna en el modelo
        if campoTabla in columnasTabla:
            columnaTabla = columnasTabla[campoTabla]
            # Normalizar el dato si es de tipo string
            if isinstance(columnaTabla.type, db.String):
                dataFormateada[campoTabla] = normalizar_string(valorTabla, 'lower' if campoTabla != 'descripcion' else 'capitalize')
            else:
                dataFormateada[campoTabla] = valorTabla
        # Verificar si el campo existe como una relacion en el modelo
        elif campoTabla in relacionesTabla:
            relacionTabla = relacionesTabla[campoTabla]
            # Si la relación es con el modelo de Quillas, procesar la lista de quillas
            if relacionTabla.mapper.class_ == QuillaModelo:
                for dataQuillas in valorTabla:  # Iterar sobre los elementos relacionados (quillas)
                    quillaFormateada = {}
                    # Obtener las columnas del modelo QuillaModelo
                    columnasQuilla = {columna.name: columna for columna in QuillaModelo.__table__.columns}
                    for campoQuilla, valorQuilla in dataQuillas.items():
                        if campoQuilla in columnasQuilla:
                            columnaQuilla = columnasQuilla[campoQuilla]
                            # Normalizar el dato si es de tipo string
                            if isinstance(columnaQuilla.type, db.String):
                                quillaFormateada[campoQuilla] = normalizar_string(valorQuilla, 'lower')
                            else:
                                quillaFormateada[campoQuilla] = valorQuilla
                        else:
                            # Manejar el caso en que el campo de quilla no exista en el modelo
                            return False, {"message": f"El campo de quilla '{campoQuilla}' no existe en el modelo."}

                    quillasFormateadas.append(quillaFormateada)

                dataFormateada[campoTabla] = quillasFormateadas
            else:
                return False, {"message": f"El campo '{campoTabla}' todavía no existe en relación con su modelo."}
        else:
            # Manejar el caso en que el campo no exista ni como columna ni como relación en el modelo
            return False, {"message": f"El campo de la tabla de surf '{campoTabla}' no existe en el modelo."}

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


# Realiza la consulta a la base de datos dependiendo del parámetro proporcionado.
# - Si tabla_id está presente, obtiene la tabla por ID.
# - Si campo y valor están presentes, realiza un filtro específico.
# - Si ninguno está presente, obtiene todas las tablas.
def consultar_tablas(tabla_id=None, campo=None, valor=None):

    if tabla_id:
        return TablaDeSurfModelo.query.get(tabla_id)

    if campo and valor:
        if campo == 'quillas':
            # Filtrar por tipo de quilla usando join de modelos
            return TablaDeSurfModelo.query.options(joinedload(TablaDeSurfModelo.quillas)).join(QuillaModelo).filter(QuillaModelo.tipo == valor).all()
        else:
            # Filtrar por los campos de la tabla de surf
            return TablaDeSurfModelo.query.filter(getattr(TablaDeSurfModelo, campo) == valor).all()

    # Si no hay filtros, devuelve todas las tablas
    return TablaDeSurfModelo.query.all()
    

# Realiza la atualizacion del campo quillas en la base de datos
def actualizar_quillas(tabla, quillasData):
    quillasExistentes = {quilla.tipo: quilla for quilla in tabla.quillas}
    quillasNuevas = []
    tiposProcesados = set()

    for quilla in quillasData:
        tipo = quilla['tipo']
        material = quilla.get('material', '')
        longitud = quilla.get('longitud', '')

        quillaExistente = quillasExistentes.get(tipo)
        
        if quillaExistente:
            # Solo actualiza si hay cambios en el material o longitud
            if quillaExistente.material != material or quillaExistente.longitud != longitud:
                quillaExistente.material = material
                quillaExistente.longitud = longitud
        else:
            # Crear nueva quilla si no existe
            quillaNueva = QuillaModelo(
                tabla_de_surf_id=tabla.id,
                tipo=tipo,
                material=material,
                longitud=longitud
            )
            quillasNuevas.append(quillaNueva)

        tiposProcesados.add(tipo)

    # Eliminar quillas que ya no están en la lista
    for tipoExistente in list(quillasExistentes):
        if tipoExistente not in tiposProcesados:
            db.session.delete(quillasExistentes[tipoExistente])

    # Añadir nuevas quillas
    if quillasNuevas:
        db.session.add_all(quillasNuevas)

    # Actualizar la relación de la tabla con las quillas procesadas
    tabla.quillas = [quilla for quilla in tabla.quillas if quilla.tipo in tiposProcesados] + quillasNuevas