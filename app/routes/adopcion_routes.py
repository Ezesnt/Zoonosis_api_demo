
from flask import Blueprint, jsonify, request

from app.models.models import Adopcion, Animal, Usuario
from app.routes.auth_routes import rutaProtegida
from dbConfig import db

adopcion_bp = Blueprint('adopcion_bp', __name__)



#* ==============================
#*  ADOPCIONES ENDPOINTS
#* ==============================
#? TODO:Publicar una adopcion

@adopcion_bp.route('/adopciones/publicar/<int:id>', methods=['POST'])
@rutaProtegida('admin')
def publicar_adopcion(id):
    try:
        data = request.json
        detalle = data.get('detalle', '')
        url = data.get('url')

        if not url:
            return jsonify({"error": "Falta la url de contacto"}), 400

        animal = Animal.query.get_or_404(id)

        # VALIDACIÓN: No permitir publicar si el animal tiene dueño
        if animal.id_propietario is not None:
            return jsonify({"error": "El animal ya tiene dueño, no puede ser publicado en adopcion"}), 400

        # VALIDACIÓN: No permitir publicar si ya está en adopción
        if animal.adopcion:
            return jsonify({"error": "El animal ya está publicado en adopcion"}), 400

        nueva_adopcion = Adopcion(
            id_animal=id,
            detalle=detalle,
            url=url,
            disponible=True
        )

        db.session.add(nueva_adopcion)
        db.session.commit()

        return jsonify({"mensaje": "Animal publicado en adopción exitosamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al publicar en adopción", "detalle": str(e)}), 500



#* ==============================
#*  ADOPCIONES ENDPOINTS
#* ==============================
#? TODO:mostrar todas la adopciones


@adopcion_bp.route('/adopciones', methods=['GET'])
def listar_adopciones():
    especie = request.args.get('especie')
    
    query = Adopcion.query.filter_by(disponible=True).join(Animal)

    if especie:
        query = query.filter(Animal.especie == especie)

    adopciones = query.all()

   
    if not adopciones:
        return jsonify({
            "mensaje": "No hay animales disponibles para adopción en este momento.",
            "data": []  
        }), 200

    resultado = []
    for adopcion in adopciones:
        animal = adopcion.animal
        fotos = [f.url for f in animal.fotos]
        resultado.append({
            "id": adopcion.id,
            "nombre": animal.nombre,
            "especie": animal.especie,
            "edad": animal.edad,
            "fotos": fotos,
            "detalle": adopcion.detalle,
            "url_contacto": adopcion.url
        })

    return jsonify({
        "mensaje": "Adopciones encontradas exitosamente.",
        "data": resultado
    }), 200


#* ==============================
#*  ADOPCIONES ENDPOINTS
#* ==============================
#? TODO: mostrar detalle de una adopcion


@adopcion_bp.route('/adopciones/detalle/<int:id>', methods=['GET'])
def detalle_adopcion(id):
    adopcion = Adopcion.query.get_or_404(id)
    animal = adopcion.animal
    fotos = [f.url for f in animal.fotos]

    return jsonify({
        "id": adopcion.id,
        "nombre": animal.nombre,
        "especie": animal.especie,
        "raza": animal.raza,
        "edad": animal.edad,
        "sexo": animal.sexo,
        "color": animal.color,
        "tamanio": animal.tamanio,
        "observaciones": animal.observaciones,
        "detalle": adopcion.detalle,
        "fotos": fotos,
        "fecha_publicacion": adopcion.fecha_publicacion,
        "url_contacto": adopcion.url
    }), 200



#* ==============================
#*  ADOPCIONES ENDPOINTS
#* ==============================
#? TODO:actulizar una adopcion / asignar dueño / dar de baja / dar de alta 
  
@adopcion_bp.route('/adopciones/actualizar/<int:id>', methods=['PUT'])
@rutaProtegida('admin')
def actualizar_adopcion(id):
    try:
        data = request.json
        adopcion = Adopcion.query.get_or_404(id)
        animal = adopcion.animal

        # Si se intenta activar la adopción, validar que el animal no tenga dueño
        if 'disponible' in data and data['disponible'] == True:
            if animal.id_propietario is not None:
                return jsonify({"error": "No se puede activar la adopción porque el animal ya tiene dueño"}), 400
            adopcion.disponible = True

        if 'detalle' in data:
            adopcion.detalle = data['detalle']

        if 'url' in data:
            adopcion.url = data['url']

        if 'disponible' in data and data['disponible'] == False:
            adopcion.disponible = False

        if 'id_propietario' in data:
            nuevo_duenio = Usuario.query.get_or_404(data['id_propietario'])
            animal.id_propietario = nuevo_duenio.id
            animal.activo = True
            # Si se asigna dueño, automáticamente ya no está disponible para adopción
            adopcion.disponible = False

        db.session.commit()

        return jsonify({"mensaje": "Adopción actualizada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar adopción", "detalle": str(e)}), 500




#* ==============================
#*  ADOPCIONES ENDPOINTS
#* ==============================
#? TODO:listar animales disponibles para adopción
  
@adopcion_bp.route('/animales/para-adopcion', methods=['GET'])
@rutaProtegida('admin')
def listar_animales_para_adopcion():
    try:
        # Solo animales sin dueño y sin adopción activa
        animales_sin_duenio_y_sin_adopcion = Animal.query.filter(
            Animal.id_propietario == None,
            Animal.adopcion == None
        ).all()

        if not animales_sin_duenio_y_sin_adopcion:
            return jsonify({
                "mensaje": "No hay nuevos animales sin dueño para publicar en adopción.",
                "data": []
            }), 200

        resultado = []
        for animal in animales_sin_duenio_y_sin_adopcion:
            resultado.append({
                "id": animal.id,
                "nombre": animal.nombre,
                "especie": animal.especie
            })
        
        return jsonify({
            "mensaje": "Animales listos para ser publicados en adopción.",
            "data": resultado
        }), 200

    except Exception as e:
        return jsonify({"error": "Error al listar animales para adopción", "detalle": str(e)}), 500



#* ==============================
#*  ADOPCIONES ENDPOINTS (SOLO ADMIN)
#* ==============================
#? TODO: Mostrar TODAS las adopciones (activas e inactivas) para el admin

@adopcion_bp.route('/adopciones/admin/todas', methods=['GET'])
@rutaProtegida('admin')
def listar_todas_las_adopciones_admin():
    try:
        
        adopciones = Adopcion.query.order_by(Adopcion.id.desc()).all()

        if not adopciones:
            return jsonify({"mensaje": "No hay ninguna adopción registrada en el sistema."}), 200

        resultado = []
        for adopcion in adopciones:
            animal = adopcion.animal
            
            fotos = [f.url for f in animal.fotos] if animal.fotos else []

            
            resultado.append({
                # Datos de la adopción
                "id_adopcion": adopcion.id,
                "disponible": adopcion.disponible, 
                "detalle_adopcion": adopcion.detalle,
                "url_contacto": adopcion.url,
                "fecha_publicacion": adopcion.fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S'), 

                # Datos del animal asociado
                "id_animal": animal.id,
                "nombre_animal": animal.nombre,
                "especie": animal.especie,
                "edad": animal.edad,
                "sexo": animal.sexo,
                "fotos": fotos
            })
        
        return jsonify({
            "mensaje": "Listado completo de adopciones para gestión.",
            "data": resultado
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Error al listar todas las adopciones", "detalle": str(e)}), 500