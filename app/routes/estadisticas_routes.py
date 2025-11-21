import zoneinfo
from flask import Blueprint, jsonify, request, send_file
from sqlalchemy import func
from app.routes.auth_routes import rutaProtegida
from app.utils.estadisticas_utils import armar_contexto_estadisticas, obtener_datos_dashboard
from app.utils.huggingface_utils import resumir_texto_huggingface
from app.models.models import  Adopcion, Animal, Denuncia, ResumenIA, Turno, Usuario
from datetime import datetime
from dbConfig import db
from datetime import timezone
from app.utils.reportes import generar_reporte_pdf             


estadisticas_bp = Blueprint('estadisticas', __name__)



#* ==============================
#*  ESTADISTICAS ENDPOINTS
#* ==============================
#? TODO: LISTAR RESUMENES CON IA


@estadisticas_bp.route('/estadisticas/resumen-ia', methods=['GET'])
@rutaProtegida('admin')
def obtener_resumen_ia():
    resumen_ia = ResumenIA.query.order_by(ResumenIA.fecha_actualizacion.desc()).first()
    if resumen_ia:
       
        dt_utc = resumen_ia.fecha_actualizacion
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        fecha_arg = dt_utc.astimezone(zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires"))
        return jsonify({
            "resumen": resumen_ia.texto,
            "fecha_actualizacion": fecha_arg.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({
            "resumen": "",
            "fecha_actualizacion": None
        })
        

#* ==============================
#*  ESTADISTICAS ENDPOINTS
#* ==============================
#? TODO: GEMERAR RESUMENES CON IA
        
@estadisticas_bp.route('/estadisticas/resumen-ia', methods=['POST'])
@rutaProtegida('admin')
def generar_resumen_ia():
    contexto = armar_contexto_estadisticas()
    print("Resumen generado:", contexto)
    resumen_ia = ResumenIA(texto=contexto, fecha_actualizacion=datetime.utcnow())
    db.session.add(resumen_ia)
    db.session.commit()
    return jsonify({
        "resumen": contexto,
        "fecha_actualizacion": resumen_ia.fecha_actualizacion
    })
    
    


#* ==============================
#*  ESTADISTICAS ENDPOINTS
#* ==============================
#? TODO: MOSTRAR ESTADISTICAS DEL DASHBOARD

@estadisticas_bp.route('/estadisticas/dashboard', methods=['GET'])
@rutaProtegida('admin')
def mostrar_datos_texto():
    """
    Endpoint que devuelve todos los datos necesarios para renderizar el dashboard principal.
    """
    try:
        # Llama a la función de utils que hace todo el trabajo 
        data = obtener_datos_dashboard()
        return jsonify(data), 200
    except Exception as e:
        
        print(f"Error al generar datos del dashboard: {e}")
        return jsonify({"error": "No se pudieron generar los datos del dashboard"}), 500




#* ==============================
#*  ESTADISTICAS ENDPOINTS
#* ==============================
#? TODO: MOSTAR DATOS DEL DASHBOARD CON FILTROS DE FECHA

@estadisticas_bp.route('/dashboard/data', methods=['GET'])
@rutaProtegida('admin')
def mostrar_datos_dashboard():
    try:
        
        start_date_str = request.args.get('from')
        end_date_str = request.args.get('to')
        
        data = obtener_datos_dashboard(start_date_str, end_date_str)
        return jsonify(data), 200
    except Exception as e:
        print(f"Error al generar datos del dashboard: {e}")
        return jsonify({"error": "No se pudieron generar los datos del dashboard"}), 500
    
    


#* ==============================
#*  ESTADISTICAS ENDPOINTS
#* ==============================
#? TODO: GENERAR REPORTE EN PDF

@estadisticas_bp.route('/reporte', methods=['POST'])
@rutaProtegida('admin')
def reporte():
    data = request.get_json()
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "Debe enviar fecha_inicio y fecha_fin en formato YYYY-MM-DD"}), 400
    pdf = generar_reporte_pdf(fecha_inicio, fecha_fin)
    return send_file(pdf, mimetype='application/pdf', as_attachment=True, download_name='reporte.pdf')