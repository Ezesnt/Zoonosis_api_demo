from datetime import datetime, timedelta
from venv import logger
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.models.models import Animal, HistorialLibreta, Usuario
from app.routes.auth_routes import rutaProtegida
from app.schemas import animal_schema , foto_schema
from dbConfig import db
from app.utils.cloudinary_service import CloudinaryService
from app.schemas.animal_schema import AnimalSchema
from werkzeug.exceptions import NotFound


animal_bp = Blueprint('animal_bp', __name__)
animal_schema_instance = AnimalSchema()

#* ==================================================================
#! (ANIMALES)
#* ==================================================================


#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: crear animal 

@animal_bp.route('/animales/crear', methods=['POST'])
@rutaProtegida("ciudadano")  
def crear_animal():
    try:
      
        current_user = request.current_user
        current_user_id = current_user['id']
        
        print(f" Usuario autenticado: ID {current_user_id}")  
        
        schema = animal_schema.AnimalSchema()


        
        data = request.json
        errors = schema.validate(data)
        if errors:
            print(f"❌ Errores de validación: {errors}")
            return jsonify({"error": "Datos inválidos", "detalles": errors}), 400

    
        propietario = Usuario.query.get(current_user_id)
        if not propietario:
            print(f"❌ Usuario no encontrado en DB: ID {current_user_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404

        
        nuevo_animal = Animal(
            nombre=data['nombre'],
            especie=data['especie'],
            raza=data.get('raza'),
            edad=data.get('edad'),
            sexo=data.get('sexo'),
            color=data.get('color'),
            tamanio=data.get('tamanio'),
            esta_castrado=data.get('esta_castrado', False),
            observaciones=data.get('observaciones'),
            estado='no patentado',
            id_propietario=current_user_id,  
            fecha_registro=datetime.utcnow()
        )

        db.session.add(nuevo_animal)
        db.session.commit()

        print(f" Animal creado: ID {nuevo_animal.id}")  

        return jsonify({
            "mensaje": "Animal creado exitosamente",
            "animal": animal_schema.AnimalSchema().dump(nuevo_animal)
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f" Error al crear animal: {str(e)}")
        return jsonify({"error": "Error al crear el animal", "detalle": str(e)}), 500
    
    

#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: listar animales     

@animal_bp.route('/animales', methods=['GET'])
@rutaProtegida()
def listar_animales():
    try:
        current_user = request.current_user
        user_id = current_user['id']
        user_role = current_user['categoria']
        
        
        query = Animal.query
        
       
        if not (user_role == 'admin' and request.args.get('incluir_inactivos') == 'true'):
            query = query.filter_by(activo=True)
        
        
        if user_role != 'admin':
            query = query.filter_by(id_propietario=user_id)
        
        
        filtros_disponibles = {
            'especie': request.args.get('especie'),
            'nombre': request.args.get('nombre'),
            'numero_patente': request.args.get('patente'),
            'estado': request.args.get('estado'),
            'tamanio': request.args.get('tamanio'),
            'propietario_id': request.args.get('propietario_id')  
        }
        
        
        for campo, valor in filtros_disponibles.items():
            if valor:
                if campo == 'propietario_id' and user_role == 'admin':
                    query = query.filter_by(id_propietario=valor)
                elif campo != 'propietario_id':
                    query = query.filter(getattr(Animal, campo).ilike(f'%{valor}%'))
        
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        animales_paginados = query.paginate(page=page, per_page=per_page, error_out=False)
        
       
        resultado = animal_schema.AnimalSchema(many=True).dump(animales_paginados.items)
        
        return jsonify({
            "mensaje": "Búsqueda exitosa",
            "animales": resultado,
            "total": animales_paginados.total,
            "paginas": animales_paginados.pages,
            "pagina_actual": page,
            "filtros_aplicados": {k: v for k, v in filtros_disponibles.items() if v},
            "incluye_inactivos": user_role == 'admin' and request.args.get('incluir_inactivos') == 'true'
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Error en la búsqueda", "detalle": str(e)}), 500
 



#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: actualizar animales   

@animal_bp.route('/animales/<int:id>', methods=['PUT'])
@rutaProtegida()  
def actualizar_animal(id):
    try:
        current_user = request.current_user
        user_id = current_user['id']
        user_role = current_user['categoria']  

       
        animal = Animal.query.get_or_404(id)


        if user_role != 'admin' and animal.id_propietario != user_id:
            return jsonify({
                'error': 'No tienes permisos. Solo el dueño o un administrador puede editar este animal'
            }), 403

        
        data = animal_schema.AnimalCreateSchema().load(request.get_json(), partial=True)

        
        campos_actualizables = [
            'nombre', 'especie', 'raza', 'edad', 'sexo',
            'color', 'tamanio', 'esta_castrado', 'observaciones'
        ]
        for campo in campos_actualizables:
            if campo in data:
                setattr(animal, campo, data[campo])

        db.session.commit()

        return jsonify({
            'mensaje': 'Animal actualizado con éxito',
            'animal': animal_schema.AnimalSchema().dump(animal)
        }), 200

    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'detalles': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'detalle': str(e)}), 500
    
    
#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: dar de baja un animal 

@animal_bp.route('/animales/<int:id>/deshabilitar', methods=['PUT'])  
@rutaProtegida('admin')
def deshabilitar_animal(id):
    current_user = request.current_user
    animal = Animal.query.get_or_404(id)

    
    if current_user['categoria'] != 'admin' and animal.id_propietario != current_user['id']:
        return jsonify({'error': 'No autorizado'}), 403

    
    animal.activo = False
    animal.motivo_baja = request.json.get('motivo', 'Fallecido')  
    animal.fecha_baja = datetime.utcnow()  

    db.session.commit()

    return jsonify({
        'mensaje': 'Animal deshabilitado exitosamente',
        'motivo': animal.motivo_baja
    }), 200


#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: dar de alta un animal 

@animal_bp.route('/animales/<int:id>/activar', methods=['PUT'])
@rutaProtegida('admin')
def activar_animal(id):
    current_user = request.current_user
    animal = Animal.query.get_or_404(id)

    
    if current_user['categoria'] != 'admin' and animal.id_propietario != current_user['id']:
        return jsonify({'error': 'No autorizado'}), 403

    
    animal.activo = True
    animal.motivo_baja = None
    animal.fecha_baja = None

    db.session.commit()

    return jsonify({
        'mensaje': 'Animal reactivado exitosamente',
        'animal': animal_schema.AnimalSchema().dump(animal)
    }), 200
    

#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: patentar animal 1 año 
       
@animal_bp.route('/animales/<int:id>/patentar', methods=['POST'])
@rutaProtegida('admin')  
def patentar_animal(id):
    try:
        data = animal_schema.AnimalPatentarSchema().load(request.get_json() or {})
        animal = Animal.query.get_or_404(id)
        
        if animal.estado == 'aprobado':
            raise ValidationError("Este animal ya está patentado")

        # Generación de número de patente 
        current_year = datetime.now().year
        ultimo_numero = db.session.query(
            db.func.max(
                db.cast(
                    db.func.right(Animal.numero_patente, 4),
                    db.Integer
                )
            )
        ).filter(
            Animal.numero_patente.like(f'PAT-{current_year}-%')
        ).scalar() or 0

        nuevo_numero = f"PAT-{current_year}-{(ultimo_numero + 1):04d}"

        # Cálculo  de fechas
        fecha_emision = datetime.utcnow()
        
        if 'fecha_vencimiento' in data:
            fecha_vencimiento = datetime.combine(data['fecha_vencimiento'], datetime.min.time())
            if fecha_vencimiento <= fecha_emision:
                raise ValidationError("La fecha de vencimiento debe ser futura")
            if fecha_vencimiento > fecha_emision + timedelta(days=366):
                raise ValidationError("La vigencia máxima es de 1 año")
        else:
            try:
                fecha_vencimiento = fecha_emision.replace(year=fecha_emision.year + 1)
            except ValueError:
                fecha_vencimiento = fecha_emision + timedelta(days=365)

        # Actualización 
        db.session.query(Animal).filter_by(id=id).update({
            'estado': 'patentado',
            'numero_patente': nuevo_numero,
            'fecha_emision_patente': fecha_emision,
            'fecha_vencimiento_patente': fecha_vencimiento
        })
        db.session.commit()

        return jsonify(animal_schema.AnimalResponseSchema().dump(animal)), 200

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error patentando animal {id}: {str(e)}")
        return jsonify({"error": "Error interno"}), 500
   
    
#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: buscar por patente     

@animal_bp.route('/animales/patente/<string:nro>', methods=['GET'])
@rutaProtegida()
def buscar_por_patente(nro):
    try:
        animal = Animal.query.filter_by(numero_patente=nro).first_or_404()
        
        
        current_user = request.current_user
        if current_user['categoria'] != 'admin' and animal.id_propietario != current_user['id']:
            return jsonify({"error": "No autorizado"}), 403
            
        return jsonify(animal_schema.AnimalSchema().dump(animal)), 200
    except Exception as e:
        logger.error(f"Error buscando patente {nro}: {str(e)}")
        return jsonify({"error": "Error en la búsqueda"}), 500
  
    
#* ==============================
#*  ANIMAL ENDPOINTS
#* ==============================
#? TODO: filtrar solamente inactivos   

@animal_bp.route('/animales/inactivos', methods=['GET'])
@rutaProtegida('admin')
def listar_inactivos():
    try:
        query = Animal.query.filter_by(activo=False)
        
        
        if request.args.get('propietario_id'):
            query = query.filter_by(id_propietario=request.args.get('propietario_id'))
        
        animales = query.all()
        return jsonify({
            "inactivos": animal_schema.AnimalSchema(many=True).dump(animales)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
    
    
#* ==================================================================
#! ( Libreta Digital del Animal)
#* ================================================================== 





#* ==============================
#*  Libreta ENDPOINTS
#* ==============================
#? TODO: crear libreta 

@animal_bp.route('/animales/<int:id>/libreta', methods=['POST'])
@rutaProtegida('admin')  #
def agregar_entrada_libreta(id):
    try:
        current_user = request.current_user
        
        Animal.query.get_or_404(id)

        
        schema = animal_schema.LibretaCreateSchema()
        data = schema.load(request.get_json())

        
        nueva_entrada = HistorialLibreta(
            id_animal=id,
            tipo=data['tipo'],
            descripcion=data.get('descripcion'),
            fecha=data['fecha'],
            registrado_por=current_user['id']
        )

        db.session.add(nueva_entrada)
        db.session.commit()

        return animal_schema.LibretaSchema().dump(nueva_entrada), 201

    except ValidationError as err:
        return {"error": err.messages}, 400
    

#* ==============================
#*  Libreta ENDPOINTS
#* ==============================
#? TODO: mostrar la libreta de 1 animal
    
@animal_bp.route('/animales/<int:id>/libreta', methods=['GET'])
def obtener_historial_animal(id):
    entradas = (
        HistorialLibreta.query
        .filter_by(id_animal=id)
        .options(db.joinedload(HistorialLibreta.usuario))  
        .order_by(HistorialLibreta.fecha.desc())
        .all()
    )
    return animal_schema.LibretaSchema(many=True).dump(entradas), 200


#* ==============================
#*  Libreta ENDPOINTS
#* ==============================
#? TODO:editar entradas de la libreta

@animal_bp.route('/animales/libreta/<int:id>', methods=['PUT'])
@rutaProtegida('admin')
def editar_entrada_libreta(id):
    try:
        entrada = HistorialLibreta.query.get_or_404(id)

        
        schema = animal_schema.LibretaUpdateSchema()
        data = schema.load(request.get_json())

        
        if 'tipo' in data:
            entrada.tipo = data['tipo']
        if 'descripcion' in data:
            entrada.descripcion = data['descripcion']
        if 'fecha' in data:
            entrada.fecha = data['fecha']

        db.session.commit()

        return jsonify({
            'mensaje': 'Entrada actualizada exitosamente',
            'entrada': animal_schema.LibretaSchema().dump(entrada)
        })

    except ValidationError as err:
        return {"error": err.messages}, 400

    except Exception as e:
        db.session.rollback()
        raise e




#* ==============================
#*  animales ENDPOINTS
#* ==============================
#? TODO:subir imagen 

@animal_bp.route('/animales/<int:id>/fotos', methods=['POST'])
def subir_foto(id):
    if 'foto' not in request.files:
        return jsonify({"error": "No se proporcionó archivo"}), 400
    
    try:
        foto = CloudinaryService.upload_animal_photo(
            request.files['foto'],
            id
        )
        return jsonify(foto_schema.dump(foto)), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
 
 
#* ==============================
#*  ANIMALES ENDPOINTS
#* ==============================
#? TODO:el admin puede registrar un animales con imagenes y sin dueño ideal para publicar adopciones 
   
@animal_bp.route('/admin/animales/crear', methods=['POST'])
@rutaProtegida("admin")
def crear_animal_admin():
    try:
        schema = animal_schema.AnimalSchema()  
        data = request.form
        file = request.files.get('foto')
        
        errors = schema.validate(data)
        if errors:
            return jsonify({"error": "Datos inválidos", "detalles": errors}), 400

        esta_castrado = (data.get('esta_castrado', 'false').lower() == 'true')
        edad = int(data['edad']) if data.get('edad') else None

        nuevo_animal = Animal(
            nombre=data['nombre'],
            especie=data['especie'],
            raza=data.get('raza'),
            edad=edad,
            sexo=data.get('sexo'),
            color=data.get('color'),
            tamanio=data.get('tamanio'),
            esta_castrado=esta_castrado,
            observaciones=data.get('observaciones'),
            estado='no patentado',
            id_propietario=None,
            fecha_registro=datetime.utcnow()
        )

        db.session.add(nuevo_animal)
        db.session.commit()

        foto_url = None
        if file:
            foto = CloudinaryService.upload_animal_photo(file, nuevo_animal.id)
            foto_url = foto.url

        return jsonify({
            "mensaje": "Animal en adopción creado",
            "animal": animal_schema_instance.dump(nuevo_animal),
            "foto_url": foto_url
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



 
@animal_bp.route('/animales/<int:animal_id>', methods=['GET'])
@rutaProtegida('admin') 
def obtener_detalle_animal(animal_id):
   
    try:
        animal = Animal.query.get_or_404(animal_id)

        resultado = animal_schema.AnimalSchema().dump(animal)

        return jsonify({
            "mensaje": "Detalle del animal obtenido con éxito.",
            "animal": resultado
        }), 200

    except NotFound:
        return jsonify({
            "error": "Recurso no encontrado",
            "mensaje": f"No se encontró ningún animal con el ID {animal_id}."
        }), 404
        
    except Exception as e:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(e)
        }), 500