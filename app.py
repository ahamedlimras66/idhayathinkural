import os
from models.schema import *
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__,static_folder='static')
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_first_request
def create_table():
    db.create_all()
    if adminUser.query.filter_by(username="root").first() is None:
        adminID = adminUser(username="root", password="root")
        db.session.add(adminID)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
	return adminUser.query.get(int(user_id))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(ModelView(commandBox,db.session))
admin.add_view(ModelView(adminUser,db.session))
admin.add_view(ModelView(event,db.session))
@app.route('/sitemap.xml')
def static_sitemap():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/')
def home():
    cmds = commandBox.query.all()
    events = event.query.first()
    events = str(events.dateTime)
    return render_template('index.html',
                            cmds=cmds,
                            month=events[5:7],
                            date=events[8:10],
                            year=events[0:4],
                            time=events[10:])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gal')
def gal():
    return render_template('gal.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit', methods=['POST'])
def  submit():
    name = request.form['name']
    idea =  request.form['command']
    cmd = commandBox(name=name,command=idea)
    db.session.add(cmd)
    db.session.commit()
    return redirect('/')

@app.route('/login')
def login():
    return render_template('admin.html')

@app.route('/login_check', methods=['POST', 'GET'])
def loginCheck():
    userName = request.form['username']
    password = request.form['password']
    user = adminUser.query.filter_by(username=userName).first()
    if user:
        if user.password == password:
            login_user(user, remember=False)
            return redirect('/admin')
    return render_template('admin.html', name = "invalid login")

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(debug=True)