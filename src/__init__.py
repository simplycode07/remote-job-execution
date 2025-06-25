from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from celery import Celery


basedir = path.abspath(path.dirname(__file__))

db_name = "database.db"
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite://{path.join(basedir, db_name)}"

app.config["CELERY_BROKER_URL"] = 'redis://localhost:6379/0'
app.config["CELERY_RESULT_BACKEND"] = 'redis://localhost:6379/0'
db = SQLAlchemy(app)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def start():
    global app, db

    from .views import view_routes, initialize_login
    app.register_blueprint(view_routes)

    with app.app_context():
        if not path.exists(db_name):
            db.create_all()

    initialize_login(app)

    return app


