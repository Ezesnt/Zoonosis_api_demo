from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from app.config import Config
from dbConfig import db
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.models.models import Usuario , Animal,HistorialLibreta,Adopcion, Denuncia,ArchivoDenuncia,Turno,ResetPasswordToken

ma = Marshmallow()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    print("🧪 CONFIG:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    Config.init_cloudinary()  
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    # Importar y registrar blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.usuario_routes import usuario_bp
    from app.routes.turno_routes import turno_bp
    from app.routes.animal_routes import animal_bp
    from app.routes.adopcion_routes import adopcion_bp
    from app.routes.denuncia_routes import denuncia_bp
    from app.routes.estadisticas_routes import estadisticas_bp
    from app.routes.noticias_routes import noticia_bp
    
    
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(usuario_bp, url_prefix='/')
    app.register_blueprint(turno_bp, url_prefix='/')
    app.register_blueprint(animal_bp, url_prefix='/')
    app.register_blueprint(adopcion_bp, url_prefix='/')
    app.register_blueprint(denuncia_bp, url_prefix='/')
    app.register_blueprint(estadisticas_bp, url_prefix='/')
    app.register_blueprint(noticia_bp, url_prefix='/')


    #with app.app_context():
        #db.create_all()

    return app