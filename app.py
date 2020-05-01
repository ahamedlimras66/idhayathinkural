import os
import datetime
import tempfile
from models.schema import *
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, url_for, redirect, send_from_directory, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__,static_folder='static')
app.secret_key = 'my-secret-key'
app.config['UPLOAD_FOLDER'] = "file/req"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_first_request
def create_table():
    db.create_all()
    if adminUser.query.filter_by(username="root").first() is None:
        adminID = adminUser(username="root", password=generate_password_hash("root",method='sha256'))
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

class UserAdmin(ModelView):
    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password,method='sha256')

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(ModelView(commandBox,db.session))
admin.add_view(UserAdmin(adminUser,db.session))
admin.add_view(ModelView(event,db.session))
admin.add_view(ModelView(donateDetails,db.session))
admin.add_view(ModelView(requirementDetial,db.session))



@app.route('/sitemap.xml')
def static_sitemap():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/')
def home():
    cmds = commandBox.query.all()
    events = event.query.first()
    if events is not None:
        events = str(events.dateTime)
        return render_template('index.html',
                                cmds=cmds,
                                month=events[5:7],
                                date=events[8:10],
                                year=events[0:4],
                                time=events[10:])
    else:
        return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gal')
def gal():
    return render_template('gal.html')

@app.route('/events')
def events():
    cmds = commandBox.query.all()
    events = event.query.first()
    if events is not None:
        events = str(events.dateTime)
        return render_template('index.html',
                                cmds=cmds,
                                month=events[5:7],
                                date=events[8:10],
                                year=events[0:4],
                                time=events[10:])
    else:
        return render_template('events.html',cmds=cmds)

@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/Donate')
def Donate():
    return render_template('Donate.html')

@app.route('/Requirement')
def Requirement():
    return render_template('Requirement.html')

@app.route('/RequirementDetial', methods=['POST'])
def RequirementDetial():
    file = request.files['myfile']
    fileformat = file.filename[file.filename.find('.'):]
    if fileformat in ['.png', '.jpg', '.pdf', '.doc']:
        name = request.form['name']
        address = request.form['address']
        requirement = request.form['requirement']
        strength = request.form['strength']
        mydate = datetime.datetime.strptime(request.form['mydate'], '%Y-%m-%d')
        if name!='' and address!='' and strength!='':
            req = requirementDetial(name=name,
                                    address=address,
                                    requirement=requirement,
                                    strength=strength,
                                    mydate=mydate)
            db.session.add(req)
            db.session.commit()
            filename  = str(req.id)+fileformat
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            req.url = "http://www.idhayathinkural.in/file/"+filename
            db.session.commit()
            return render_template('Requirement.html',info="Thanks for filled")
        else:
            error="please enter Requirement corretal"
    else:
        error="please check file format (.png, .jpg, .pdf, .doc)"
    return render_template('Requirement.html',error=error)

@app.route("/file/<fileName>")
@login_required
def view(fileName):
    print(fileName)
    try:
        return send_file('file/req/'+fileName, attachment_filename="test")
    except:
        pass
    
@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def  submit():
    name = request.form['name']
    idea =  request.form['command']
    cmd = commandBox(name=name,command=idea)
    db.session.add(cmd)
    db.session.commit()
    return redirect('/')

@app.route('/DonateDetails',methods=['POST'])
def DonateDetails():
    name = request.form['name']
    phone = request.form['phoneno']
    things = request.form['things']
    mydate = datetime.datetime.strptime(request.form['mydate'], '%Y-%m-%d')
    if name!='' and phone!='' and things!='title':
        dd = donateDetails(name=name,
                        phone=phone,
                        things=things,
                        mydate=mydate
        )
        db.session.add(dd)
        db.session.commit()
        return render_template('Donate.html',info="Thanks for Donate")
    else:
        return render_template('Donate.html',error="please enter details corretal")

@app.route('/login')
def login():
    return render_template('admin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

@app.route('/login_check', methods=['POST', 'GET'])
def loginCheck():
    userName = request.form['username']
    password = request.form['password']
    user = adminUser.query.filter_by(username=userName).first()
    if user and check_password_hash(user.password, password):
            login_user(user, remember=False)
            return redirect('/admin')
    return render_template('admin.html', name = "invalid login")

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(debug=True)