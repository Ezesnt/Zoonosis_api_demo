from marshmallow import Schema, fields

class TurnoSchema(Schema):
    id = fields.Int(dump_only=True)
    id_usuario = fields.Int(required=True)
    id_animal = fields.Int(required=True)
    tipo_turno = fields.Str(required=True)
    fecha_solicitada = fields.Date(required=True)
    fecha_turno = fields.DateTime(allow_none=True)
    estado = fields.Str()
    instrucciones = fields.Str(allow_none=True)
    motivo_cancelacion = fields.Str(allow_none=True)
    # Para mostrar datos del animal y usuario en admin
    animal = fields.Nested('AnimalSchema', only=('id', 'nombre', 'especie'), dump_only=True)
    usuario = fields.Nested('UsuarioSchema', only=('id', 'nombre', 'apellido', 'dni','telefono'), dump_only=True)
    
   