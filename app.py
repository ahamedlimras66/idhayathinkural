import os
import datetime
import json
from models.schema import *
from flask_mail import Mail,Message
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, url_for, redirect, send_from_directory, send_file, jsonify, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


#setup
app = Flask(__name__,static_folder='static')
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "file/req"
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'limraslimahamed@gmail.com'
app.config['MAIL_PASSWORD'] = 'Ahamedlimras99.'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

#creat database 
@app.before_first_request
def create_table():
    db.create_all()
    if adminUser.query.filter_by(username="root").first() is None:
        adminID = adminUser(username="root", password=generate_password_hash("root",method='sha256'),mail="limraslim@gmail.com")
        db.session.add(adminID)
        db.session.commit()

#remember option
@login_manager.user_loader
def load_user(user_id):
	return adminUser.query.get(int(user_id))

#app admin option
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


#sitemap for google site
@app.route('/sitemap.xml')
def static_sitemap():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/cmd')
def show_cmd():
    cmds = commandBox.query.all()
    data = {"name":[],
            "command":[],
            "replay":[]}
    for i in cmds:
        data['name'].append(i.name)
        data['command'].append(i.command)
        data['replay'].append(i.replay)
    return jsonify(data)

@app.route('/save_cmd/<jsdata>')
def save_cmd(jsdata):
    data = json.loads(jsdata)
    new_cmd = commandBox(name=data['name'],command=data['cmd'])
    db.session.add(new_cmd)
    db.session.commit()

    return Response(status=200)

#app url
@app.route('/')
def home():
    events = event.query.first()
    cmds = commandBox.query.all()
    if events is not None:
        events = str(events.dateTime)
        return render_template('index.html',
                                cmds=cmds,
                                month=events[5:7],
                                date=events[8:10],
                                year=events[0:4],
                                time=events[10:])
    else:
        return render_template('index.html',cmds=cmds)

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
        return render_template('events.html',
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
    name = request.form['name']
    phoneno = request.form['phoneno']
    address = request.form['address']
    requirement = request.form['requirement']
    strength = request.form['strength']
    file = request.files['myfile']

    mydate = datetime.datetime.strptime(request.form['mydate'], '%Y-%m-%d')
    if name!='' and address!='' and strength!='' and phoneno!='':
        req = requirementDetial(name=name,
                                phone=phoneno,
                                address=address,
                                requirement=requirement,
                                strength=strength,
                                mydate=mydate)
        
        db.session.add(req)
        db.session.commit()
    else:
        error="please enter Requirement corretal"
        return render_template('Requirement.html',error=error)
    if file.filename!='':
        fileformat = file.filename[file.filename.find('.'):]
        if fileformat not in ['.png', '.jpg', '.pdf', '.doc']:
            error="please check file format (.png, .jpg, .pdf, .doc)"
            return render_template('Requirement.html',error = error)
        else:
            filename  = str(req.id)+fileformat
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            req.url = "http://www.idhayathinkural.in/file/"+filename
            db.session.commit()

    return redirect("/sendmail/1/"+str(req.id))
    # return render_template('Requirement.html',info="Thanks for filled")

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
    phone = int(request.form['phoneno'])
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
        return redirect("/sendmail/2/"+str(dd.id))
        # return render_template('Donate.html',info="Thanks for Donate")
    else:
        return render_template('Donate.html',error="please enter details corretal")

@app.route('/sendmail/<type>/<id>')
def send_mail(type,id):
    toSend = adminUser.query.all()
    if type == '1':
        temp = requirementDetial.query.filter_by(id=id).first()
        name=temp.name
        addres=temp.address
        number=temp.phone
        requirement=temp.requirement
        requirement_file=temp.url
        strength=temp.strength
        date=temp.mydate
        template = "reqmail.html"
        for user in toSend:
            msg = Message('Hello', sender = 'idhayathinkuralmail', recipients = [user.mail])
            msg.html = render_template(template,
                                        name=name,
                                        addres=addres,
                                        number=number,
                                        requirement=requirement,
                                        requirement_file=requirement_file,
                                        strength=strength,
                                        date=date,
                                        )
            mail.send(msg)
    else:
        temp = donateDetails.query.filter_by(id=id).first()
        name=temp.name
        number=temp.phone
        option=temp.things
        date=temp.mydate
        template = "donormail.html"
        for user in toSend:
            msg = Message('Hello', sender = 'idhayathinkuralmail', recipients = [user.mail])
            msg.html = render_template(template,
                                        name=name,
                                        number=number,
                                        option=option,
                                        date=date
                                        )
            mail.send(msg)
    return redirect("/")
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