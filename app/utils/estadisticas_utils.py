from sqlalchemy import func
from datetime import datetime, timedelta
from dbConfig import db
from app.models.models import Denuncia, HistorialLibreta, Turno, Usuario, Animal, Adopcion

def armar_contexto_estadisticas():
    hoy = datetime.now()
    inicio_mes = hoy.replace(day=1)
    # Calcular inicio y fin del mes anterior
    mes_anterior = inicio_mes - timedelta(days=1)
    inicio_mes_anterior = mes_anterior.replace(day=1)
    fin_mes_anterior = inicio_mes - timedelta(seconds=1)

    # Usuarios registrados este mes
    usuarios_mes = db.session.query(func.count(Usuario.id)).filter(Usuario.fecha_registro >= inicio_mes).scalar()
    total_usuarios = db.session.query(func.count(Usuario.id)).scalar()

    # Animales registrados por especie este mes
    animales_mes = db.session.query(
        Animal.especie, func.count(Animal.id)
    ).filter(Animal.fecha_registro >= inicio_mes).group_by(Animal.especie).all()

    # Animales patentados vs no patentados
    patentados = db.session.query(func.count(Animal.id)).filter(Animal.estado == 'aprobado').scalar()
    no_patentados = db.session.query(func.count(Animal.id)).filter(Animal.estado != 'aprobado').scalar()

    # Adopciones este mes
    adopciones_mes = db.session.query(func.count(Adopcion.id)).filter(Adopcion.fecha_publicacion >= inicio_mes).scalar()

    # Denuncias por tipo y resueltas este mes
    denuncias_tipo = db.session.query(
        Denuncia.tipo_denuncia, func.count(Denuncia.id)
    ).filter(Denuncia.fecha >= inicio_mes).group_by(Denuncia.tipo_denuncia).all()
    denuncias_resueltas = db.session.query(func.count(Denuncia.id)).filter(
        Denuncia.fecha >= inicio_mes,
        Denuncia.estado == 'resuelto'
    ).scalar()
    total_denuncias_mes = db.session.query(func.count(Denuncia.id)).filter(Denuncia.fecha >= inicio_mes).scalar()

    # Denuncias mes anterior
    total_denuncias_mes_anterior = db.session.query(func.count(Denuncia.id)).filter(
        Denuncia.fecha >= inicio_mes_anterior,
        Denuncia.fecha < inicio_mes
    ).scalar()
    if total_denuncias_mes_anterior == 0:
        variacion = "N/A"
    else:
        variacion_num = ((total_denuncias_mes - total_denuncias_mes_anterior) / total_denuncias_mes_anterior) * 100
        variacion = f"{variacion_num:+.1f}%"

    # Turnos confirmados este mes
    turnos_confirmados = db.session.query(func.count(Turno.id)).filter(
        Turno.estado == 'confirmado',
        Turno.fecha_turno >= inicio_mes
    ).scalar()

    # Castraciones este mes
    castraciones = db.session.query(func.count(Turno.id)).filter(
        Turno.tipo_turno.in_([
            'castracion_canino_macho',
            'castracion_canino_hembra',
            'castracion_felino_macho',
            'castracion_felino_hembra'
        ]),
        Turno.fecha_turno >= inicio_mes,
        Turno.estado == 'confirmado'
    ).scalar()

    # Vacunaciones este mes
    vacunaciones = db.session.query(func.count(Turno.id)).filter(
        Turno.tipo_turno == 'vacunacion_antirrabica',
        Turno.fecha_turno >= inicio_mes,
        Turno.estado == 'confirmado'
    ).scalar()

    # Barrio con más denuncias este mes
    denuncias_barrio = db.session.query(
        Denuncia.barrio, func.count(Denuncia.id)
    ).filter(Denuncia.fecha >= inicio_mes).group_by(Denuncia.barrio).all()
    barrio_top = max(denuncias_barrio, key=lambda x: x[1])[0] if denuncias_barrio else "Ninguno"

    # Animales por especie (mes)
    animales_str = ", ".join([f"{cant} {especie}(s)" for especie, cant in animales_mes]) if animales_mes else "ningún animal"

    # Armar el texto tipo noticia
    texto = (
        f"Reporte mensual de Zoonosis Bariloche ({hoy.strftime('%B %Y')}):\n"
        f"Se registraron {usuarios_mes} nuevos usuarios este mes (total: {total_usuarios}). "
        f"En cuanto a animales, se inscribieron {animales_str} este mes. "
        f"Actualmente, {patentados} animales están patentados y {no_patentados} no lo están. "
        f"Se concretaron {adopciones_mes} adopciones.\n"
        f"En lo que va del mes, hubo {total_denuncias_mes} denuncias, de las cuales {denuncias_resueltas} fueron resueltas "
        f"({variacion} respecto al mes anterior). "
    )
    if denuncias_tipo:
        texto += "Por tipo de denuncia: " + ", ".join([f"{cant} de {tipo.replace('_', ' ')}" for tipo, cant in denuncias_tipo]) + ". "
    if denuncias_barrio:
        texto += f"El barrio con más denuncias fue {barrio_top}. "
    texto += (
        f"Se confirmaron {turnos_confirmados} turnos, incluyendo {castraciones} castraciones y {vacunaciones} vacunaciones antirrábicas."
    )

    return texto






