
from flask import Blueprint, request, jsonify
from dbConfig import db
from app.models.models import Denuncia, ArchivoDenuncia
from app.schemas.denuncia_schema import ArchivoDenunciaSchema, DenunciaSchema
from app.utils.cloudinary_service import CloudinaryService
from app.routes.auth_routes import rutaProtegida
from datetime import datetime
from app.utils.email_utils import enviar_mail_resend 

denuncia_bp = Blueprint('denuncias', __name__)

denuncia_schema = DenunciaSchema()
archivo_schema = ArchivoDenunciaSchema()


#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:listar todas las denuncias


@denuncia_bp.route('/denuncias', methods=['POST'])
@rutaProtegida("ciudadano")
def crear_denuncia():
    current_user = request.current_user
    current_user_id = current_user['id']

    
    descripcion = request.form.get('descripcion')
    tipo_denuncia = request.form.get('tipo_denuncia')
    detalles_extra = request.form.get('detalles_extra')
    ubicacion = request.form.get('ubicacion')

    nueva_denuncia = Denuncia(
        id_usuario=current_user_id,
        descripcion=descripcion,
        tipo_denuncia=tipo_denuncia,
        detalles_extra=detalles_extra,
        ubicacion=ubicacion
    )

    db.session.add(nueva_denuncia)
    db.session.commit()

    
    archivos = request.files.getlist('archivos')  

    archivos_creados = []
    for archivo in archivos:
        cloudinary_data = CloudinaryService.upload_denuncia_file(archivo, nueva_denuncia.id, current_user_id)
        nuevo_archivo = ArchivoDenuncia(
            id_denuncia=nueva_denuncia.id,
            nombre_archivo=cloudinary_data['public_id'],
            ruta_archivo=cloudinary_data['secure_url']
        )
        db.session.add(nuevo_archivo)
        archivos_creados.append(nuevo_archivo)

    db.session.commit()

    # Puedes devolver la denuncia y los archivos subidos
    result = denuncia_schema.dump(nueva_denuncia)
    result['archivos'] = archivo_schema.dump(archivos_creados, many=True)
    return jsonify(result), 201




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:listar todas las denuncias del usuario actual

@denuncia_bp.route('/denuncias/mis', methods=['GET'])
@rutaProtegida("ciudadano")
def mis_denuncias():
    current_user = request.current_user
    current_user_id = current_user['id']

    denuncias = Denuncia.query.filter_by(id_usuario=current_user_id).all()
    return denuncia_schema.jsonify(denuncias, many=True)




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:listar detalle de una denuncia 

@denuncia_bp.route('/denuncias/<int:id_denuncia>', methods=['GET'])
@rutaProtegida("ciudadano")
def detalle_denuncia(id_denuncia):
    denuncia = Denuncia.query.get_or_404(id_denuncia)
    return denuncia_schema.jsonify(denuncia)





#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:subir archivos a una denuncia

@denuncia_bp.route('/denuncias/<int:id_denuncia>/archivos', methods=['POST'])
@rutaProtegida("ciudadano")
def subir_archivo_denuncia(id_denuncia):
    current_user = request.current_user
    current_user_id = current_user['id']

    file = request.files.get('archivo')
    if not file:
        return jsonify({"error": "No se envió archivo"}), 400

    cloudinary_data = CloudinaryService.upload_denuncia_file(file, id_denuncia, current_user_id)

    nuevo_archivo = ArchivoDenuncia(
        id_denuncia=id_denuncia,
        nombre_archivo=cloudinary_data['public_id'],
        ruta_archivo=cloudinary_data['secure_url']
    )
    db.session.add(nuevo_archivo)
    db.session.commit()

    return archivo_schema.jsonify(nuevo_archivo), 201




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:buscar denuncias con filtros

@denuncia_bp.route('/denuncias/buscar', methods=['GET'])
@rutaProtegida("admin")
def buscar_denuncias():
    estado = request.args.get('estado')
    tipo_denuncia = request.args.get('tipo_denuncia')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    query = Denuncia.query

    if estado:
        query = query.filter_by(estado=estado)
    if tipo_denuncia:
        query = query.filter_by(tipo_denuncia=tipo_denuncia)
    if fecha_inicio:
        query = query.filter(Denuncia.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Denuncia.fecha <= fecha_fin)

    denuncias = query.all()
    return denuncia_schema.jsonify(denuncias, many=True)





#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:cambiar estado de una denuncia

