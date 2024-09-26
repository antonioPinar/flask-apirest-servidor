from flask_sqlalchemy import SQLAlchemy

# Inicializamos SQLAlchemy
db = SQLAlchemy()

# Modelo de la tabla de surf
class TablaDeSurfModelo(db.Model):
    __tablename__ = 'tablas_de_surf'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    longitud = db.Column(db.String(10), nullable=False)
    ancho = db.Column(db.String(10), nullable=False)
    espesor = db.Column(db.String(10), nullable=False)
    volumen = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    material = db.Column(db.String(20), nullable=False)
    quillas = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    def to_dict(self):
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
            'quillas': self.quillas.split(','),
            'precio': self.precio,
            'estado': self.estado,
            'descripcion': self.descripcion
        }
