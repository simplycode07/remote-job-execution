from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

from src.job_executor import JobExecutor

basedir = path.abspath(path.dirname(__file__))

db_name = "database.db"
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite://{path.join(basedir, db_name)}"

db = SQLAlchemy(app)

executor = JobExecutor

def start():
    global app, db

    from .views import view_routes, initialize_login
    app.register_blueprint(view_routes)

    with app.app_context():
        if not path.exists(db_name):
            db.create_all()

    initialize_login(app)

    return app


