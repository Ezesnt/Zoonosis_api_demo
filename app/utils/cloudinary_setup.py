import os
import cloudinary
from dotenv import load_dotenv

def configure_cloudinary():
    """Configura Cloudinary con las variables de entorno"""
    load_dotenv()  # Carga las variables del .env
    
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )
    
    
    try:
        cloudinary.api.ping()
        print("✅ Configuración de Cloudinary validada")
    except Exception as e:
        print(f"❌ Error en configuración Cloudinary: {str(e)}")
        raise