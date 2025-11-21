import io
from datetime import datetime
from sqlalchemy import func
from app.models.models import Usuario, Animal, Denuncia, Turno, Adopcion, HistorialLibreta, Noticia
from dbConfig import db
from flask import render_template
from weasyprint import HTML as WeasyHTML
import base64


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def crear_grafico_moderno(labels, values, titulo, tipo='bar', fontsize=12):
    """
    Crea un gráfico de Matplotlib con un estilo oscuro y moderno,
    y lo devuelve como una imagen en formato base64.
    """
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120) 
    fig.patch.set_facecolor('#1E1E2E')
    ax.set_facecolor('#1E1E2E')

    colors = ['#00f2fe', '#4facfe', '#00c9ff', '#92fe9d', '#f8ffae', '#ffaaa5', '#a2d2ff']

    if tipo == 'pie':
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
               wedgeprops={'edgecolor': '#1E1E2E', 'linewidth': 2}, 
               textprops={'color': 'white', 'weight': 'bold', 'fontsize': fontsize})
    elif tipo == 'bar':
        bars = ax.bar(labels, values, color=colors)
        ax.bar_label(bars, fmt='%d', color='white', fontsize=fontsize - 1, padding=3)
        ax.yaxis.grid(True, linestyle='--', which='major', color='gray', alpha=.25)

    ax.set_title(titulo.upper(), color='white', fontsize=fontsize + 4, weight='bold', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#444444')
    ax.spines['left'].set_color('#444444')
    ax.tick_params(axis='x', colors='white', rotation=20, labelsize=fontsize)
    ax.tick_params(axis='y', colors='white', labelsize=fontsize)

    img = io.BytesIO()
    plt.tight_layout(pad=1.5)
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), transparent=True)
    plt.close(fig)
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')

