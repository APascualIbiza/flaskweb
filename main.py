from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret123'

#Config MySQL
app.config['MYSQL_HOST'] = '192.168.0.20'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abastos'
app.config['MYSQL_DB'] = 'appBD'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

import routes

if __name__ == '__main__':
    app.run()