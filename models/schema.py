from db import db
from flask_login import UserMixin

class adminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))

class commandBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40),nullable=True)
    command = db.Column(db.String(1000),nullable=False)
    replay = db.Column(db.String(1000),nullable=True)