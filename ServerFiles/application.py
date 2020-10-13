#DATE           TEAM MEMBER         UPDATE
#09/24/2020     DROBERTS            Created application.py frame
#10/03/2020     NCROWN              Created authenticate() function for login
#10/04/2020     NCROWN              Updated functionality of authenticate() to connect to database and compare hashed passwords
#10/04/2020     TFEITOSA            Created newclass() function for newclass interface
#10/05/2020     NCROWN              Updated application to handle sessions, removed demo code, and added logout function
#10/05/2020     DROBERTS            Changed application to run with new SSL certificates
#10/05/2020     NCROWN              Added addaccount, Added sessioncount function and related code to login function to prevent excessive login attempts
#10/05/2020     TFEITOSA            Created show_calendar() function for the calendar interface
#10/06/2020     NCROWN              Added error handling for database connection error to authenticate(); Added form support for newaccount; implemented passHash() and DisconnectDB(); added backend for confirm.html
#10/07/2020     TFEITOSA            Worked on calendar() interface
#10/07/2020     NCROWN              Fixed errors on backend of confirm() function for passing empty tuples by using global variables
#10/07/2020     NCROWN              Implemented tuplebuilder functions; continued development on confirm() function
#10/08/2020     TFEITOSA            Continued work on calendar() interface
#10/08/2020     NCROWN              Implemented SHA256 password encryption, completed confirm()/newaccount() functionality; updated newclass to interact with confirm() functionality; completed newclass() functionality; added template for listaccounts, listclasses, modifyaccount, and modifyclass
#10/09/2020     NCROWN              Added handling for duplicate username submissions in newaccount(); simplified imports; worked on listaccounts, listclasses, modifyaccount, and modifyclasses
#10/10/2020     NCROWN              Completed work for modifyaccount backend; account deletion and modification functionality completed, class deletion and modification functionality completed
#10/10/2020     TFEITOSA            Worked on functionality for attendance()

from flask import Flask, render_template, request, session, redirect, url_for, flash
from app_calendar import *
from database_connector import *
from datetime import timedelta, date
from passwordhashgen import *
from tuplebuilder import *
import json

#global variables to mitigate issue with passing queries and tuples to confirm()
query = ''
queryTuple = ''
inputID = 0

#flask framework
app = Flask(__name__)
app.config['SECRET_KEY'] ='12345'

#Session handling
@app.route('/', methods=['get'])
def sessioncount():
    #Sets lifetime of session to 5 minutes for login attempts
    if "instructor" in session:
        return redirect(url_for('show_calendar'))
    else:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        #If no attempt session is active, creates the session
        if "attempt" not in session:
            session['attempt'] = 0
    return redirect(url_for('authenticate'))


#Login handling    
@app.route('/login', methods=['post', 'get'])
def authenticate():
    message = ''
    error = ''
    #Handles if the user navigated directly to login and didn't set a sessioncount
    if "attempt" not in session:
        return redirect(url_for('sessioncount'))
    #Correct path
    else:
        if request.method == 'POST':
            #Blocks user from excessive login attempts
            if session['attempt'] >= 3:
                message = "Too many failed attempts. Please wait 5 minutes."
            #Correct path
            else:
                #Imports form data from index.html
                username = request.form.get('formuser') 
                userpass = request.form.get('formpass')
                #Connecting to the database
                try:
                    mydb = ConnectDB()
                    #Queries the database for credentials
                    mycursor = mydb.cursor()
                    mycursor.execute("SELECT PassHash FROM Accounts WHERE Username = %s", (username,))
                    result = mycursor.fetchone()
                    #Checks for results
                    if (result is None):
                        message = "Incorrect username or password"
                        attempt = session.get('attempt')
                        attempt += 1
                        session['attempt']=attempt
                    #Compares hashed passwords
                    else:
                        #Correct path
                        importHash = ''.join(result)
                        passwordCompare = False
                        passwordCompare = passCompare(userpass, importHash)
                        if passwordCompare == True:
                            message = "Correct credentials"
                            #Creates session with username
                            app.permanent_session_lifetime = timedelta(minutes=15)
                            session['instructor'] = username
                            session.pop('attempt', None)
                            return redirect(url_for('show_calendar'))           
                        #Incorrect credentials
                        else:
                            message = "Incorrect username or password"
                            attempt = session.get('attempt')
                            attempt += 1
                            session['attempt']=attempt
                #Handles database connection errors
                except:
                    error = "Database error"
        #Handles session already being active
        else:
            if "instructor" in session:
                return redirect(url_for('show_calendar'))
            
    return render_template('login.html', message=message, error=error)


