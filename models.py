import sqlite3 as sql
from flask import session
from passlib.hash import sha256_crypt


def email_ver()

def insertUser(request):
    con = sql.connect("database.db")
    username1 = request.form['uname1']
    password1 = request.form['psw1']
    #encrypt the password
    password = sha256_crypt.encrypt(password)
    mobile = request.form['phone1']
    sqlQuery = "select username from users where (username ='" + username + "')"
    cursor = con.cursor()
    cursor.execute(sqlQuery)
    row = cursor.fetchone()
    if row:
        con.close()
        return username + " has already been registered."
    else:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username,password,age,gender, interest) VALUES (?,?,?,?,?)", (username,password,age,gender,interest))
        con.commit()
        con.close()
        return username + " has been registered successfully."

def retrieveUsers(user):
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute("SELECT * FROM users where user="+user+';')
	users = cur.fetchall()
	con.close()
	return users
	
	
def authenticate(request):
    con = sql.connect("database.db")
    username = request.form['username']
    password = request.form['password']
    sqlQuery = "select password from users where username = '%s'"%username
    cursor = con.cursor()
    print "sqlQuery= "+ sqlQuery
    cursor.execute(sqlQuery)
    row = cursor.fetchone()
    status = False
    if row:
        status = sha256_crypt.verify(password, row[0])
        print "password=",row[0]," status=",status
        if status:
           msg = username + " has logged in Successfully."
           session['username'] = username
    else:
        msg = username + " has failed to login."

    return status