from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask import url_for
from flask import flash, redirect, g
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from random import randint
import sqlite3
import os
from passlib.hash import sha256_crypt
from functools import wraps

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
code1=0
code2=0
email1=""
un = ""
couple={}

val = randint(1000000,999999999999)

app=Flask(__name__)

app.secret_key="some secret"
'''
@app.before_request
def before_request():
	g.username=None
	if 'username' in session:
		g.username = session['username']
'''
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'username' in session:
			return f(*args,**kwargs)
		else:
			flash('unauthorised , please login')
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		return redirect('/home/')
	return render_template("index.html")


@app.route('/signup')
def signup():
	return render_template('signup.html')


@app.route('/everify' ,methods=['POST'])
def everify():
	
	couple["phone1"] = request.form['phone1']
	couple["phone2"] = request.form['phone2']
	couple["us1"] = request.form['uname1']
	couple["us2"] = request.form['uname2']
	
	couple["email1"] = request.form['email1']
	couple["email2"] = request.form['email2']
	email1 = request.form['email1']
	email2 = request.form['email2']
	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	row=None
	cursor.execute("SELECT * FROM users WHERE USERNAME = ? OR USERNAME = ?",(couple['us1'],couple['us2']))
	row = cursor.fetchone()
	if row:
		flash("Username already exists")
		return redirect('/signup')
	cursor.execute("SELECT * FROM users WHERE EMAIL = ? OR EMAIL = ?",(couple['email1'],couple['email2']))
	row= cursor.fetchone()
	if row:
		flash("Email already registered")
		return redirect('/signup')

	couple["psw1"] = request.form['psw1']
	couple["psw2"] = request.form['psw2']
	couple["cpsw1"] = request.form['cpsw1']
	couple["cpsw2"] = request.form['cpsw2']

	if couple["psw1"]!=couple["cpsw1"] or couple["psw2"]!=couple["cpsw2"]:
		flash('Passwords do not match')
		return redirect('/signup')
	couple["age1"]=request.form["age1"]
	couple["age2"]=request.form["age2"]
	
	couple["gender1"]=request.form["gender1"]
	couple["gender2"]=request.form["gender2"]

	couple["fname1"] = request.form['fname1']
	#print(couple["fname1"])
	couple["fname2"] = request.form['fname2']
	couple["lname1"] = request.form['lname1']
	couple["lname2"] = request.form['lname2']
	if couple["email1"] == couple["email2"]:
		flash('Same email entered')
		return redirect('/signup')

	global code1
	code1 = randint(1000000,9999999)
	TEXT1 = "Your verification code is " + str(code1)
	SUBJECT = "Verification Code"
	msg1 = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT1)

	print code1
	global code2
	code2 = randint(1000000,9999999)
	print code2
	TEXT2 = "Your verification code is " + str(code2)
	msg2 = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT2)


	#Create login Server
	server = smtplib.SMTP('smtp.googlemail.com', 587)
	server.starttls()
	server.ehlo()
	server.login("coupledal@gmail.com", "ShubhAksh@123")
	 
	#Send Mail
	user1 = email1
	user2 = email2
	server.sendmail("coupledal@gmail.com",user1, msg1)
	server.sendmail("coupledal@gmail.com",user2, msg2)
	server.quit()
	global val
	val = randint(10000000,99999999999999)
	return redirect(url_for('enter_code',value = val))

@app.route('/enter_code/<value>')
def enter_code(value):
	#print(couple["us1"])
	#print(couple["fname1"])
	return render_template('everify.html',u1=couple["fname1"],u2=couple["fname2"],val =value)


