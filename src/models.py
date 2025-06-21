from . import db
from flask_login import UserMixin
from datetime import datetime
import enum

class UserType(enum.Enum):
    DOCTOR = 0
    PATIENT = 1
    ADMIN = 2

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # explicit table name (optional but recommended)

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    first_name = db.Column(db.String(300), nullable=False)
    last_name = db.Column(db.String(300), nullable=False)
    
    country_code = db.Column(db.String(5), nullable=False)  # e.g. "+91"
    mobile = db.Column(db.String(10), nullable=False)

    user_type = db.Column(db.Enum(UserType, name="user_type_enum"), nullable=False)  
    # name="user_type_enum" creates a Postgres enum type named user_type_enum
