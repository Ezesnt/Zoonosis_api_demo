from marshmallow import Schema, fields

class AdopcionSchema(Schema):
    id = fields.Int(dump_only=True)
    id_animal = fields.Int(required=True)
    detalle = fields.Str()
    url = fields.Str(required=True)
    disponible = fields.Bool()
    fecha_publicacion = fields.DateTime()