#Handles logging the user out
@app.route('/logout')
def logout():
    #Kills the user session, logging them out
    session.pop('instructor', None)
    return redirect(url_for('sessioncount'))


#Handles the calendar
@app.route('/calendar', methods = ['GET', 'POST'])
def show_calendar():
    #active session
    
    if "instructor" in session:
        # Getting variables to build the calendar
        y = get_year()
        m = get_month()
        mn = get_month_name()
        day_selected = get_today()
        dm = get_days_in_month()
        wd = get_first_weekday()
        t = get_total_accounts()
        tc = get_classes_today()
        ac = get_all_classes_TESTING()
        
        
        # Gets user input on Calendar day buttons
        if request.method == 'POST':
            #Imports form data from calendar.html
            if 'cal_day' in request.form:
                day_selected = request.form.get('cal_day')
                return redirect(url_for('calendar'))
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('calendar.html', year=y, month=m, day=day_selected, days_in_month=dm,
    weekday=wd, month_name=mn, total_accounts=t, all_classes=ac, today_classes=tc)


#Handles creation of new accounts    
@app.route('/newaccount', methods = ['GET', 'POST'])
def newaccount():
    error = ''
    #active session
    if "instructor" in session:
        try: 
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            #Populates belt selection dropdown
            mycursor.execute("SELECT * FROM BeltRanks order by BeltID")
            beltList = mycursor.fetchall()
            if request.method == 'POST':
                #Imports form data from newaccount.html
                firstName = request.form.get('first_name')
                lastName = request.form.get('last_name')
                address = request.form.get('address') 
                phone = request.form.get('phone')
                email = request.form.get('email') 
                birthdate = request.form.get('birthday')
                parent = request.form.get('parent') 
                notes = request.form.get('notes')
                belt = request.form.get('belt')
                instructor = request.form.get('instructor') 
                username = request.form.get('username')
                password = request.form.get('password')
                userStatus = request.form.get('userstatus')
                #userstatus checkbox unchecked
                if userStatus == None:
                    userStatus = 0
                #userstatus checkbox checked
                else:
                    userStatus = 1
                #Handles instructor checkbox value and rogue username/password entry
                if instructor == None:
                    instructor = 0
                    username = None
                    password = None
                else:
                    instructor = 1
                    password = passHash(password)
                #Duplicate username handling
                mycursor.execute("SELECT Username FROM Accounts WHERE Username = %s", (username,))
                usernameResult = mycursor.fetchall()
                #No duplicate usernames
                if (username is None) or (usernameResult == []):
                    #Query tuple constuction
                    global queryTuple
                    queryTuple = accountTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password)
                    #final query construction
                    global query
                    query = accountQuery(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password)
                    #Checks Accounts for anyone with the same name
                    mycursor.execute("SELECT AccountID FROM Accounts WHERE Last_Name = %s AND First_Name = %s", (lastName, firstName))
                    result = mycursor.fetchall()
                    print(result)
                    #Unique name
                    if result == []:
                        #Submits data into database
                        mycursor.execute(query, queryTuple)
                        mydb.commit()
                        #Flash message passed to next page load
                        flash('Record added.', 'success')
                        #Clear globals
                        query = ''
                        queryTuple = ''
                        return redirect(url_for('newaccount'))
                    #Name found in database
                    else:
                        #Builds name string
                        name = firstName + ' ' + lastName
                        #redirect to confirm() with variables
                        return redirect(url_for('confirm', name=name, page='newaccount'))
                #Duplicate username
                else:
                    error = 'Username already present in database. Please re-enter information and try again.'
        #Handles database connection errors
        except:
                error = 'Database error'
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('newaccount.html', beltList=beltList, error=error)


