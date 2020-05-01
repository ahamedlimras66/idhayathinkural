from db import db
from flask_login import UserMixin

class adminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(80))

class commandBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40),nullable=True)
    command = db.Column(db.String(1000),nullable=False)
    replay = db.Column(db.String(1000),nullable=True)

class event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(40),nullable=False)
    dateTime = db.Column(db.DateTime,nullable=False)

class donateDetails(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(40),nullable=False)
    phone = db.Column(db.Integer,nullable=False)
    things = db.Column(db.String(40),nullable=False)
    mydate = db.Column(db.Date,nullable=False)

class requirementDetial(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(40),nullable=False)
    address = db.Column(db.String,nullable=False)
    requirement = db.Column(db.String(40))
    strength = db.Column(db.String(40),nullable=False)
    mydate = db.Column(db.Date,nullable=False)
    url = db.Column(db.String(40))

