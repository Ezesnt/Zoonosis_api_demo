from datetime import timedelta
import os
from dotenv import load_dotenv
import cloudinary

# Carga variables del .env
load_dotenv()

class Config:
    # Configuración básica de Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '11111')  
    
    # Database (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:1111@localhost:5432/zoonosis_base')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT (Autenticación)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '22255')  
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    @staticmethod
    def init_cloudinary():
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )