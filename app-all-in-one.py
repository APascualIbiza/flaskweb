from flask import Flask,render_template, flash, redirect , url_for , session ,request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField , TextAreaField ,PasswordField , validators
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime
import json

app = Flask(__name__)
app.debug = True
app.secret_key='secret123'

#Config MySQL
app.config['MYSQL_HOST'] = '192.168.0.20'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abastos'
app.config['MYSQL_DB'] = 'appBD'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def chart():
        
    legend = "Conexiones"
    
    #create cursor
    cur = mysql.connection.cursor()

    #get healthcheck
    healthcheck = cur.execute("SELECT * FROM healthcheck")
    checks = cur.fetchall()

    #get connections data
    result = cur.execute("SELECT * FROM app_status WHERE VARIABLE_NAME IN ('CONNECTIONS', 'ACCESS_DENIED_ERRORS', 'TABLE_OPEN_CACHE_MISSES', 'LAST_QUERY_COST')")
    rows = cur.fetchall()
    cur.close()

    labels=[]
    values=[]
    for row in rows:
        labels.append(row['VARIABLE_NAME'])
        values.append(row['VARIABLE_VALUE'])
    print(labels, values)

    return render_template('about.html', checks=checks, labels=json.dumps(labels), values=json.dumps(values))
    
@app.route('/activities')
def activities():

        #create cursor
        cur = mysql.connection.cursor()

        #get user activities
        result = cur.execute("SELECT * FROM app_activity ORDER BY activity_id DESC")

        if result > 0:
            activities = cur.fetchall()
            cur.close()
            return render_template('activities.html',activities=activities)
        else:
            msg = 'No se han encontrado actividades.'
            cur.close()
            return render_template('activities.html',msg=msg)


@app.route('/users')
def users():

        #create cursor
        cur = mysql.connection.cursor()

        #get user activities
        result = cur.execute("SELECT app_users.uid, displayname FROM app_users")
        users = cur.fetchall()

        #get user conections
        connections = cur.execute("SELECT app_users.uid, displayname, name, last_activity, last_check FROM app_users LEFT JOIN app_authtoken ON app_users.uid = app_authtoken.uid")

        if connections > 0:
            conns = cur.fetchall()
            cur.close()
            return render_template('users.html',users=users, conns=conns)
        else:
            msg = 'No se ha conectado.'
            cur.close()
            return render_template('users.html',users=users, msg=msg)
    

@app.route('/activity/<string:id>/')
def activity(id):
    #create cursor
    cur = mysql.connection.cursor()

    #get user activities
    result = cur.execute("SELECT * FROM app_activity WHERE activity_id = %s",[id])

    activity = cur.fetchone()

    return render_template('activity.html',activity=activity)


@app.route('/user/<string:id>/')
def user(id):
    #create cursor
    cur = mysql.connection.cursor()

    #get user activities
    result = cur.execute("SELECT * FROM app_users WHERE uid = %s",[id])
    user = cur.fetchone()
    
    result2 = cur.execute("SELECT timestampa ,file FROM app_activity WHERE user = %s", [id])

    if result2 > 0:
        activities = cur.fetchall()
        return render_template('user.html',user=user ,activities=activities)
    else:
        msg = 'No se han encontrado actividades.'
        return render_template('user.html',user=user ,msg=msg)



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

        # Create crusor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO webapp_users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name,email,username,password))

        # commit to DB
        mysql.connection.commit()
        #close connection
        cur.close()

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

        # Create cursor

        cur = mysql.connection.cursor()

        #Get user by username

        result = cur.execute("SELECT * FROM webapp_users WHERE username = %s" ,[username])

        if result > 0:
        # Get Stored hash
            data = cur.fetchone()
            password = data['password']
            cur.close()
            # Compare Passwords
            if sha256_crypt.verify(password_candidate,password):
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash('Ud. está ahora autenticado.','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Nombre de usuario no encontrado.'
                return render_template('login.html',error=error)

        else:
            error = 'Nombre de usuario no encontrado.'
            return render_template('login.html',error=error)

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

    #create cursor
    cur = mysql.connection.cursor()

    #get user activity
    result = cur.execute("SELECT * FROM app_activity")

    allusers = cur.fetchall()
    cur.close()

    if result > 0:
        return render_template('dashboard.html',articles=allusers)
    else:
        msg = 'No se han encontrado actividades.'
        return render_template('dashboard.html',msg=msg)
 

@app.template_filter('ts')
def ts_filter(ts):
    if ts is None:
      return ""
    return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')

if __name__ =='__main__':
    app.run()