def obtener_datos_dashboard():
    """
    Recopila y estructura los datos numéricos para el dashboard principal.
    Devuelve un diccionario listo para ser convertido a JSON.
    """
    hoy = datetime.now()

    # 1. Datos para los KPI Cards
    animales_registrados = db.session.query(func.count(Animal.id)).scalar() or 0
    
    usuarios_activos = db.session.query(func.count(Usuario.id)).filter(Usuario.activo == True).scalar() or 0
    denuncias_pendientes = db.session.query(func.count(Denuncia.id)).filter(Denuncia.estado == 'pendiente').scalar() or 0
    turnos_programados = db.session.query(func.count(Turno.id)).filter(Turno.estado == 'confirmado', Turno.fecha_turno >= hoy).scalar() or 0
    en_adopcion = db.session.query(func.count(Adopcion.id)).filter(Adopcion.disponible == True).scalar() or 0
    
    # 2. Datos para el Gráfico de Barras (Animales por Especie)
    animales_por_especie_query = db.session.query(
        Animal.especie, func.count(Animal.id)
    ).group_by(Animal.especie).all()
    
    animales_por_especie_data = [
        {"name": especie.capitalize(), "total": cantidad} for especie, cantidad in animales_por_especie_query
    ]

    # 3. Datos para el Gráfico de Torta (Estado de Vacunación)
    total_animales = animales_registrados
    # CORRECCIÓN IMPORTANTE: Se cuenta sobre el historial de la libreta.
    vacunados = db.session.query(func.count(db.distinct(HistorialLibreta.id_animal))).\
        filter(HistorialLibreta.tipo.like('%vacuna%')).scalar() or 0
        
    no_vacunados = total_animales - vacunados
    
    porc_vacunados = round((vacunados / total_animales) * 100) if total_animales > 0 else 0
    porc_no_vacunados = 100 - porc_vacunados

    estado_vacunacion_data = [
        {"name": "Vacunados", "value": porc_vacunados, "color": "#28A745"}, # Verde
        {"name": "No Vacunados", "value": porc_no_vacunados, "color": "#DC3545"} # Rojo
    ]

    # --- Construye el diccionario final ---
    dashboard_data = {
        "kpi_cards": {
            "animalesRegistrados": animales_registrados,
            "usuariosActivos": usuarios_activos,
            "denunciasPendientes": denuncias_pendientes,
            "turnosProgramados": turnos_programados,
            "enAdopcion": en_adopcion
        },
        "animalesPorEspecie": animales_por_especie_data,
        "estadoVacunacion": estado_vacunacion_data
    }

    return dashboard_data