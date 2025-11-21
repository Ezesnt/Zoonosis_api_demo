
from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models.models import FotoNoticia, Noticia
from app.routes.auth_routes import rutaProtegida
from app.schemas import Noticias_schema
from app.utils.cloudinary_service import CloudinaryService
from dbConfig import db
from app.schemas.Noticias_schema import FotoNoticiaSchema, NoticiaSchema

noticia_schema = NoticiaSchema()
noticias_schema = NoticiaSchema(many=True)

noticia_bp = Blueprint('noticias', __name__)


#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO: CREAR UNA DENUNCIA

@noticia_bp.route('/noticias', methods=['POST'])
@rutaProtegida("admin")
def crear_noticia():
    current_user = request.current_user
    current_user_id = current_user['id']

    # Datos del formulario
    titulo = request.form.get('titulo')
    fecha = request.form.get('fecha')  # opcional
    barrio = request.form.get('barrio', 'otro')
    descripcion = request.form.get('descripcion')
    

    # Crear noticia
    noticia = Noticia(
        titulo=titulo,
        fecha=datetime.fromisoformat(fecha) if fecha else datetime.utcnow(),
        barrio=barrio,
        descripcion=descripcion,
        id_admin=current_user_id
    )
    db.session.add(noticia)
    db.session.commit()  

    # Subir imágenes
    imagenes = request.files.getlist('imagenes')
    fotos_creadas = []
    for img in imagenes:
        cloudinary_data = CloudinaryService.upload_noticia_photo(img, noticia.id, current_user_id)
        nueva_foto = FotoNoticia(
            id_noticia=noticia.id,
            public_id=cloudinary_data['public_id'],
            url=cloudinary_data['secure_url'],
            es_principal=False
        )
        db.session.add(nueva_foto)
        fotos_creadas.append(nueva_foto)
    db.session.commit()

    # Serializar respuesta
    result = noticia_schema.dump(noticia)
    result['imagenes'] = [foto.url for foto in fotos_creadas]
    return jsonify(result), 201



#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO: LISTAR NOTICIAS 

@noticia_bp.route('/noticias', methods=['GET'])
def listar_noticias():
    noticias = Noticia.query.filter_by(publicado=True).order_by(Noticia.fecha.desc()).all()
    result = noticias_schema.dump(noticias)
    return jsonify(result)
    



#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO: EDITAR NOTICIA

@noticia_bp.route('/noticias/editar/<int:id>', methods=['PUT'])
@rutaProtegida("admin")
def editar_noticia(id):
    noticia = Noticia.query.get_or_404(id)
    current_user = request.current_user
    current_user_id = current_user['id']

    # Actualizar campos si vienen en el form
    noticia.titulo = request.form.get('titulo', noticia.titulo)
    noticia.fecha = datetime.fromisoformat(request.form.get('fecha')) if request.form.get('fecha') else noticia.fecha
    noticia.barrio = request.form.get('barrio', noticia.barrio)
    noticia.descripcion = request.form.get('descripcion', noticia.descripcion)

    # Subir nuevas imágenes si se envían
    nuevas_imagenes = request.files.getlist('imagenes')
    fotos_creadas = []
    for img in nuevas_imagenes:
        if img and img.filename:  # Solo si hay archivo
            cloudinary_data = CloudinaryService.upload_noticia_photo(img, noticia.id, current_user_id)
            nueva_foto = FotoNoticia(
                id_noticia=noticia.id,
                public_id=cloudinary_data['public_id'],
                url=cloudinary_data['secure_url'],
                es_principal=False
            )
            db.session.add(nueva_foto)
            fotos_creadas.append(nueva_foto)

    db.session.commit()

    # Serializar respuesta
    result = noticia_schema.dump(noticia)
    # Incluye todas las imágenes (viejas y nuevas)
    result['imagenes'] = [foto.url for foto in noticia.fotos]
    return jsonify(result), 200




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO: DAR DE BAJA NOTICIA

@noticia_bp.route('/noticias/<int:id>/baja', methods=['PUT'])
@rutaProtegida("admin")
def baja_noticia(id):
    noticia = Noticia.query.get_or_404(id)
    noticia.publicado = False
    db.session.commit()
    return jsonify({"msg": "Noticia dada de baja correctamente"}), 200


#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO: LISTAR TODAS LAS NOTICIAS (ADMIN)

@noticia_bp.route('/admin/noticias', methods=['GET'])
@rutaProtegida("admin")
def listar_todas_noticias():
    noticias = Noticia.query.order_by(Noticia.fecha.desc()).all()
    result = noticias_schema.dump(noticias)
    return jsonify(result)
   

