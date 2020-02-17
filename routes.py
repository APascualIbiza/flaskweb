from flask import Flask, render_template, flash, redirect , url_for , session , request, logging
from wtforms import Form, StringField , TextAreaField ,PasswordField , validators
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime
import json

from main import app
import db

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def chart():

    labels=[]
    values=[]
    checks=db.fetchAllHealthcheck()
    rows=db.fetchAllStatus()
    for row in rows:
        labels.append(row['VARIABLE_NAME'])
        values.append(row['VARIABLE_VALUE'])
    print(labels, values)

    return render_template('about.html', checks=checks, labels=json.dumps(labels), values=json.dumps(values))
    
@app.route('/activities')
def activities():

    activities=db.fetchAllActivities()
    
    if activities != None:
        return render_template('activities.html', activities=activities)
    else:
        msg = 'No se han encontrado actividades.'
        return render_template('activities.html', msg=msg)

@app.route('/users')
def users():

    users = db.fetchAllAUsersActivities()
    conns = db.fetchAllUsersConnections()

    if conns != None:
        return render_template('users.html', users=users, conns=conns)
    else:
        msg = 'No se ha conectado.'
        return render_template('users.html', users=users, msg=msg)
    

@app.route('/activity/<string:id>/')
def activity(id):
    
    activity = db.fetchActivity(id)

    return render_template('activity.html', activity=activity)


@app.route('/user/<string:id>/')
def user(id):

    user = db.fetchUserName(id)
    activities = db.fetchAllUserActivities(id)
    
    if activities != None:
        return render_template('user.html', user=user, activities=activities)
    else:
        msg = 'No se han encontrado actividades.'
        return render_template('user.html', user=user, msg=msg)


class RegisterForm(Form):
    name = StringField('Nombre de la cuenta',[validators.Length(min=1,max=50)])
    username = StringField('Nombre del usuario',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=4,max=25)])
    password = PasswordField('Password', [ validators.DataRequired (),validators.EqualTo('confirm',message ='Los passwords no coinciden.')])
    confirm = PasswordField('Repita el password')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        db.insertWebappUser(name, email, username, password)

        flash("Ud. está ahora registrado, puede autenticarse." , 'success')

        redirect(url_for('login'))
    return render_template('register.html',form=form)

# user login
@app.route('/login',methods =['GET','POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        

        data = db.fetchWebappUser(username)

        if data != None:
        # Get Stored hash
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate,password):
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash('Ud. está ahora autenticado.','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'El login ha fallado.'
                return render_template('login.html', error=error)

        else:
            error = 'El login ha fallado.'
            return render_template('login.html', error=error)

    return render_template('login.html')

#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('No autorizado, ppor favor, autentíquese.','danger')
            return redirect(url_for('login'))
    return wrap


#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Ya no está autenticado.','success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    allusers = db.fetchallActivities()

    if allusers != None:
        return render_template('dashboard.html',articles=allusers)
    else:
        msg = 'No se han encontrado actividades.'
        return render_template('dashboard.html',msg=msg)
 

@app.template_filter('ts')
def ts_filter(ts):
    if ts is None:
      return ""
    return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
