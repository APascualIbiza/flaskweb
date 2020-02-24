# from flask import Flask
from flask_mysqldb import MySQL
from main import app

# init MYSQL
mysql = MySQL(app)


def fetchAllHealthcheck():

    # create cursor
    cur = mysql.connection.cursor()

    # get healthcheck
    cur.execute("SELECT * FROM healthcheck")
    checks = cur.fetchall()
    cur.close()

    return checks


def fetchAllStatus():

    # create cursor
    cur = mysql.connection.cursor()

    # get connections data
    cur.execute("SELECT * FROM app_status WHERE VARIABLE_NAME IN ('CONNECTIONS', 'ACCESS_DENIED_ERRORS', 'TABLE_OPEN_CACHE_MISSES', 'LAST_QUERY_COST')")
    rows = cur.fetchall()
    cur.close()

    return rows


def fetchAllActivities():

    # create cursor
    cur = mysql.connection.cursor()

    # get user activities
    cur.execute("SELECT * FROM app_activity ORDER BY activity_id DESC")
    activities = cur.fetchall()
    cur.close()

    return activities


def fetchAllAUsersActivities():

    # create cursor
    cur = mysql.connection.cursor()

    # get user activities
    cur.execute("SELECT app_users.uid, displayname FROM app_users")
    users = cur.fetchall()
    cur.close()

    return users


def fetchAllUsersConnections():

    # create cursor
    cur = mysql.connection.cursor()

    # get user conections
    cur.execute("SELECT app_users.uid, displayname, name, last_activity, last_check FROM app_users LEFT JOIN app_authtoken ON app_users.uid = app_authtoken.uid")

    conns = cur.fetchall()
    cur.close()

    return conns


def fetchActivity(id):

    # create cursor
    cur = mysql.connection.cursor()

    # get user activities
    cur.execute("SELECT * FROM app_activity WHERE activity_id = %s", [id])
    activity = cur.fetchone()
    cur.close()

    return activity


def fetchUserName(id):

    # create cursor
    cur = mysql.connection.cursor()

    # get username
    cur.execute("SELECT * FROM app_users WHERE uid = %s", [id])
    user = cur.fetchone()
    cur.close()

    return user


def fetchAllUserActivities(id):

    # create cursor
    cur = mysql.connection.cursor()

    # get user activities
    cur.execute("SELECT timestampa, file FROM app_activity WHERE user = %s", [id])
    activities = cur.fetchall()
    cur.close()

    return activities


def insertWebappUser(name, email, username, password):

    # Create cursor
    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO webapp_users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

    # commit to DB
    mysql.connection.commit()

    # close connection
    cur.close()


def fetchWebappUser(username):

    # Create cursor
    cur = mysql.connection.cursor()

    # Get user by username
    cur.execute("SELECT * FROM webapp_users WHERE username = %s", [username])
    data = cur.fetchone()

    cur.close()

    return data


def fetchallActivities():

    # create cursor
    cur = mysql.connection.cursor()

    # get user activity
    cur.execute("SELECT * FROM app_activity")
    allusers = cur.fetchall()
    cur.close()

    return allusers
