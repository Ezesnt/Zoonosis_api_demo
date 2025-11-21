# schemas/usuario_schema.py

from marshmallow import Schema, ValidationError, fields , validate, validates

from app.models.models import Usuario

class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    apellido = fields.Str(required=True)
    domicilio = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)
    categoria = fields.Str()
    dni = fields.Str()
    telefono = fields.Str()
    fecha_registro = fields.DateTime(dump_only=True)
    activo = fields.Bool()
    
class AdminUsuarioUpdateSchema(Schema):
    activo = fields.Bool()
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    apellido = fields.Str(required=True)
    domicilio = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)
    dni = fields.Str()
    telefono = fields.Str()
    fecha_registro = fields.DateTime(dump_only=True)
    categoria = fields.Str(required=False, validate=validate.OneOf(['admin', 'ciudadano']))
    
class UsuarioUpdateSchema(Schema):

    nombre = fields.Str(required=False, validate=validate.Length(min=2, max=15))
    apellido = fields.Str(required=False, validate=validate.Length(min=2, max=15))
    domicilio = fields.Str(required=False, validate=validate.Length(min=2,max=150))
    email = fields.Email(required=False, validate=validate.Length(min=4,max=30))
    dni = fields.Str(required=False, validate=validate.Length(min=8, max=8))
    telefono = fields.Str(allow_none=False, validate=validate.Length(min=6,max=15))
  
    @validates('dni')
    def validate_dni(self, dni):
            if dni:  
                current_user_id = self.context.get('current_user_id')
                existe = Usuario.query.filter(
                    Usuario.dni == dni,
                    Usuario.id != current_user_id
                ).first()
                if existe:
                    raise ValidationError("El DNI ya está registrado ")

    @validates('email')
    def validate_email(self, email):
            if email:  
                current_user_id = self.context.get('current_user_id')
                existe = Usuario.query.filter(
                    Usuario.email == email,
                    Usuario.id != current_user_id
                ).first()
                if existe:
                    raise ValidationError("El email ya está registrado")
                
class CiudadanoSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(dump_only=True)
    apellido = fields.Str(dump_only=True)
    dni = fields.Str(dump_only=True)