@app.route('/home/')
def home():
	
	if 'username' in session:
		global un
		un = session['username']
		print (un)
		conn = sqlite3.connect('data.db')
		cursor = conn.cursor()
		row=None
		cursor.execute("SELECT * FROM couples WHERE FIRST = ?",[un])
		row = cursor.fetchone()
		if row is None:
			text = "Single hai tu bc"
			cursor.execute("SELECT * FROM users WHERE USERNAME = ?",[un])
			row = cursor.fetchone()
			desc = row[10]
			return render_template('home.html',text=text,bio=desc)
		
		un1=row[1]
		cursor.execute("SELECT * FROM users WHERE USERNAME = ?",[un1])
		row = cursor.fetchone()
		fname=row[1]
		text = "Committed to "+str(fname)
		cursor.execute("SELECT * FROM users WHERE USERNAME = ?",[un])
		row = cursor.fetchone()
		desc = row[10]
		return render_template('home.html',text=text,bio=desc)
   	return redirect('/')

@app.route('/forgot_password/',methods = ['GET','POST'])
@is_logged_in
def forgot():
	if request.method == 'GET':
		return redirect('/')
	
	global email1
	email1 = request.form['email']
	
	global code1
	code1 = randint(1000000,9999999)
	TEXT1 = "Your verification code is " + str(code1)
	SUBJECT = "Verification Code"
	msg1 = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT1)

	#Create login Server
	server = smtplib.SMTP('smtp.googlemail.com', 587)
	server.starttls()
	server.ehlo()
	server.login("coupledal@gmail.com", "ShubhAksh@123")
	 
	#Send Mail
	user1 = email1
	server.sendmail("coupledal@gmail.com",user1, msg1)
	server.quit()
	global val
	val = randint(10000000,99999999999999)
	return redirect(url_for('passcode',value = val))

@app.route('/passcode/<value>')
@is_logged_in
def passcode(value):
	#print(couple["us1"])
	#print(couple["fname1"])
	global val
	val = randint(10000000,99999999999999)
	return render_template('passcode.html',val =value)


@app.route('/pverify/<val>', methods=['POST'])
@is_logged_in
def pverify(val):
	#try:
		code1e=int(request.form['pcode'])
		password = request.form['psw']
		cpassword = request.form['cpsw']

		if code1==code1e and password==cpassword:
			conn = sqlite3.connect('data.db')
			password = sha256_crypt.encrypt(password)

			#print(couple['psw1'])
			#print(sha256_crypt.encrypt(couple['psw1']))
			
			cur = conn.cursor()
			cur.execute("UPDATE users SET PASSWORD = ? WHERE EMAIL = ?", (password,email1))
									
			#except:
			#print("Error aa gaya bc")
				#conn.rollback()
			
			conn.commit()
			flash("Password changed")
			return redirect('/')

		else:
			flash('Verification Failed')
			return redirect(url_for('passcode',value = val))

	#except Exception as e:	
	#	flash('Verification Failed')
	#	return redirect(url_for('passcode',value = val))


@app.route('/login/', methods=['GET','POST'])
def login():
	if request.method=='GET':
		return redirect('/')
	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	row=None
	un=request.form["uname"]
	cursor.execute("SELECT * FROM users WHERE USERNAME = ?",[un])
	row = cursor.fetchone()
	if row==None:
		flash("Username does not exist")
		return redirect("/")
	if sha256_crypt.verify(request.form['psw'],row[5]):
		session['username'] = request.form['uname']
		return redirect("/home/")
	else:
		flash("Incorrect password")
		return redirect("/")


