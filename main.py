from flask import Flask
# from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.debug = True
#app.secret_key = 'secret123'
app.secret_key = os.environ.get('SECRET_KEY')

# Config MySQL
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = 'appBD'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

import routes

if __name__ == '__main__':
    app.run()
