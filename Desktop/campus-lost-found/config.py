import os

class Config:
    SECRET_KEY = 'secret123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///campus.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/static/uploads'