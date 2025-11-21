import re
from marshmallow import Schema, fields, validate, ValidationError, validates
from datetime import datetime, timedelta

class AnimalSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    especie = fields.Str(required=True, validate=validate.OneOf(["perro", "gato", "otro"]))
    raza = fields.Str(allow_none=True, validate=validate.Length(max=100))
    edad = fields.Int(allow_none=True, validate=validate.Range(min=0, max=30))
    sexo = fields.Str(allow_none=True, validate=validate.OneOf(["macho", "hembra", "desconocido"]))
    color = fields.Str(allow_none=True, validate=validate.Length(max=50))
    tamanio = fields.Str(allow_none=True, validate=validate.OneOf(["chico", "mediano", "grande"]))
    esta_castrado = fields.Bool(allow_none=True)
    observaciones = fields.Str(allow_none=True)
    estado = fields.Str(dump_only=True)
    numero_patente = fields.Str(dump_only=True)
    fecha_emision_patente = fields.DateTime(dump_only=True)
    fecha_vencimiento_patente = fields.DateTime(dump_only=True)
    fecha_registro = fields.DateTime(dump_only=True)
    id_propietario = fields.Int(dump_only=True)
    activo = fields.Bool(dump_only=True)
    
    @validates('edad')
    def validate_edad(self, value):
        if value is not None and value < 0:
            raise ValidationError("La edad no puede ser negativa")

class AnimalCreateSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    especie = fields.Str(required=True, validate=validate.OneOf(["perro", "gato", "otro"]))
    raza = fields.Str(allow_none=True, validate=validate.Length(max=100))
    edad = fields.Int(allow_none=True, validate=validate.Range(min=0, max=30))
    sexo = fields.Str(allow_none=True, validate=validate.OneOf(["macho", "hembra", "desconocido"]))
    color = fields.Str(allow_none=True, validate=validate.Length(max=50))
    tamanio = fields.Str(allow_none=True, validate=validate.OneOf(["chico", "mediano", "grande"]))
    esta_castrado = fields.Bool(allow_none=True)
    observaciones = fields.Str(allow_none=True)

    @validates('edad')
    def validate_edad(self, value):
        if value is not None and value < 0:
            raise ValidationError("La edad no puede ser negativa")

class AnimalPatentarSchema(Schema):
   
    pass

class AnimalResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str()
    estado = fields.Str()
    numero_patente = fields.Str(
        validate=validate.Regexp(r'^PAT-\d{4}-\d{4}$', error="Formato de patente inválido")
    )
    fecha_emision_patente = fields.DateTime()
    fecha_vencimiento_patente = fields.DateTime(
        description="Calculada automáticamente como 1 año después de la emisión"
    )
    
class UserBasicSchema(Schema):
    nombre = fields.Str()
    apellido = fields.Str()
    categoria = fields.Str()

class LibretaSchema(Schema):
    id = fields.Int(dump_only=True)
    tipo = fields.Str()
    descripcion = fields.Str()
    fecha = fields.Date()
    registrado_por = fields.Nested(UserBasicSchema, attribute="usuario") 

class LibretaCreateSchema(Schema):
    tipo = fields.Str(required=True, validate=validate.OneOf(["vacuna", "desparasitación", "control", "operación", "otro"]))
    descripcion = fields.Str(allow_none=True)
    fecha = fields.Date(required=True)
    
class LibretaUpdateSchema(Schema):
    tipo = fields.Str(validate=validate.OneOf(["vacunación", "desparasitación", "control"]))
    descripcion = fields.Str()
    fecha = fields.Date()