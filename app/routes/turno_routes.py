
from datetime import date
from flask import Blueprint, jsonify, request

from app.models.models import Turno
from app.routes.auth_routes import rutaProtegida
from app.schemas import turno_schema
from app.utils.email_utils import enviar_mail_resend
from dbConfig import db

turno_bp = Blueprint('turno_bp', __name__)

turno_schema = turno_schema.TurnoSchema()


#* ==============================
#*  TURNO ENDPOINTS
#* ==============================
#? TODO: SOLICITAR PRE-TURNO

@turno_bp.route('/pre-turnos', methods=['POST'])
@rutaProtegida('ciudadano')
def solicitar_pre_turno():
    current_user = request.current_user
    current_user_id = current_user['id']
    data = request.json

    fecha_solicitada = data.get('fecha_solicitada')
    if not fecha_solicitada:
        fecha_solicitada = date.today().isoformat()

    nuevo_turno = Turno(
        id_usuario=current_user_id,
        id_animal=data['id_animal'],
        tipo_turno=data['tipo_turno'],
        fecha_solicitada=fecha_solicitada,
        estado='pendiente'
    )
    db.session.add(nuevo_turno)
    db.session.commit()

    usuario = nuevo_turno.usuario
    asunto = "Confirmación de solicitud de pre-turno"
    contenido_html = f"""
        <h3>Hola {usuario.nombre},</h3>
        <p>Hemos recibido correctamente tu solicitud de pre-turno para <b>{data['tipo_turno'].replace('_', ' ').capitalize()}</b>.</p>
        <p>Nuestro equipo revisará la solicitud y pronto recibirás un segundo correo con la confirmación final, incluyendo la fecha y hora asignadas para tu turno.</p>
        <br>
        <p>Muchas gracias,</p>
        <p><b>El equipo de Zoonosis Bariloche</b></p>
    """
    enviar_mail_resend(usuario.email, asunto, contenido_html)

    return jsonify(turno_schema.dump(nuevo_turno)), 201



#* ==============================
#*  TURNO ENDPOINTS
#* ==============================
#? TODO: VER MIS PRE-TURNOS

@turno_bp.route('/pre-turnos/mis', methods=['GET'])
@rutaProtegida('ciudadano')
def ver_mis_pre_turnos():
    current_user = request.current_user
    turnos = Turno.query.filter_by(id_usuario=current_user['id']).order_by(Turno.fecha_solicitada.desc()).all()
    return jsonify(turno_schema.dump(turnos, many=True))



#* ==============================
#*  TURNO ENDPOINTS
#* ==============================
#? TODO: LISTAR PRE-TURNOS ADMIN

@turno_bp.route('/admin/pre-turnos', methods=['GET'])
@rutaProtegida('admin')
def listar_pre_turnos_admin():
    estado = request.args.get('estado')
    tipo_turno = request.args.get('tipo_turno')
    query = Turno.query
    if estado:
        query = query.filter_by(estado=estado)
    if tipo_turno:
        query = query.filter_by(tipo_turno=tipo_turno)
    turnos = query.order_by(Turno.fecha_solicitada.desc()).all()
    return jsonify(turno_schema.dump(turnos, many=True))




#* ==============================
#*  TURNO ENDPOINTS
#* ==============================
#? TODO: CONFIRMAR PRE-TURNO

@turno_bp.route('/admin/pre-turnos/<int:turno_id>/confirmar', methods=['PUT'])
@rutaProtegida('admin')
def confirmar_pre_turno(turno_id):
    data = request.json
    turno = Turno.query.get_or_404(turno_id)
    turno.fecha_turno = data['fecha_turno']
    turno.estado = 'confirmado'
    turno.instrucciones = data.get('instrucciones')
    db.session.commit()

    # Enviar mail al usuario
    usuario = turno.usuario
    asunto = "Pre-turno confirmado"
    contenido_html = f"""
        <h3>Hola {usuario.nombre},</h3>
        <p>Tu pre-turno para <b>{turno.tipo_turno.replace('_', ' ').capitalize()}</b> fue confirmado para el día <b>{turno.fecha_turno.strftime('%Y-%m-%d %H:%M')}</b>.</p>
        <p>Instrucciones: {turno.instrucciones or 'No hay instrucciones adicionales.'}</p>
    """
    enviar_mail_resend(usuario.email, asunto, contenido_html)

    return jsonify(turno_schema.dump(turno))




#* ==============================
#*  TURNO ENDPOINTS
#* ==============================
#? TODO: CANCELAR PRE-TURNO

@turno_bp.route('/admin/pre-turnos/<int:turno_id>/cancelar', methods=['PUT'])
@rutaProtegida('admin')
def cancelar_pre_turno(turno_id):
    data = request.json
    turno = Turno.query.get_or_404(turno_id)
    turno.estado = 'cancelado'
    turno.motivo_cancelacion = data.get('motivo_cancelacion')
    db.session.commit()

    # Enviar mail al usuario
    usuario = turno.usuario
    asunto = "Pre-turno cancelado"
    contenido_html = f"""
        <h3>Hola {usuario.nombre},</h3>
        <p>Lamentamos informarte que tu pre-turno para <b>{turno.tipo_turno.replace('_', ' ').capitalize()}</b> fue cancelado.</p>
        <p>Motivo: {turno.motivo_cancelacion or 'No se especificó motivo.'}</p>
    """
    enviar_mail_resend(usuario.email, asunto, contenido_html)

    return jsonify(turno_schema.dump(turno))