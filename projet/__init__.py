import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_modals import Modal
from flask_mail import Mail
from projet.config import Config
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate(db)
login_manager = LoginManager()
ckeditor = CKEditor()
modal = Modal()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
mail = Mail()
admin = Admin()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    from projet.adminbp.routes import MyAdminIndexView

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    modal.init_app(app)
    mail.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexView())
    migrate.init_app(app, db)

    from projet.models import User
    
    #admin.add_view(ModelView(User, db.session, name="Utilisateurs", endpoint="user_admin"))
    
    from projet.main.routes import main
    from projet.users.routes import users
    from projet.recettes.routes import recettes
    from projet.plats.routes import plats_bp
    from projet.errors.handlers import errors
    from projet.adminbp.routes import adminbp

    app.register_blueprint(adminbp)
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(recettes)
    app.register_blueprint(plats_bp)
    app.register_blueprint(errors)
    return app
app = create_app()  # Crée l'application Flask
