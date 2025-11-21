import cloudinary.uploader
from app.models.models import FotoAnimal
from datetime import datetime
from dbConfig import db

class CloudinaryService:
    @staticmethod
    def upload_animal_photo(file, animal_id):
        """Sube una foto a Cloudinary y guarda referencia en DB"""
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=f"animales/{animal_id}",
                public_id=f"photo_{datetime.now().timestamp()}",
                resource_type="image",
                quality="auto:good",
                width=1200,
                crop="limit"
            )
            
            new_photo = FotoAnimal(
                id_animal=animal_id,
                public_id=result['public_id'],
                url=result['secure_url'],
                es_principal=False
            )
            
            db.session.add(new_photo)
            db.session.commit()
            
            return new_photo
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al subir imagen: {str(e)}")
        

    @staticmethod
    def upload_denuncia_file(file, denuncia_id, user_id):
        """Sube archivos de denuncia (PDF, Word, imágenes) a Cloudinary"""
        try:
            # Determina el tipo de recurso basado en la extensión
            if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                resource_type = "image"
                transformations = {"quality": "auto:good", "width": 1200, "crop": "limit"}
            else:
                resource_type = "raw"
                transformations = {}
            
            # Sube el archivo a Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder=f"denuncias/{user_id}/{denuncia_id}",
                public_id=f"doc_{datetime.now().timestamp()}",
                resource_type=resource_type,
                allowed_formats=['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'],
                **transformations
            )
            
            return {
                'public_id': result['public_id'],
                'secure_url': result['secure_url'],
                'resource_type': resource_type,
                'format': result.get('format', '')
            }
            
        except Exception as e:
            raise Exception(f"Error al subir archivo de denuncia: {str(e)}")
        
        


    @staticmethod
    def upload_noticia_photo(file, noticia_id, admin_id):
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=f"noticias/{admin_id}/{noticia_id}",
                public_id=f"noticia_{datetime.now().timestamp()}",
                resource_type="image",
                quality="auto:good",
                width=1200,
                crop="limit"
            )
            return {
                'public_id': result['public_id'],
                'secure_url': result['secure_url']
            }
        except Exception as e:
            raise Exception(f"Error al subir imagen de noticia: {str(e)}")