#Confirmation handling
@app.route('/confirm/<name>/<page>', methods = ['GET', 'POST'])
def confirm(name, page):
    #Calls global query
    confirmQuery = globals()['query']
    error = ''
    #Session good
    if "instructor" in session:
        #If the query is empty, redirects back to the calendar
        if confirmQuery == None:
            redirect(url_for('show_calendar'))
        #Good path
        else:
            #Get global queryTuple
            confirmQueryTuple = globals()['queryTuple']
            #Good path
            try:
                mydb = ConnectDB()
                mycursor = mydb.cursor()
                #Constructs message for display on the confirm.html page
                message = 'There is already a database entry for ' + name + ". Do you wish to create a new record anyway?"
                #Button press
                if request.method == 'POST':
                    #Calls globals for clearing
                    global query
                    global queryTuple
                    #Handles confim button
                    if 'confirmbutton' in request.form:
                        #Insert query/tuple into database
                        mycursor.execute(confirmQuery, confirmQueryTuple)
                        mydb.commit()
                        #Pass flash message to next page
                        if (page == "listaccounts") or (page == "listclasses"):
                            flash('Record modified.', 'success')
                        else:
                            flash('Record added.', 'success')
                        #Reset globals
                        query = ''
                        queryTuple = ''
                        inputID = 0
                        
                        return redirect(url_for(page))
                    #Handles deny button
                    elif 'denybutton' in request.form:
                        #Pass flash message to next page
                        if (page == "listaccounts") or (page == "listclasses"):
                            flash('Cancelled record update.', 'success')
                        else:
                            flash('Cancelled record upload.', 'success') 
                        #Reset globals
                        query = ''
                        queryTuple = ''
                        inputID = 0
                        return redirect(url_for(page))
            #Handles database connection errors
            except:
                error = 'Database error'
    #Session bad
    else:
        return redirect(url_for('sessioncount'))
    return render_template('confirm.html', message=message, error=error, name=name, page=page)


