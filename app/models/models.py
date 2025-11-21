from sqlalchemy import Enum
from app.data import constants
from dbConfig import db
from datetime import datetime



class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    apellido = db.Column(db.String(150), nullable=False)
    domicilio = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    categoria = db.Column(db.String(50), default='ciudadano')  # 'admin', 'ciudadano', etc
    dni = db.Column(db.String(20), unique=True, nullable=True)
    telefono = db.Column(db.String(30), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    barrio = db.Column(Enum(*constants.BARRIOS, name="barrios_enum"), default='otro')

    turnos = db.relationship('Turno', backref='usuario', lazy=True)
    denuncias = db.relationship('Denuncia', backref='usuario', lazy=True)
    animales = db.relationship('Animal', backref='propietario', lazy=True)
    reset_tokens = db.relationship('ResetPasswordToken', backref='usuario', lazy=True)


class Animal(db.Model):
    __tablename__ = 'animales'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    especie = db.Column(db.String(50), nullable=False)  # perro, gato, etc.
    raza = db.Column(db.String(100), nullable=True)
    edad = db.Column(db.Integer, nullable=True)
    sexo = db.Column(db.String(10), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    tamanio = db.Column(db.String(50), nullable=True)  # chico, mediano, grande
    esta_castrado = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    motivo_baja = db.Column(db.String(100), nullable=True)
    fecha_baja = db.Column(db.DateTime, nullable=True)  

    estado = db.Column(db.String(50), default='no patentado')  # no patentado, pendiente, aprobado, rechazado
    numero_patente = db.Column(db.String(50), unique=True, nullable=True)
    fecha_emision_patente = db.Column(db.DateTime, nullable=True)
    fecha_vencimiento_patente = db.Column(db.DateTime, nullable=True)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    id_propietario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    adopcion = db.relationship('Adopcion', backref='animal', uselist=False)
    historial_libreta = db.relationship('HistorialLibreta', backref='animal', lazy=True)
    
    fotos = db.relationship('FotoAnimal', backref='animal')


class FotoAnimal(db.Model):
    __tablename__ = 'fotos_animales'
    
    id = db.Column(db.Integer, primary_key=True)
    id_animal = db.Column(db.Integer, db.ForeignKey('animales.id'))
    public_id = db.Column(db.String(255), nullable=False)  
    url = db.Column(db.String(512), nullable=False)       
    es_principal = db.Column(db.Boolean, default=False)
    
    
class HistorialLibreta(db.Model):
    __tablename__ = 'historial_libreta'

    id = db.Column(db.Integer, primary_key=True)
    id_animal = db.Column(db.Integer, db.ForeignKey('animales.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # vacuna, desparasitación, control, otro
    descripcion = db.Column(db.String(255), nullable=True)
    fecha = db.Column(db.DateTime, nullable=False)
    registrado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    usuario = db.relationship('Usuario', backref='registros_libreta')


class Adopcion(db.Model):
    __tablename__ = 'adopciones'

    id = db.Column(db.Integer, primary_key=True)
    id_animal = db.Column(db.Integer, db.ForeignKey('animales.id'), nullable=False)
    detalle = db.Column(db.Text, nullable=True)  # Descripción o texto libre sobre el animal
    url = db.Column(db.String(255), unique=False, nullable=False)  # Slug o identificador amigable
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    disponible = db.Column(db.Boolean, default=True)



class Denuncia(db.Model):
    __tablename__ = 'denuncias'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='pendiente')
    descripcion = db.Column(db.Text, nullable=False)
    tipo_denuncia = db.Column(Enum(*constants.TIPOS_DENUNCIA, name="tipos_denuncia_enum"), nullable=False)
    barrio = db.Column(db.String(50), default='otro')
    
    detalles_extra = db.Column(db.Text)
    ubicacion = db.Column(db.String(255))
    
    
    archivos = db.relationship('ArchivoDenuncia', backref='denuncia', lazy=True)
    
    
class ArchivoDenuncia(db.Model):
    __tablename__ = 'archivos_denuncia'

    id = db.Column(db.Integer, primary_key=True)
    id_denuncia = db.Column(db.Integer, db.ForeignKey('denuncias.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)

    

class Turno(db.Model):
    __tablename__ = 'turnos'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_animal = db.Column(db.Integer, db.ForeignKey('animales.id'), nullable=False)
    tipo_turno = db.Column(Enum(*constants.TIPOS_TURNO, name="tipos_turno_enum"), nullable=False)
    fecha_solicitada = db.Column(db.Date, nullable=False)
    fecha_turno = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(50), default='pendiente')  # pendiente, confirmado, cancelado
    instrucciones = db.Column(db.Text, nullable=True)
    motivo_cancelacion = db.Column(db.Text, nullable=True)

    
    animal = db.relationship('Animal', backref='turnos')
    
    

class ResetPasswordToken(db.Model):
    __tablename__ = 'reset_password_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)


class ResumenIA(db.Model):
    __tablename__ = 'resumen_ia'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    

class Noticia(db.Model):
    __tablename__ = 'noticias'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    barrio = db.Column(db.String(50), default='otro')
    imagenes = db.Column(db.JSON, nullable=True)  # Lista de URLs o public_ids
    descripcion = db.Column(db.Text, nullable=False)
    publicado = db.Column(db.Boolean, default=True)  # True=publicada, False=borrador/baja lógica
    id_admin = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admin = db.relationship('Usuario', backref='noticias')
    fotos = db.relationship('FotoNoticia', backref='noticia', lazy=True)
    
class FotoNoticia(db.Model):
    __tablename__ = 'fotos_noticia'
    id = db.Column(db.Integer, primary_key=True)
    id_noticia = db.Column(db.Integer, db.ForeignKey('noticias.id'), nullable=False)
    public_id = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    es_principal = db.Column(db.Boolean, default=False)