@app.route('/verify/<val>', methods=['POST'])
def verify(val):
	#try:
	code1e=int(request.form['ecode1'])
	code2e=int(request.form['ecode2'])

	if code1==code1e and code2==code2e:
		conn = sqlite3.connect('data.db')
		couple["psw1"] = sha256_crypt.encrypt(couple["psw1"])
		couple["psw2"] = sha256_crypt.encrypt(couple["psw2"])
		print(couple['psw1'])
		print(sha256_crypt.encrypt(couple['psw1']))
		#try:
		cur = conn.cursor()
		cur.execute("INSERT INTO users (USERNAME,FIRST_NAME,LAST_NAME,MOBILE,EMAIL,PASSWORD,AGE,GENDER,FLAG) VALUES (?,?,?,?,?,?,?,?,?)", (couple["us1"],couple["fname1"],couple["lname1"],couple["phone1"],couple["email1"],couple["psw1"],couple["age1"],couple["gender1"],1))
		cur.execute("INSERT INTO users (USERNAME,FIRST_NAME,LAST_NAME,MOBILE,EMAIL,PASSWORD,AGE,GENDER,FLAG) VALUES (?,?,?,?,?,?,?,?,?)", (couple["us2"],couple["fname2"],couple["lname2"],couple["phone2"],couple["email2"],couple["psw2"],couple["age2"],couple["gender2"],1))
		cur.execute("INSERT INTO couples (FIRST,SECOND,couple_id) VALUES(?,?,?)" , (couple['us1'],couple['us2'],couple['us1']))
		cur.execute("INSERT INTO couples (FIRST,SECOND,couple_id) VALUES(?,?,?)" , (couple['us2'],couple['us1'],couple['us1']))					
		'''except:
		#print("Error aa gaya bc")
			conn.rollback()
		'''
		conn.commit()
		flash("You have registered successfully.")
		return redirect('/')
	else:
		flash('Verification Failed')
		return redirect(url_for('enter_code',value = val))

	#except Exception as e:	
	flash('Verification Failed')
	return redirect(url_for('enter_code',value = val))

@app.route('/logout/')
def logout():
	session.pop('username',None)
	return redirect('/')

@app.route('/edit_bio/',methods=['GET','POST'])
@is_logged_in
def edit_bio():
	if request.method=='GET':
		return redirect('/home/')
	bio = request.form['bio']
	username = session['username']
	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	cursor.execute("UPDATE users SET BIO = ? WHERE USERNAME = ?", (bio,username))
	conn.commit()
	return redirect('/home/')

@app.route('/mood/')
@is_logged_in
def mood():
	return render_template('mood.html')

@app.route('/bajrang_dal/')
@is_logged_in
def bajrang_dal():
	conn = sqlite3.connect('data.db')
	curr = conn.cursor()
	curr.execute('SELECT * FROM bajrang')
	acts = curr.fetchall()
	return render_template('bajrang.html',acts = acts)

@app.route('/add_bajrang/',methods = ['GET','POST'])
@is_logged_in
def add_bajrang():
	if request.method!='POST':
		return redirect('/home/')
	date = request.form['date']
	place = request.form['place']
	time = request.form['time']
	incident = request.form['incident']

	conn = sqlite3.connect('data.db')
	curr = conn.cursor()
	curr.execute('INSERT INTO bajrang(DATE,TIME,PLACE,INCIDENT) VALUES(?,?,?,?)',(date,time,place,incident))
	conn.commit()

	return redirect('/bajrang_dal/')	


@app.route('/profile',methods = ['GET'])
@is_logged_in
def profile():
	if request.method!='GET':
		return redirect('/home')
    
	user = request.args['user']
	un = user
	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	row=None
	cursor.execute("SELECT * FROM users WHERE USERNAME = ?",[un])
	row = cursor.fetchone()
	desc = row[10]
	return render_template('profile.html',detail = row)
	

@app.route('/others/')
@is_logged_in
def others():
	other={}
	conn = sqlite3.connect('data.db')
	cursor=conn.cursor()
	cursor.execute("SELECT FIRST,SECOND,couple_id FROM couples GROUP BY couple_id HAVING COUNT(*) > 1")
	unique = cursor.fetchall()
	un = session['username']
	
	user1 = []
	user2 = []
	for user in unique:
		if user[0] == un or user[1] == un:
			pass
		else:
			cursor.execute("SELECT * FROM users WHERE USERNAME = ?",(user[0],))
			value_1 = cursor.fetchone()
			print(value_1[0],value_1[1])
			cursor.execute("SELECT * FROM users WHERE USERNAME = ?",(user[1],))
			value_2 = cursor.fetchone()
			text = str(value_1[1]) + " " + str(value_1[2]) + "," + str(value_2[1]) + " " + str(value_2[2]) + "," + str(value_1[0]) + "," + str(value_2[0])
			other[user[0]] = text
	return render_template('others.html',other = other)

