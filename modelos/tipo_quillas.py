from database import db

class QuillaModelo(db.Model):
    __tablename__ = 'tipo_quillas'
    
    id = db.Column(db.Integer, primary_key=True)
    tabla_de_surf_id = db.Column(db.Integer, db.ForeignKey('tablas_surf.id'))
    tipo = db.Column(db.String(20), nullable=False)  # Tipo de quilla (Tri-fin, Quad, Single)
    material = db.Column(db.String(20), nullable=True)
    longitud = db.Column(db.String(10), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('tabla_de_surf_id', 'tipo', name='unique_quilla_tipo'),
        db.CheckConstraint("tipo IN ('tri-fin', 'quad', 'single')", name='valid_tipo'),
    )

    def to_dict(self):
        return {
            'tipo': self.tipo,
            'material': self.material,
            'longitud': self.longitud
        }
