from datetime import datetime, timedelta
from functools import wraps
import logging
import uuid
import jwt
from flask import Blueprint, current_app, g , jsonify, request
from marshmallow import ValidationError
from flask import current_app as app
from app.schemas.auth_schema import ResetPasswordSchema, UsuarioRegistroSchema, LoginSchema
from werkzeug.security import generate_password_hash
from dbConfig import db
from app.models.models import Usuario, ResetPasswordToken
from app.utils.email_utils import enviar_mail_resend



auth_bp = Blueprint('auth_bp', __name__)

 



# Configuración  de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: Decorador para JWT

def rutaProtegida(*categorias_permitidas):
    """
    Decorador para proteger rutas con JWT via header n-auth.
    Valida: presencia, formato, expiración y categoría del token.
    
    Args:
        *categorias_permitidas: Roles autorizados (ej: 'admin', 'ciudadano')
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 1. Obtener y validar header
            auth_header = request.headers.get('n-auth')
            if not auth_header:
                logger.warning("Intento de acceso sin token")
                return jsonify({"status": 401, "message": "Token requerido"}), 401
            
            # 2. Limpiar token
            token = auth_header.replace("Bearer", "").replace("bearer", "").strip()
            if not token:
                logger.warning("Token vacío después de limpieza")
                return jsonify({"status": 401, "message": "Formato de token inválido"}), 401
            
            logger.info(f"Token recibido: {token[:15]}...")  # Log parcial por seguridad
            
            try:
                # 3. Decodificar token
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                # 4. Verificar expiración
                exp_timestamp = payload.get('exp')
                if exp_timestamp:
                    exp_datetime = datetime.fromtimestamp(exp_timestamp)
                    if datetime.utcnow() > exp_datetime:
                        logger.warning(f"Token expirado (expiró: {exp_datetime})")
                        return jsonify({"status": 401, "message": "Token expirado"}), 401
                
                # 5. Verificar categoría si se especificó
                if categorias_permitidas:
                    user_category = payload.get('categoria')
                    if user_category not in categorias_permitidas:
                        logger.warning(f"Intento de acceso no autorizado. Categoría: {user_category}, Requeridas: {categorias_permitidas}")
                        return jsonify({
                            "status": 403,
                            "message": f"Acceso no autorizado. Rol requerido: {', '.join(categorias_permitidas)}"
                        }), 403
                
                # 6. Adjuntar usuario al request
                request.current_user = payload
                logger.info(f"Acceso autorizado para usuario: {payload.get('id')}")
                
                return f(*args, **kwargs)
            
            except jwt.ExpiredSignatureError:
                logger.warning("Token expirado (capturado por jwt)")
                return jsonify({"status": 401, "message": "Token expirado"}), 401
            except jwt.InvalidTokenError as e:
                logger.error(f"Token inválido: {str(e)}")
                return jsonify({"status": 401, "message": "Token inválido"}), 401
            except Exception as e:
                logger.critical(f"Error inesperado: {str(e)}", exc_info=True)
                return jsonify({"status": 500, "message": "Error interno del servidor"}), 500
        
        return wrapper
    return decorator

     
#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: Registrar nuevo usuario

@auth_bp.route('/auth/register', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)  
        
        
        schema = UsuarioRegistroSchema(context={'password': data.get('password')})
        validated_data = schema.load(data)
        
        if Usuario.query.filter_by(email=validated_data['email']).first():
            return jsonify({"status": "error", "message": "Email ya registrado"}), 400
            
        if Usuario.query.filter_by(dni=validated_data['dni']).first():
            return jsonify({"status": "error", "message": "DNI ya registrado"}), 400

        
        nuevo_usuario = Usuario(
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido'],
            domicilio=validated_data['domicilio'],
            email=validated_data['email'],
            password=generate_password_hash(validated_data['password']),  
            dni=validated_data['dni'],
            telefono=validated_data.get('telefono'),
            barrio=validated_data['barrio'] 
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Usuario registrado",
            "data": {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre,
                "email": nuevo_usuario.email
            }
        }), 201

    except ValidationError as e:
        print("Errores de validación:", e.messages) 
        return jsonify({"status": "error", "message": "Error de validación", "errors": e.messages}), 400
        
    except Exception as e:
        db.session.rollback()
        print("Error interno:", str(e))  
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    
 
 
  
  
#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: Solicitar reseteo de contraseña 

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"status": "error", "message": "Email no registrado"}), 404

    # Generar token único
    token = str(uuid.uuid4())

    nuevo_token = ResetPasswordToken(token=token, user_id=usuario.id)
    db.session.add(nuevo_token)
    db.session.commit()

    # Generar enlace
    reset_url = f"https://sanidadanimalbariloche.com/auth/reset-password?token={token}"

    # Contenido HTML del correo
    html = f"""
    <h3>Hola {usuario.nombre},</h3>
    <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
    <a href="{reset_url}">Restablecer contraseña</a>
    <p>Este enlace expirará en 1 hora. Si no solicitaste esto, ignorá este correo.</p>
    """

    status, respuesta = enviar_mail_resend(usuario.email, "Restablecer contraseña", html)
    print("📨 Enviado:", status)
    print("📬 Respuesta:", respuesta)

    if status == 200 or status == 202:
        return jsonify({"status": "success", "message": "Se ha enviado el enlace al correo"}), 200
    else:
        return jsonify({"status": "error", "message": "Error al enviar correo", "detalles": respuesta}), 500






#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: resetear contraseña

@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        schema = ResetPasswordSchema(context={'password': data.get('password')})
        validated_data = schema.load(data)

        token_obj = ResetPasswordToken.query.filter_by(token=validated_data['token'], is_used=False).first()
        if not token_obj:
            return jsonify({"status": "error", "message": "Token inválido o ya usado"}), 400

        if (datetime.utcnow() - token_obj.created_at).total_seconds() > 3600:
            return jsonify({"status": "error", "message": "Token expirado"}), 400

        # Actualizar la contraseña
        usuario = token_obj.usuario
        usuario.password = generate_password_hash(validated_data['password'])
        token_obj.is_used = True

        db.session.commit()

        return jsonify({"status": "success", "message": "Contraseña actualizada correctamente"}), 200

    except ValidationError as e:
        return jsonify({"status": "error", "message": "Error de validación", "errors": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        print("Error interno:", str(e))
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    



#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: login

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        print("🟡 Entrando a /auth/login")

        data = request.get_json()
        print("📥 Datos recibidos:", data)

        schema = LoginSchema()

        try:
            schema.load(data)
            print("✅ Validación de schema OK")
        except ValidationError as err:
            print("❌ Error de validación:", err.messages)
            return jsonify({
                "status": "error",
                "message": "Datos inválidos",
                "errors": err.messages
            }), 400

        print("🔍 Buscando usuario en la DB...")
        usuario = schema.load_usuario_valido(data)
        print("👤 Usuario encontrado:", usuario)

        if usuario:
            # Se comprueba si el usuario está activo antes de generar el token.
            if not usuario.activo:
                print(f"🔒 Acceso denegado. Usuario '{usuario.email}' está inactivo.")
                return jsonify({
                    "status": "error", 
                    "message": "Usuario desactivado. Comuníquese con la zoonosis para reactivar su cuenta."
                }), 403 
            

            
            payload = {
                "usuario": data["usuario"],
                "id": usuario.id,
                "categoria": usuario.categoria,
                "exp": datetime.utcnow() + timedelta(hours=12)
            }

            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

            print("✅ Login exitoso, token generado")
            return jsonify({
                "status": "success",
                "token": token,
                "categoria": usuario.categoria
            }), 200
        else:
            print("❌ Credenciales inválidas")
            return jsonify({'status': "error", "message": "Credenciales inválidas"}), 401

    except ValidationError as err:
        print("❌ Error de validación externa:", err.messages)
        return jsonify({
            "status": "error",
            "message": "Error de validación",
            "errors": err.messages
        }), 400

    except Exception as e:
        print("🔥 Error inesperado:", str(e))
        return jsonify({'status': 500, "message": str(e)}), 500



#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: Logout

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    return jsonify({"status": "success", "message": "Sesión cerrada correctamente"}), 200



#* ==============================
#*  AUTH ENDPOINTS
#* ==============================
#? TODO: Obtener información del usuario autenticado

@auth_bp.route('/auth/me', methods=['GET'])
@rutaProtegida("ciudadano")
def obtener_usuario():
    usuario = Usuario.query.get(g.usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "categoria": usuario.categoria
        }
    }), 200
