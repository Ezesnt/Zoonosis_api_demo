from marshmallow import Schema, fields

class HistorialLibretaSchema(Schema):
    id = fields.Int(dump_only=True)
    id_animal = fields.Int(required=True)
    tipo = fields.Str(required=True)  # vacuna, desparasitación, etc.
    descripcion = fields.Str()
    fecha = fields.DateTime(required=True)
    registrado_por = fields.Str()
