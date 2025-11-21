from dataclasses import fields
from wsgiref import validate
from app.data import constants
from app.models.models import Denuncia, ArchivoDenuncia
from app import ma


class ArchivoDenunciaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ArchivoDenuncia
        include_fk = True


class DenunciaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Denuncia
        include_fk = True

    archivos = ma.Nested(ArchivoDenunciaSchema, many=True)