@denuncia_bp.route('/admin/denuncias/<int:denuncia_id>/estado', methods=['PUT'])
@rutaProtegida('admin')
def cambiar_estado_denuncia(denuncia_id):
    try:
        data = request.json
        nuevo_estado = data.get('nuevo_estado')

        if nuevo_estado not in ['pendiente', 'en_proceso', 'resuelto', 'cancelado']:
            return jsonify({'error': 'Estado inválido'}), 400

        denuncia = Denuncia.query.get_or_404(denuncia_id)
        denuncia.estado = nuevo_estado
        db.session.commit()

        # Enviar mail al denunciante
        usuario = denuncia.usuario
        asunto = "Actualización de tu denuncia"
        contenido_html = f"""
            <h3>Hola {usuario.nombre},</h3>
            <p>El estado de tu denuncia <b>#{denuncia.id}</b> ha cambiado a: <b>{nuevo_estado.replace('_', ' ').capitalize()}</b>.</p>
            <p>Descripción: {denuncia.descripcion}</p>
            <p>Gracias por colaborar con Zoonosis Bariloche.</p>
        """
        enviar_mail_resend(usuario.email, asunto, contenido_html)

        return jsonify({'mensaje': 'Estado actualizado y mail enviado', 'nuevo_estado': nuevo_estado})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:buscar denuncias con filtros para admin

@denuncia_bp.route('/admin/denuncias/buscar', methods=['GET'])
@rutaProtegida('admin')
def buscar_denuncias_filtro():
    estado = request.args.get('estado')
    tipo_denuncia = request.args.get('tipo_denuncia')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    descripcion = request.args.get('descripcion')

    query = Denuncia.query

    if estado:
        query = query.filter(Denuncia.estado == estado)

    if tipo_denuncia:
        query = query.filter(Denuncia.tipo_denuncia == tipo_denuncia)

    if fecha_inicio and fecha_fin:
        query = query.filter(Denuncia.fecha.between(fecha_inicio, fecha_fin))

    if descripcion:
        query = query.filter(Denuncia.descripcion.ilike(f"%{descripcion}%"))

    denuncias = query.order_by(Denuncia.fecha.desc()).all()
    return jsonify(denuncia_schema.DenunciaSchema(many=True).dump(denuncias))



#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:listar detalle de una denuncia para admin

@denuncia_bp.route('/admin/denuncias/<int:denuncia_id>', methods=['GET'])
@rutaProtegida('admin')
def detalle_denuncia_admin(denuncia_id):
    denuncia = Denuncia.query.get_or_404(denuncia_id)
    result = denuncia_schema.dump(denuncia)
    result['archivos'] = ArchivoDenunciaSchema(many=True).dump(denuncia.archivos)
    return jsonify(result)




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:listar archivos de una denuncia

@denuncia_bp.route('/admin/denuncias/<int:denuncia_id>/archivos', methods=['GET'])
@rutaProtegida('admin')
def obtener_archivos_denuncia(denuncia_id):
    archivos = ArchivoDenuncia.query.filter_by(id_denuncia=denuncia_id).all()
    return jsonify(ArchivoDenunciaSchema(many=True).dump(archivos))




#* ==============================
#*  DENUNCIAS ENDPOINTS
#* ==============================
#? TODO:listar todas las denuncias para admin

@denuncia_bp.route('/admin/denuncias', methods=['GET'])
@rutaProtegida('admin')
def listar_denuncias_admin():
    
    estado = request.args.get('estado')
    tipo_denuncia = request.args.get('tipo_denuncia')
    descripcion = request.args.get('descripcion')

    query = Denuncia.query

    if estado:
        query = query.filter(Denuncia.estado == estado)
    if tipo_denuncia:
        query = query.filter(Denuncia.tipo_denuncia == tipo_denuncia)
    if descripcion:
        query = query.filter(Denuncia.descripcion.ilike(f"%{descripcion}%"))

    denuncias = query.order_by(Denuncia.fecha.desc()).all()

    # Serializar con datos del usuario
    resultado = []
    for d in denuncias:
        usuario = d.usuario
        resultado.append({
            "id": d.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "dni": usuario.dni,
            "barrio": usuario.barrio,
            "ubicacion": d.ubicacion,
            "estado": d.estado,
            "telefono": usuario.telefono,
            "tipo_denuncia": d.tipo_denuncia,
            "fecha": d.fecha.strftime("%Y-%m-%d %H:%M"),
        })

    return jsonify(resultado)