@app.route('/restaurants/')
def res():
	if 'username' not in session:
		return redirect('/')

	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM restaurants")
	rs = cursor.fetchall()
	fr = []
	for rp in rs:
		cursor.execute("SELECT AVG(RATING) FROM resratings WHERE NAME = ?",[rp[0]])
		rate = str(cursor.fetchone())
		rate = rate.replace(",","")
		rate = rate.replace("(","")
		rate = rate.replace(")","")
		fr.append([rp[0],rp[1],rp[2],rate])
		
	return render_template("restaurants.html",fr=fr)


@app.route('/add_res/',methods=['GET','POST'])
def add_res():

	if 'username' not in session:
		return redirect('/')

	name = request.form['Name']
	pin = request.form['pin']
	url = request.form['url']
	
	conn = sqlite3.connect('data.db')
	curr = conn.cursor()
	curr.execute('SELECT * FROM restaurants WHERE NAME = ? AND PIN = ?',(name,pin))
	row = curr.fetchone()
	if row is None:
		curr.execute('INSERT INTO restaurants(NAME,PIN,URL) VALUES(?,?,?)',(name,pin,url))
	else:
		flash("Restaurant already exists")
		return redirect('/restaurants/')
	conn.commit()
	return redirect('/restaurants/')


@app.route('/resratings',methods=['GET'])
def resrate():
	if 'username' not in session:
		return redirect('/')

	name = request.args['name']
	username = session['username']
	rate = request.args['rate']
	conn = sqlite3.connect('data.db')
	cur = conn.cursor()
	cur.execute('SELECT * FROM resratings WHERE USER = ? AND NAME = ?',(username,name))
	row = cur.fetchone()
	if row is None:
		cur.execute('INSERT INTO resratings(USER,NAME,RATING) VALUES(?,?,?)',(username,name,rate))
	else:
		cur.execute('UPDATE resratings SET RATING = ? WHERE USER = ? AND NAME = ?',(rate,username,name))
	conn.commit()
	return redirect('/restaurants/')



@app.route('/theatres/')
def t():
	if 'username' not in session:
		return redirect('/')

	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM theatres")
	rs = cursor.fetchall()
	fr = []
	for rp in rs:
		cursor.execute("SELECT AVG(RATING) FROM tratings WHERE NAME = ?",[rp[0]])
		rate = str(cursor.fetchone())
		rate = rate.replace(",","")
		rate = rate.replace("(","")
		rate = rate.replace(")","")
		fr.append([rp[0],rp[1],rate])
		
	return render_template("theatres.html",fr=fr)


@app.route('/add_t/',methods=['GET','POST'])
def add_t():

	if 'username' not in session:
		return redirect('/')

	name = request.form['Name']
	pin = request.form['taddr']
	
	conn = sqlite3.connect('data.db')
	curr = conn.cursor()
	curr.execute('SELECT * FROM theatres WHERE NAME = ? AND ADDR = ?',(name,pin))
	row = curr.fetchone()
	if row is None:
		curr.execute('INSERT INTO theatres(NAME,ADDR) VALUES(?,?)',(name,pin))
	else:
		flash("Theatre already exists")
		return redirect('/theatres/')
	conn.commit()
	return redirect('/theatres/')


@app.route('/tratings',methods=['GET'])
def trate():
	if 'username' not in session:
		return redirect('/')

	name = request.args['name']
	username = session['username']
	rate = request.args['rate']
	conn = sqlite3.connect('data.db')
	cur = conn.cursor()
	cur.execute('SELECT * FROM tratings WHERE USER = ? AND NAME = ?',(username,name))
	row = cur.fetchone()
	if row is None:
		cur.execute('INSERT INTO tratings(USER,NAME,RATING) VALUES(?,?,?)',(username,name,rate))
	else:
		cur.execute('UPDATE tratings SET RATING = ? WHERE USER = ? AND NAME = ?',(rate,username,name))
	conn.commit()
	return redirect('/theatres/')

	conn.commit()
	return redirect('/restaurants/')


