#DATE           TEAM MEMBER         UPDATE
#09/24/2020     DROBERTS            Created application.py
#10/03/2020     NCROWN              Created authenticate() function for login
#10/04/2020     NCROWN              Updated functionality of authenticate() to connect to database and compare hashed passwords
#10/05/2020     NCROWN              Updated application to handle sessions,removed demo code, and added logout function

from flask import Flask, render_template, request, session
from testform import TestForm
from classes import NewClassForm
from database_connector import ConnectDB
import hashlib
import mysql.connector

app = Flask(__name__)

app.config['SECRET_KEY'] ='12345'
  
@app.route('/', methods=['post', 'get'])
def authenticate():
    message = ''
    if request.method == 'POST':
        #Imports form data from index.html
        username = request.form.get('formuser') 
        userpass = request.form.get('formpass')
        #Password/salt hash conversion
        salt = "salt"
        db_password = userpass+salt
        dbhashed = hashlib.md5(db_password.encode())
        suppliedHash = dbhashed.hexdigest()
        #Connecting to the database
        mydb = ConnectDB()
        #Queries the database for credentials
        mycursor = mydb.cursor()
        mycursor.execute("SELECT PassHash FROM Accounts WHERE Username = %s", (username,))
        result = mycursor.fetchone()
        importHash = ''.join(result)
        #Checks for results
        if result is None:
            message = "Incorrect username or passworde"
        #Compares hashed passwords
        else:
            #Correct path
            if importHash == suppliedHash:
                message = "Correct credentials"
                #Creates session with username
                session['instructor'] = username
                return calendar()           
            #Incorrect credentials
            else:
                message = "Incorrect username or password"
    #Handles session already being active
    else:
        if "instructor" in session:
            return calendar()
            
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    #Kills the user session, logging them out
    session.pop('instructor', None)
    return authenticate()

@app.route('/calendar')
def calendar():
    #active session
    if "instructor" in session:
        placeholder = 1
    #bad session
    else:
        return authenticate()
    return render_template('calendar.html')
    
@app.route('/newclass', methods = ['GET', 'POST'])
def newclass():
    #Session good
    if "instructor" in session:
        message = ''
        if request.method == "POST":
            class_name = request.form["class_name"]
            date = request.form["date"]
            start_time = request.form["start_time"]
            end_time = request.form["end_time"]
            students = request.form["students"]
            instructors = request.form["instructors"]
            
            query = "INSERT INTO Classes (ClassName, ClassDate, ClassStartTime, ClassEndTime) VALUES"
            query += "(" + class_name + "," + date + "," + start_time + "," + end_time + ");"
            
            try: 
                mydb = ConnectDB()
                comm = mydb.cursor()
                comm.execute(query)
                message = "Class Recorded"
            except OSError:
                message = "Unable to save class"
    #Session bad
    else:
        return authenticate()
    
    return render_template('newclass.html')

app.run(ssl_context='adhoc', host='0.0.0.0', port=8080)
