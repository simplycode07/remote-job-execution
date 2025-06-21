from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db_name = "database.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neondb_owner:npg_zpTOm80RFfnG@ep-weathered-cherry-a5ags46k-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

def start():
    global app, db

    from .views import view_routes, initialize_login
    app.register_blueprint(view_routes)

    with app.app_context():
        if not path.exists(db_name):
            db.create_all()

    initialize_login(app)

    return app


