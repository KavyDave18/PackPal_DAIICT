import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv
import pymysql

# Use PyMySQL instead of MySQLdb
pymysql.install_as_MySQLdb()

# Add the current directory to the path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from models import db
from routes.auth import auth_bp
from routes.checklist import checklist_bp
from routes.members import members_bp
from routes.alerts import alerts_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://root:@localhost/packpal_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(checklist_bp, url_prefix='/api/checklists')
    app.register_blueprint(members_bp, url_prefix='/api/members')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {
            "message": "Welcome to PackPal API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "checklists": "/api/checklists",
                "members": "/api/members",
                "alerts": "/api/alerts"
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True) 