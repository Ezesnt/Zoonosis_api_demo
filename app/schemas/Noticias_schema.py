from marshmallow import Schema, fields

class FotoNoticiaSchema(Schema):
    id = fields.Int()
    url = fields.Str()
    es_principal = fields.Bool()

class NoticiaSchema(Schema):
    id = fields.Int()
    titulo = fields.Str(required=True)
    fecha = fields.DateTime(required=True)
    barrio = fields.Str(required=True)
    descripcion = fields.Str(required=True)
    publicado = fields.Bool()
    id_admin = fields.Int()
    imagenes = fields.Nested(FotoNoticiaSchema, many=True, attribute="fotos")
    