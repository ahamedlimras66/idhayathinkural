from app import app
from db import db
from models.schema import *

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
    if adminUser.query.filter_by(username="root").first() is None:
        adminID = adminUser(username="root", password="root")
        db.session.add(adminID)
        db.session.commit()