def generar_reporte_pdf(fecha_inicio, fecha_fin):
    # --- 1. CONSULTAS A LA BASE DE DATOS ---
    fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Contadores para las cards
    total_animales = Animal.query.count()
    animales_periodo = Animal.query.filter(Animal.fecha_registro.between(fecha_inicio_dt, fecha_fin_dt)).count()
    usuarios_activos = Usuario.query.filter_by(activo=True).count()
    usuarios_nuevos = Usuario.query.filter(Usuario.fecha_registro.between(fecha_inicio_dt, fecha_fin_dt)).count()
    denuncias_recibidas = Denuncia.query.filter(Denuncia.fecha.between(fecha_inicio_dt, fecha_fin_dt)).count()
    denuncias_resueltas = Denuncia.query.filter(Denuncia.estado == 'resuelto', Denuncia.fecha.between(fecha_inicio_dt, fecha_fin_dt)).count()
    turnos_programados = Turno.query.filter(Turno.fecha_solicitada.between(fecha_inicio_dt, fecha_fin_dt)).count()
    turnos_realizados = Turno.query.filter(Turno.estado == 'confirmado', Turno.fecha_solicitada.between(fecha_inicio_dt, fecha_fin_dt)).count()
    adopciones_realizadas = Adopcion.query.filter(Adopcion.disponible == False, Adopcion.fecha_publicacion.between(fecha_inicio_dt, fecha_fin_dt)).count()
    animales_en_adopcion = Adopcion.query.filter_by(disponible=True).count()
    noticias_publicadas = Noticia.query.filter(Noticia.fecha.between(fecha_inicio_dt, fecha_fin_dt)).count()
    patente_vigente = Animal.query.filter(Animal.fecha_vencimiento_patente > datetime.now()).count()
    castrados = Animal.query.filter_by(esta_castrado=True).count()
    animales_baja = Animal.query.filter(Animal.fecha_baja.isnot(None), Animal.fecha_baja.between(fecha_inicio_dt, fecha_fin_dt)).count()

    # Consultas para los datos de los gráficos
    denuncias_por_tipo_q = db.session.query(Denuncia.tipo_denuncia, func.count(Denuncia.id)).filter(Denuncia.fecha.between(fecha_inicio_dt, fecha_fin_dt)).group_by(Denuncia.tipo_denuncia).all()
    animales_por_especie_q = db.session.query(Animal.especie, func.count(Animal.id)).group_by(Animal.especie).all()
    turnos_por_tipo_q = db.session.query(Turno.tipo_turno, func.count(Turno.id)).filter(Turno.fecha_solicitada.between(fecha_inicio_dt, fecha_fin_dt)).group_by(Turno.tipo_turno).all()
    animales_por_barrio_q = db.session.query(Usuario.barrio, func.count(Animal.id)).join(Usuario, Animal.id_propietario == Usuario.id).filter(Usuario.barrio.isnot(None)).group_by(Usuario.barrio).order_by(func.count(Animal.id).desc()).limit(5).all()
    
    # --- 2. CÁLCULO DE TOTALES PARA GRÁFICOS (ORDEN CORREGIDO) ---
    # Ahora se calculan DESPUÉS de que las variables _q existen.
    total_denuncias_periodo = sum(int(d[1]) for d in denuncias_por_tipo_q)
    total_turnos_periodo = sum(int(t[1]) for t in turnos_por_tipo_q)

    # --- 3. GENERACIÓN DE GRÁFICOS COMO IMÁGENES ---
    grafico_denuncias = crear_grafico_moderno([str(d[0]).replace('_', ' ').capitalize() for d in denuncias_por_tipo_q], [int(d[1]) for d in denuncias_por_tipo_q], "Denuncias por Tipo (Período)", tipo='bar')
    grafico_especies = crear_grafico_moderno([str(e[0]) for e in animales_por_especie_q], [int(e[1]) for e in animales_por_especie_q], "Distribución por Especie", tipo='pie')
    grafico_turnos = crear_grafico_moderno([str(t[0]).replace('_', ' ').capitalize() for t in turnos_por_tipo_q], [int(t[1]) for t in turnos_por_tipo_q], "Turnos por Tipo (Período)", tipo='bar')
    grafico_patentes = crear_grafico_moderno(['Vigentes', 'No Vigentes'], [patente_vigente, total_animales - patente_vigente], "Estado de Patentes", tipo='pie')
    grafico_castrados = crear_grafico_moderno(['Castrados', 'No Castrados'], [castrados, total_animales - castrados], "Estado de Castraciones", tipo='pie')
    grafico_barrios = crear_grafico_moderno([str(b[0]) for b in animales_por_barrio_q], [int(b[1]) for b in animales_por_barrio_q], "Top 5 Barrios con más Animales", tipo='bar')

    # --- 4. INFORMACIÓN INSTITUCIONAL ---
    nombre_sistema = "Sanidad Animal Bariloche"
    logo_url = "https://i.ibb.co/LDWM45C6/logoS.png"
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    periodo = f"{fecha_inicio_dt.strftime('%d/%m/%Y')} - {fecha_fin_dt.strftime('%d/%m/%Y')}"
    
    # --- 5. PREPARACIÓN DEL CONTEXTO Y RENDERIZADO DE HTML ---
    context = {
        # --- Datos para las Cards ---
        "total_animales": total_animales,
        "animales_periodo": animales_periodo,
        "usuarios_activos": usuarios_activos,
        "usuarios_nuevos": usuarios_nuevos,
        "denuncias_recibidas": denuncias_recibidas,
        "denuncias_resueltas": denuncias_resueltas,
        "turnos_programados": turnos_programados,
        "turnos_realizados": turnos_realizados,
        "adopciones_realizadas": adopciones_realizadas,
        "animales_en_adopcion": animales_en_adopcion,
        "noticias_publicadas": noticias_publicadas,
        "patente_vigente": patente_vigente,
        "castrados": castrados,
        "animales_baja": animales_baja,

        # --- Datos para los Gráficos (Imágenes) ---
        "grafico_denuncias": grafico_denuncias,
        "grafico_especies": grafico_especies,
        "grafico_turnos": grafico_turnos,
        "grafico_patentes": grafico_patentes,
        "grafico_castrados": grafico_castrados,
        "grafico_barrios": grafico_barrios,

        # --- Datos para los Totales debajo de los Gráficos ---
        "total_denuncias_periodo": total_denuncias_periodo,
        "total_turnos_periodo": total_turnos_periodo,
        
        # --- Información Institucional ---
        "nombre_sistema": nombre_sistema,
        "logo_url": logo_url,
        "fecha_generacion": fecha_generacion,
        "periodo": periodo
    }
    
    html_string = render_template('reporte.html', **context)
    
    # --- 6. CONVERSIÓN A PDF ---
    pdf_bytes = WeasyHTML(string=html_string).write_pdf()
    return io.BytesIO(pdf_bytes)