@app.route('/breakup/')
@is_logged_in
def breakup():
	un = session['username']
	row = None
	conn = sqlite3.connect('data.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE USERNAME = ?",(un,))
	row = cur.fetchone()
	if row is not None:
		if int(row[9]) == 0:
			flash('Single hai bc')
			return redirect(url_for('home'))

		else:
			lover = []
			username_from_couple = None
			cur.execute("SELECT * FROM couples WHERE FIRST = ?",(un,))
			username_from_couple = cur.fetchone()
			if username_from_couple is not None:
				lover_username = username_from_couple[1]
				cur.execute("SELECT * FROM users WHERE USERNAME = ?",(lover_username,))
				lover_detail = cur.fetchone()
				lover.extend([lover_detail[0],lover_detail[1],lover_detail[2],lover_detail[3],lover_detail[4],lover_detail[7],lover_detail[8],lover_detail[10]])

				return render_template('breakup_new.html',detail = lover)
			else:
				return redirect(url_for('home'))
				
				
	else:
		return redirect(url_for('home'))

@app.route('/confirm_breakup/',methods=['GET'])
@is_logged_in
def confirm_breakup():
	
	un = session['username']
	row = None
	conn = sqlite3.connect('data.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE USERNAME = ?",(un,))
	row = cur.fetchone()
	print (row[9])
	if row is not None:
		if row[9] == 0:
			return redirect(url_for('home'))
		else:
			col = None
			cur.execute("SELECT * FROM couples WHERE FIRST = ?",(un,))
			col = cur.fetchone()
			love = col[1]
			#print love
			cur.execute("UPDATE users SET notification = ? WHERE USERNAME = ?",("breakup",love,))
			conn.commit()
			flash('Notification Send for breakup,if confirmed you will no longer be couple')
			return redirect(url_for('home'))
	else:
		return(redirect(url_for('home')))
	
@app.route('/notification/')
@is_logged_in
def notification():
	un = session['username']
	row = None
	conn = sqlite3.connect('data.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE USERNAME = ?",(un,))
	row = cur.fetchone()
	if row[11] == "breakup":
		return render_template('ask.html')
	else:
		return "No Notifications"


@app.route('/sad/',methods=['POST'])
@is_logged_in
def sad():
	un = session['username']
	result = request.form['email']
	print result
	row = None
	conn = sqlite3.connect('data.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE USERNAME = ?",(un,))
	row = cur.fetchone()
	if result == "Y" or result=="y":
		if sha256_crypt.verify(request.form['pwd'],row[5]):
			cur.execute("SELECT * FROM couples WHERE FIRST = ? ",(un,))
			col = None
			col = cur.fetchone()
			if col is not None:
				other_one = col[1]
				cur.execute("DELETE FROM couples WHERE FIRST = ?",(un,))
				conn.commit()
				cur.execute("DELETE FROM couples WHERE FIRST = ?",(other_one,))
				conn.commit()
				cur.execute("UPDATE users SET FLAG = ? WHERE USERNAME = ?",(0,un,))
				conn.commit()
				cur.execute("UPDATE users SET FLAG = ? WHERE USERNAME = ?",(0,other_one,))
				conn.commit()
				cur.execute("UPDATE users SET notification = NULL WHERE USERNAME = ?",(un,))
				conn.commit()
				cur.execute("UPDATE users SET notification = NULL WHERE USERNAME = ?",(other_one,))
				conn.commit()			
				return redirect(url_for('home'))
			else:
				return redirect(url_for('home'))
		else:
			flash('Incorrect Password')
	else:
		return redirect(url_for('home'))			

@app.route('/search_partner')
@is_logged_in
def search_partner():
    other = {}
    unique = None
    un = session['username']
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM USERS WHERE USERNAME != ? and FLAG = ?",(un,0,))
    unique = cur.fetchall()
    if unique == None:
        flash('No single user found')
        return redirect(url_for('home'))
    else:
        for user in unique:
            cursor.execute("SELECT * FROM users WHERE USERNAME = ?",(user[0],))
            value_1 = cursor.fetchone()
            text = str(value_1[1] + " " + str(value_1[2]) + "," + str(value_1[0]))
            other[user[0]] = text
        return render_template('singles.html',other = other)








if __name__=='__main__':
    app.run(debug=True)