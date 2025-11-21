import io
import base64
from datetime import datetime, date
from sqlalchemy import func, and_
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.models.models import Usuario, Animal, Denuncia, Turno, Adopcion, HistorialLibreta, Noticia
from dbConfig import db

def grafico_torta(labels, values, titulo):
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    ax.set_title(titulo)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.read()).decode('utf-8')
    plt.close(fig)
    return img_b64

def grafico_barras(labels, values, titulo, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.bar(labels, values, color='skyblue')
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.read()).decode('utf-8')
    plt.close(fig)
    return img_b64

def grafico_linea(labels, values, titulo, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.plot(labels, values, marker='o')
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.read()).decode('utf-8')
    plt.close(fig)
    return img_b64

def generar_reporte_pdf(fecha_inicio, fecha_fin):
    # Convertir fechas
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # 1. Resumen general
    total_animales = Animal.query.count()
    animales_periodo = Animal.query.filter(Animal.fecha_registro >= fecha_inicio, Animal.fecha_registro <= fecha_fin).count()
    usuarios_activos = Usuario.query.filter_by(activo=True).count()
    usuarios_nuevos = Usuario.query.filter(Usuario.fecha_registro >= fecha_inicio, Usuario.fecha_registro <= fecha_fin).count()
    denuncias_recibidas = Denuncia.query.filter(Denuncia.fecha >= fecha_inicio, Denuncia.fecha <= fecha_fin).count()
    denuncias_resueltas = Denuncia.query.filter(Denuncia.estado == 'resuelto', Denuncia.fecha >= fecha_inicio, Denuncia.fecha <= fecha_fin).count()
    denuncias_pendientes = Denuncia.query.filter(Denuncia.estado == 'pendiente', Denuncia.fecha >= fecha_inicio, Denuncia.fecha <= fecha_fin).count()
    turnos_programados = Turno.query.filter(Turno.fecha_solicitada >= fecha_inicio, Turno.fecha_solicitada <= fecha_fin).count()
    turnos_realizados = Turno.query.filter(Turno.estado == 'confirmado', Turno.fecha_solicitada >= fecha_inicio, Turno.fecha_solicitada <= fecha_fin).count()
    adopciones_realizadas = Adopcion.query.filter(Adopcion.fecha_publicacion >= fecha_inicio, Adopcion.fecha_publicacion <= fecha_fin, Adopcion.disponible == False).count()
    animales_baja = Animal.query.filter(Animal.fecha_baja >= fecha_inicio, Animal.fecha_baja <= fecha_fin).count()

    # 2. Estadísticas de animales
    animales_por_especie = db.session.query(Animal.especie, func.count(Animal.id)).group_by(Animal.especie).all()
    animales_por_raza = db.session.query(Animal.raza, func.count(Animal.id)).group_by(Animal.raza).order_by(func.count(Animal.id).desc()).limit(5).all()
    animales_por_barrio = db.session.query(Usuario.barrio, func.count(Animal.id)).join(Usuario, Usuario.id == Animal.id_propietario).group_by(Usuario.barrio).all()
    castrados = Animal.query.filter_by(esta_castrado=True).count()
    no_castrados = Animal.query.filter_by(esta_castrado=False).count()
    hoy = datetime.now()
    patente_vigente = Animal.query.filter(Animal.fecha_vencimiento_patente > hoy).count()
    vacunados = db.session.query(HistorialLibreta.tipo, func.count(HistorialLibreta.id)).filter(HistorialLibreta.tipo == 'vacuna').group_by(HistorialLibreta.tipo).all()
    desparasitados = db.session.query(HistorialLibreta.tipo, func.count(HistorialLibreta.id)).filter(HistorialLibreta.tipo == 'desparasitación').group_by(HistorialLibreta.tipo).all()
    animales_adoptados = Adopcion.query.filter_by(disponible=False).count()

    # 3. Estadísticas de denuncias
    denuncias_por_tipo = db.session.query(Denuncia.tipo_denuncia, func.count(Denuncia.id)).filter(Denuncia.fecha >= fecha_inicio, Denuncia.fecha <= fecha_fin).group_by(Denuncia.tipo_denuncia).all()
    denuncias_por_barrio = db.session.query(Denuncia.barrio, func.count(Denuncia.id)).filter(Denuncia.fecha >= fecha_inicio, Denuncia.fecha <= fecha_fin).group_by(Denuncia.barrio).all()
    denuncias_resueltas_vs_pendientes = [
        ('Resueltas', denuncias_resueltas),
        ('Pendientes', denuncias_pendientes)
    ]
    
    

    # 4. Estadísticas de turnos
    turnos_por_tipo = db.session.query(Turno.tipo_turno, func.count(Turno.id)).filter(Turno.fecha_solicitada >= fecha_inicio, Turno.fecha_solicitada <= fecha_fin).group_by(Turno.tipo_turno).all()
    turnos_por_estado = db.session.query(Turno.estado, func.count(Turno.id)).filter(Turno.fecha_solicitada >= fecha_inicio, Turno.fecha_solicitada <= fecha_fin).group_by(Turno.estado).all()
    turnos_por_barrio = db.session.query(Usuario.barrio, func.count(Turno.id)).join(Usuario, Usuario.id == Turno.id_usuario).filter(Turno.fecha_solicitada >= fecha_inicio, Turno.fecha_solicitada <= fecha_fin).group_by(Usuario.barrio).all()

    # 5. Otros datos útiles
    noticias_publicadas = Noticia.query.filter(Noticia.fecha >= fecha_inicio, Noticia.fecha <= fecha_fin, Noticia.publicado == True).count()
    animales_en_adopcion = Adopcion.query.filter_by(disponible=True).count()
    animales_adoptados_periodo = Adopcion.query.filter(Adopcion.fecha_publicacion >= fecha_inicio, Adopcion.fecha_publicacion <= fecha_fin, Adopcion.disponible == False).count()
    registros_libreta = HistorialLibreta.query.filter(HistorialLibreta.fecha >= fecha_inicio, HistorialLibreta.fecha <= fecha_fin).count()
    usuarios_periodo = Usuario.query.filter(Usuario.fecha_registro >= fecha_inicio, Usuario.fecha_registro <= fecha_fin).count()

    # 6. Gráficos
    grafico_especies = grafico_torta(
        [e[0] for e in animales_por_especie],
        [e[1] for e in animales_por_especie],
        "Animales por Especie"
    )
    grafico_castrados = grafico_barras(
        ['Castrados', 'No Castrados'],
        [castrados, no_castrados],
        "Animales Castrados vs No Castrados",
        "Estado", "Cantidad"
    )
    grafico_denuncias_tipo = grafico_barras(
        [d[0] for d in denuncias_por_tipo],
        [d[1] for d in denuncias_por_tipo],
        "Denuncias por Tipo",
        "Tipo", "Cantidad"
    )
    grafico_animales_raza = grafico_barras(
        [r[0] for r in animales_por_raza],
        [r[1] for r in animales_por_raza],
        "Top 5 Razas de Animales",
        "Raza", "Cantidad"
    )
    grafico_animales_barrio = grafico_barras(
        [b[0] for b in animales_por_barrio],
        [b[1] for b in animales_por_barrio],
        "Animales por Barrio",
        "Barrio", "Cantidad"
    )

    # 7. Información institucional
    nombre_sistema = "Sanidad Animal Bariloche"
    logo_url = "https://i.ibb.co/LDWM45C6/logoS.png"  
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    periodo = f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"

    # 8. Renderizar HTML
    from flask import render_template
    html = render_template('reporte.html',
        total_animales=total_animales,
        animales_periodo=animales_periodo,
        usuarios_activos=usuarios_activos,
        usuarios_nuevos=usuarios_nuevos,
        denuncias_recibidas=denuncias_recibidas,
        denuncias_resueltas=denuncias_resueltas,
        denuncias_pendientes=denuncias_pendientes,
        turnos_programados=turnos_programados,
        turnos_realizados=turnos_realizados,
        adopciones_realizadas=adopciones_realizadas,
        animales_baja=animales_baja,
        patente_vigente=patente_vigente,
        vacunados=vacunados,
        desparasitados=desparasitados,
        animales_adoptados=animales_adoptados,
        denuncias_por_barrio=denuncias_por_barrio,
        turnos_por_tipo=turnos_por_tipo,
        turnos_por_estado=turnos_por_estado,
        turnos_por_barrio=turnos_por_barrio,
        noticias_publicadas=noticias_publicadas,
        animales_en_adopcion=animales_en_adopcion,
        animales_adoptados_periodo=animales_adoptados_periodo,
        registros_libreta=registros_libreta,
        usuarios_periodo=usuarios_periodo,
        grafico_especies=grafico_especies,
        grafico_castrados=grafico_castrados,
        grafico_denuncias_tipo=grafico_denuncias_tipo,
        grafico_animales_raza=grafico_animales_raza,
        grafico_animales_barrio=grafico_animales_barrio,
        nombre_sistema=nombre_sistema,
        logo_url=logo_url,
        fecha_generacion=fecha_generacion,
        periodo=periodo
    )

    # 9. Convertir a PDF
    from weasyprint import HTML as WeasyHTML
    pdf = WeasyHTML(string=html).write_pdf()
    return io.BytesIO(pdf)