#Handles creation of new classes
@app.route('/newclass', methods = ['GET', 'POST'])
def newclass():
    error = ''
    #Session good
    if "instructor" in session:
        #Build lists for select options in newclass.html
        hourList = ["00", "01", "02", "03", "04" , "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
        minuteList = ["00", "15", "30", "45"]
        if request.method == "POST":
            #Get values from newclass.html form
            class_name = request.form.get('class_name')
            date = request.form.get('date')
            start_hour = request.form.get('starthour')
            end_hour = request.form.get('endhour')
            start_minute = request.form.get('startminute')
            end_minute = request.form.get('endminute')
            
            #Send times to timeBuilder to construct time strings
            start_time = timeBuilder(start_hour, start_minute)
            end_time = timeBuilder(end_hour, end_minute)
            
            #Update query and queryTuple global variables to facilitate confirm()
            global query
            query = "INSERT INTO Classes (ClassName, ClassDate, ClassStartTime, ClassEndTime) VALUES (%s, %s, %s, %s)"
            global queryTuple
            queryTuple = (class_name, date, start_time, end_time)
            
            #Good path
            try: 
                mydb = ConnectDB()
                mycursor = mydb.cursor()
                #Query database to see if class exists in this time/date slot
                mycursor.execute("SELECT ClassStartTime FROM Classes WHERE ClassDate = %s", (date,))
                result = mycursor.fetchall()
                #Compares query results to current form data
                if result == []:
                    #Submits data into database
                    mycursor.execute(query, queryTuple)
                    mydb.commit()
                    #Flash message for next page load
                    flash('Record added.', 'success')
                    #Clear globals
                    query = ''
                    queryTuple = ''
                    return redirect(url_for('newclass'))
                #Date found in database
                else:
                    #Time and date found in database, asks user to confirm creation of new class
                    if (any(start_time in i for i in result)):
                        #Builds name string
                        name = "class starting at " + start_time + " on " + date
                        #Redirects to confirm() with variables
                        return redirect(url_for('confirm', name=name, page='newclass'))
                    #Unique class
                    else:
                        #Submits data into database
                        mycursor.execute(query, queryTuple)
                        mydb.commit()
                        #Flash message for next page load
                        flash('Record added.', 'success')
                        #Clear globals
                        query = ''
                        queryTuple = ''
                        return redirect(url_for('newaccount'))
            #Handles database connection errors
            except:
                error = 'Database error'
    #Session bad
    else:
        return redirect(url_for('sessioncount'))
        
    return render_template('newclass.html', error=error, hourList=hourList, minuteList=minuteList)


#Handles class modification and deletion    
@app.route('/modifyclass', methods=['GET', 'POST'])
def modifyclass():
    error = ''
    #active session
    if "instructor" in session:
        #Build lists for select options in newclass.html
        hourList = ["00", "01", "02", "03", "04" , "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
        minuteList = ["00", "15", "30", "45"]
        #Good path
        try: 
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            #Populates data from query
            global inputID
            #Checks global variable incase of direct access to page
            if inputID == 0:
                return redirect(url_for('listclasses'))
            #Good path
            else:
                mycursor.execute("SELECT ClassID, ClassName, ClassDate, ClassStartTime, ClassEndTime FROM Classes WHERE ClassID = %s", (inputID,))
                classData = mycursor.fetchone()
                class_name = classData[1]
                date = classData[2]
                #Breaks time string into an array with delimiter :
                start_time = classData[3].split(':')
                end_time = classData[4].split(':')
                #Assembles data for insertion into form
                classDataList = (inputID, class_name, date, start_time[0], start_time[1], end_time[0], end_time[1])
                if request.method == 'POST':
                    #Delete record path
                    if 'classdeletebutton' in request.form:
                        mycursor.execute("DELETE FROM Classes WHERE ClassID = %s", (inputID,))
                        mydb.commit()
                        #Flash message for next page load
                        flash('Record deleted.', 'success')
                        return redirect(url_for('listclasses'))
                    #Update path
                    elif 'classsubmitbutton' in request.form:
                        #Get values from modifyclass.html form
                        class_name = request.form.get('class_name')
                        date = request.form.get('date')
                        start_hour = request.form.get('starthour')
                        end_hour = request.form.get('endhour')
                        start_minute = request.form.get('startminute')
                        end_minute = request.form.get('endminute')
                        
                        #Send times to timeBuilder to construct time strings
                        start_time = timeBuilder(start_hour, start_minute)
                        end_time = timeBuilder(end_hour, end_minute)
                        
                        #Update query and queryTuple global variables to facilitate confirm()
                        global query
                        query = "UPDATE Classes SET ClassName = %s, ClassDate = %s, ClassStartTime = %s, ClassEndTime = %s WHERE ClassID = %s"
                        global queryTuple
                        queryTuple = (class_name, date, start_time, end_time, inputID)
                        #Checks classes for anyone with the same last name
                        mycursor.execute("SELECT ClassID FROM Classes WHERE ClassDate = %s AND ClassStartTime = %s", (date, start_time,))
                        result = mycursor.fetchall()
                        #Compares query results to current form data
                        if (result == []):
                            #Submits data into database
                            mycursor.execute(query, queryTuple)
                            mydb.commit()
                            #Flash message passed to next page load
                            flash('Record updated.', 'success')
                            #Clear globals
                            query = ''
                            queryTuple = ''
                            inputID = 0
                            return redirect(url_for('listclasses'))
                        #Last name found in database
                        else:
                            #Class found in database, asks user to confirm modifying class
                            if (any(classData[0] in i for i in result)):
                                #submits data into database
                                mycursor.execute(query, queryTuple)
                                mydb.commit()
                                #Flash message passed to next page load
                                flash('Record updated.', 'success')
                                #Clear globals
                                query = ''
                                queryTuple = ''
                                inputID = 0
                                return redirect(url_for('listclasses'))
                            #Class found in database that doesn't match ClassID, asks user to confirm class modification
                            else:
                                #Builds name string
                                name = "class starting at " + start_time + " on " + date
                                #redirect to confirm() with variables
                                return redirect(url_for('confirm', name=name, page='listclasses'))
        #Handles database connection errors    
        except:
                error = 'Database error'
        
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('modifyclass.html', error=error, hourList=hourList, minuteList=minuteList, classDataList=classDataList)


#Handles class selection  
@app.route('/listclasses', methods=['GET', 'POST'])
def listclasses():
    error = ''
    #active session
    if "instructor" in session:
        #Good path
        try: 
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            #Populates class selection dropdown
            mycursor.execute("SELECT ClassID, ClassName, ClassDate, ClassStartTime, ClassEndTime FROM Classes order by ClassID")
            classList = mycursor.fetchall()
            #Submit button pressed
            if request.method == 'POST':
                #Imports form data from listclasses.html
                global inputID
                inputID = request.form.get('classes')
                if 'submitbutton' in request.form:
                    return redirect(url_for('modifyclass'))
                elif 'attendance' in request.form:
                    return redirect(url_for('attendance'))
            
        #Handles database connection errors    
        except:
            error = 'Database error'
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('listclasses.html', error=error, classList=classList)

#Handles attendance for a class
@app.route('/attendance', methods = ['GET', 'POST'])
def attendance():
    error = ''
    
    #active session
    if "instructor" in session:
        
        try:
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            # Grabbing Label variables about class
            global inputID
            mycursor.execute("SELECT ClassName, ClassDate FROM Classes WHERE ClassID = %s", (inputID,))
            class_data = mycursor.fetchone()
            name = class_data[0]
            date = class_data[1]
            # Grabbing Accounts List for attendance
            mycursor.execute("SELECT AccountID, First_Name, Last_Name FROM Accounts ORDER BY Last_Name")
            accountList = mycursor.fetchall()
            # Update Attendance on submission
            if request.method == 'POST':
                if 'confirm' in request.form:
                    students = request.form.get('selected')
                    students_json = json.dumps(students)
                    query = "UPDATE Classes SET Attendance = %s WHERE ClassID = %s"
                    mycursor.execute(query, (students_json, inputID,))
                    mydb.commit()
                    testing = ["test", "2", "0233"]
                    flash('Attendance Recorded', 'success')
                    #Clear globals
                    query = ''
                    inputID = 0
                    return redirect(url_for('listclasses'))
        except:
            error = "Database Error"
            
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('attendance.html', error=error, class_name=name, class_date=date, accountList=accountList)

#Handles account modification and deletion    
@app.route('/modifyaccount', methods=['GET', 'POST'])
def modifyaccount():
    error = ''
    #active session
    if "instructor" in session:
        #Good path
        try: 
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            #Populates belt selection dropdown
            mycursor.execute("SELECT * FROM BeltRanks order by BeltID")
            beltList = mycursor.fetchall()
            #Populates data from query
            global inputID
            #Checks global variable incase of direct access to page
            if inputID == 0:
                return redirect(url_for('listaccounts'))
            #Good path
            else:
                mycursor.execute("SELECT * FROM Accounts where AccountID = %s", (inputID,))
                accountData = mycursor.fetchone()
                firstname = accountData[1]
                lastname = accountData[2]
                address = accountData[3]
                if address == None:
                    address = ""
                phone  = accountData[4]
                instructor = accountData[5]
                birthdate = accountData[6]
                email = accountData[7]
                if email == None:
                    email = ""
                parent = accountData[8]
                if parent == None:
                    parent = ""
                belt = accountData[9]
                status = accountData[10]
                notes = accountData[11]
                if notes == None:
                    notes = ""
                username = accountData[12]
                if username == None:
                    username =""
                #Assembles data for insertion into form
                accountList = (inputID, firstname, lastname, address, phone, instructor, birthdate, email, parent, belt, status, notes, username)
                if request.method == 'POST':
                    #Delete record path
                    if 'accountdeletebutton' in request.form:
                        #Protects the admin account from deletion
                        if accountData[0] == 1:
                            flash('Record cannot be deleted.', 'success')
                            return redirect(url_for('listaccounts'))
                        #Delete record path
                        else:
                            mycursor.execute("DELETE FROM Accounts WHERE AccountID = %s", (inputID,))
                            mydb.commit()
                            #Flash message for next page load
                            flash('Record deleted.', 'success')
                            return redirect(url_for('listaccounts'))
                    #Update path
                    elif 'accountsubmitbutton' in request.form:
                        #Imports form data from newaccount.html
                        firstName = request.form.get('first_name')
                        lastName = request.form.get('last_name')
                        address = request.form.get('address') 
                        phone = request.form.get('phone')
                        email = request.form.get('email') 
                        birthdate = request.form.get('birthday')
                        parent = request.form.get('parent') 
                        notes = request.form.get('notes')
                        belt = request.form.get('belt')
                        instructor = request.form.get('instructor') 
                        username = request.form.get('username')
                        password = request.form.get('password')
                        userStatus = request.form.get('userstatus')
                        #Prevents removal of admin account login 
                        if (accountData[0] == 1) and (instructor == None):
                            flash('Record cannot have instructor property removed.', 'success')
                            return redirect(url_for('listaccounts'))
                        #Update path
                        else:
                            #userstatus checkbox unchecked
                            if userStatus == None:
                                userStatus = 0
                            #userstatus checkbox checked
                            else:
                                userStatus = 1
                            #instructor checkbox unchecked
                            if instructor == None:
                                instructor = 0
                                username = None
                                password = None
                            #instructor checkbox uhecked
                            else:
                                instructor = 1
                                #Handles password changes
                                if password != None:
                                    password = passHash(password)
                            #final query construction
                            global query
                            query = accountUpdateQuery(password)
                            #Query tuple constuction
                            global queryTuple
                            queryTuple = accountUpdateTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password, inputID)
                            #Checks Accounts for anyone with the same last name
                            mycursor.execute("SELECT AccountID FROM Accounts WHERE (Last_Name = %s AND First_Name = %s)", (lastName, firstName,))
                            result = mycursor.fetchall()
                            #Compares query results to current form data
                            if (result == []):
                                #Submits data into database
                                mycursor.execute(query, queryTuple)
                                mydb.commit()
                                #Flash message passed to next page load
                                flash('Record updated.', 'success')
                                #Clear globals
                                query = ''
                                queryTuple = ''
                                inputID = 0
                                return redirect(url_for('listaccounts'))
                            #AccountIDs found in database
                            else:
                                #Current account is one of the AccountIDs
                                if (any(accountData[0] in i for i in result)):
                                    #submits data into database
                                    mycursor.execute(query, queryTuple)
                                    mydb.commit()
                                    #Flash message passed to next page load
                                    flash('Record updated.', 'success')
                                    #Clear globals
                                    query = ''
                                    queryTuple = ''
                                    inputID = 0
                                    return redirect(url_for('listaccounts'))
                                #Name found in database that doesn't match accountID, asks user to confirm account modification
                                else:
                                    #Builds name string
                                    name = firstName + ' ' + lastName
                                    #redirect to confirm() with variables
                                    return redirect(url_for('confirm', name=name, page='listaccounts'))
        #Handles database connection errors
        except:
            error = 'Database error'
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('modifyaccount.html', error=error, accountList=accountList, beltList=beltList)


#Handles account selection    
@app.route('/listaccounts', methods=['GET', 'POST'])
def listaccounts():
    error = ''
    #active session
    if "instructor" in session:
        #Good path
        try: 
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            #Populates account selection dropdown
            mycursor.execute("SELECT AccountID, First_Name, Last_Name, DOB, Phone FROM Accounts order by AccountID")
            accountList = mycursor.fetchall()
            #Submit button pressed
            if request.method == 'POST':
                #Imports form data from listaccounts.html
                global inputID
                inputID = request.form.get('account')
                return redirect(url_for('modifyaccount'))
        
        #Handles database connection errors    
        except:
                error = 'Database error'
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('listaccounts.html', error=error, accountList=accountList)

    
#flask framework
app.run(ssl_context='adhoc', host='0.0.0.0', port=8080)