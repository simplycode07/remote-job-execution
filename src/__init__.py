from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

basedir = path.abspath(path.dirname(__file__))

db_name = "database.db"
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}"

db = SQLAlchemy(app)

def start():
    global app, db

    from .views import view_routes, initialize_login

    if not app.blueprints.get("views"):
        app.register_blueprint(view_routes)

    with app.app_context():
        if not path.exists(db_name):
            db.create_all()

    initialize_login(app)

    return app


