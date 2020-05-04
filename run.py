from app import app
from db import db
from models.schema import *
from werkzeug.security import check_password_hash, generate_password_hash


db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
    if adminUser.query.filter_by(username="root").first() is None:
        adminID = adminUser(username="root", password=generate_password_hash("root",method='sha256'))
        db.session.add(adminID)
        db.session.commit()