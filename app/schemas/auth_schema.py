

from marshmallow import Schema, fields, validate, ValidationError, validates
from werkzeug.security import   check_password_hash

from app.data import constants



class UsuarioRegistroSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    domicilio = fields.Str(required=True, validate=validate.Length(min=2,max=150))
    email = fields.Email(required=True, validate=validate.Length(min=2,max=150))
    dni = fields.Str(required=True, validate=validate.Length(min=8, max=20))
    telefono = fields.Str(allow_none=True, validate=validate.Length(min=2,max=30))
    password = fields.Str(required=True, load_only=True, 
                         validate=validate.Length(min=6, max=100))
    password_confirm = fields.Str(required=True, load_only=True)
    barrio = fields.Str(
    required=True,
    validate=validate.OneOf(constants.BARRIOS, error="Barrio inválido"),
    error_messages={"required": "El barrio es obligatorio."}
)

    @validates("dni")
    def validate_dni(self, value):
        if not value.isdigit():
            raise ValidationError("El DNI debe contener solo números")

    @validates("password_confirm")
    def validate_passwords(self, value, **kwargs):
        if value != self.context.get('password'):
            raise ValidationError("Las contraseñas no coinciden")

    
class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))
    password_confirm = fields.Str(required=True)

    @validates("password_confirm")
    def validate_passwords(self, value, **kwargs):
        if value != self.context.get('password'):
            raise ValidationError("Las contraseñas no coinciden")
        
        
        
class LoginSchema(Schema):
    usuario = fields.Str(required=True)
    clave = fields.Str(required=True, load_only=True)

    @validates("usuario")
    def validar_usuario(self, value):
        from app.models.models import Usuario 
        if "@" in value:
            if not Usuario.query.filter_by(email=value).first():
                raise ValidationError("El email no está registrado.")
        elif value.isdigit():
            if not Usuario.query.filter_by(dni=value).first():
                raise ValidationError("El DNI no está registrado.")
        else:
            raise ValidationError("Debe ingresar un email válido o un DNI numérico.")

    def load_usuario_valido(self, data, **kwargs):
        # Buscar usuario por email o DNI
        from app.models.models import Usuario 
        usuario = None
        if "@" in data["usuario"]:
            usuario = Usuario.query.filter_by(email=data["usuario"]).first()
        elif data["usuario"].isdigit():
            usuario = Usuario.query.filter_by(dni=data["usuario"]).first()

        if usuario and check_password_hash(usuario.password, data["clave"]):
            return usuario
        raise ValidationError("Credenciales inválidas.")

