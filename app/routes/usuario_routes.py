
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError


from app.models.models import Usuario
from app.routes.auth_routes import rutaProtegida
from app.schemas.usuario_schema import UsuarioSchema, UsuarioUpdateSchema , AdminUsuarioUpdateSchema, CiudadanoSchema
from dbConfig import db

usuario_bp = Blueprint('usuario_bp', __name__)
usuario_schema = UsuarioSchema() 
usuarios_schema = UsuarioSchema(many=True)



#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: LISTAR TODOS LOS USUARIOS

@usuario_bp.route('/usuarios', methods=['GET'])
@rutaProtegida('admin')
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(usuarios)), 200



#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: OBTENER USUARIO POR ID

@usuario_bp.route('/usuarios/<int:id>', methods=['GET'])
@rutaProtegida('admin')
def obtener_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario_schema.dump(usuario)), 200



#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: DESACTIVAR USUARIO POR ID

@usuario_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@rutaProtegida('admin')
def desactivar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if not usuario.activo:
        return jsonify({'mensaje': 'El usuario ya estaba inactivo'}), 200

    usuario.activo = False
    db.session.commit()

    return jsonify({'mensaje': 'Usuario desactivado correctamente'}), 200


#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: ACTIVAR USUARIO POR ID

@usuario_bp.route('/usuarios/<int:id>/activar', methods=['PUT'])
@rutaProtegida('admin')
def activar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if usuario.activo:
        return jsonify({'mensaje': 'El usuario ya estaba activo'}), 200

    usuario.activo = True
    db.session.commit()

    return jsonify({'mensaje': 'Usuario activado correctamente'}), 200




#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: BUSCAR USUARIOS POR NOMBRE O DNI

@usuario_bp.route('/usuarios/buscar', methods=['GET'])
@rutaProtegida('admin')
def buscar_usuarios():
    nombre = request.args.get('nombre')
    dni = request.args.get('dni')

    query = Usuario.query
    if nombre:
        query = query.filter(Usuario.nombre.ilike(f'%{nombre}%'))
    if dni:
        query = query.filter(Usuario.dni.ilike(f'%{dni}%'))

    resultados = query.all()
    return usuarios_schema.dump(resultados), 200



#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: ACTUALIZAR MI PERFIL

@usuario_bp.route('/usuarios/me', methods=['PUT'])
@rutaProtegida('ciudadano')
def actualizar_mi_perfil():
    try:
        current_user = request.current_user
        usuario = Usuario.query.get(current_user['id'])
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        schema = UsuarioUpdateSchema()
        validated_data = schema.load(request.get_json())

        # Actualiza solo campos enviados
        for campo, valor in validated_data.items():
            if valor is not None:
                setattr(usuario, campo, valor)

        db.session.commit()
        
       
        return jsonify({
            'mensaje': 'Perfil actualizado',
            'usuario': schema.dump(usuario)  
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'detalles': e.messages}), 400
    

#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: ACTUALIZAR USUARIO POR ID (ADMIN)

@usuario_bp.route('/admin/usuarios/<int:id>', methods=['PUT'])
@rutaProtegida('admin')
def admin_actualizar_usuario(id):
    try:
        current_user = request.current_user
        if current_user['categoria'] != 'admin':
            return jsonify({'error': 'Acceso denegado'}), 403

        usuario = Usuario.query.get_or_404(id)
        data = request.get_json()
        schema = AdminUsuarioUpdateSchema()  
        validated_data = schema.load(data)

        # Actualiza todos los campos (incluyendo 'categoria' y 'activo')
        for campo, valor in validated_data.items():
            setattr(usuario, campo, valor)

        db.session.commit()
        return jsonify({
            'mensaje': 'Usuario actualizado por admin',
            'usuario': usuario_schema.dump(usuario)
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'detalles': e.messages}), 400
    
    
 
 
 
#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: OBTENER MI PERFIL

@usuario_bp.route('/usuarios/me', methods=['GET'])
@rutaProtegida('ciudadano')
def obtener_mi_perfil():
    current_user = request.current_user
    usuario = Usuario.query.get(current_user['id'])
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    schema = UsuarioSchema()
    return jsonify(schema.dump(usuario)), 200




#* ==============================
#*  USUARIO ENDPOINTS
#* ==============================
#? TODO: LISTAR USUARIOS CIUDADANOS

@usuario_bp.route('/usuarios/ciudadanos', methods=['GET'])
@rutaProtegida('admin')
def listar_usuarios_ciudadanos():
    try:
        
        ciudadano_schema = CiudadanoSchema(many=True)

        ciudadanos = Usuario.query.filter_by(categoria='ciudadano').all()

    
        resultado = ciudadano_schema.dump(ciudadanos)
        
        return jsonify(resultado), 200

    except Exception as e:
    
        return jsonify({"error": "Error al obtener la lista de ciudadanos"}), 500