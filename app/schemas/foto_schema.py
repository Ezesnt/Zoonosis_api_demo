from marshmallow import Schema, fields

class FotoAnimalSchema(Schema):
    class Meta:
        fields = ('id', 'url', 'es_principal')