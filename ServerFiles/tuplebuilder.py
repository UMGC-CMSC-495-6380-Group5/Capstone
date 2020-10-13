#DATE           TEAM MEMBER         UPDATE
#10/08/2020     NCROWN              Created tuplebuilder.py to handle building of queries and tuples for newaccount, created timeBuilder to handle time string construction
#10/10/2020     NCROWN              Created accountUpdateTuple and accountUpdateQuery to handle query building for modifying accounts

#Function for building inputs to new account
def accountTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password):
    queryTuple = (firstName, lastName, phone, instructor, birthdate, belt, userStatus)
    if (email != '') and (email != None):
        queryTuple = queryTuple + (email,)
    if (parent != '') and (parent != None):
        queryTuple = queryTuple + (parent,)
    if (notes != '') and (notes != None):
        queryTuple = queryTuple + (notes,)
    if (address != '') and (address != None):
        queryTuple = queryTuple + (address,)
    if (username != '') and (username != None):
        queryTuple = queryTuple + (username,)
    if (password != '') and (password != None):
        queryTuple = queryTuple + (password,)
    return queryTuple

#Function for building inputs to modify account
def accountUpdateTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password, accountID):
    queryTuple = (firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username)
    if (password != '') and (password != None):
        queryTuple = queryTuple + (password,)
    queryTuple = queryTuple + (accountID,)
    return queryTuple

#Function for building query for new account
def accountQuery(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password):
    queryStart = "INSERT INTO Accounts (First_Name, Last_Name, Phone, Instructor, DOB, Belt, Status"
    queryValues = ") VALUES (%s, %s, %s, %s, %s, %s, %s"
    queryEnd = ")"
    #Query building
    if (email != '') and (email != None):
        queryStart += ", Email"
        queryValues += ", %s"
    if (parent != '') and (parent != None):
        queryStart += ", Parent"
        queryValues += ", %s"
    if (notes != '') and (notes != None):
        queryStart += ", Notes"
        queryValues += ", %s"
    if (address != '') and (address != None):
        queryStart += ", Address"
        queryValues += ", %s"
    if (username != '') and (username != None):
        queryStart += ", Username"
        queryValues += ", %s"
    if (password != '') and (password != None):
        queryStart += ", PassHash"
        queryValues += ", %s"
    #final query construction
    query = queryStart+queryValues+queryEnd 
    return query
    
#unction for building query to modify account
def accountUpdateQuery(password):
    queryStart = "UPDATE Accounts SET First_Name = %s, Last_Name = %s, Phone = %s, Instructor = %s, DOB = %s, Belt = %s, Status = %s, Email = %s, Parent = %s, Notes = %s, Address = %s, Username = %s"
    queryEnd = "WHERE AccountID = %s"
    #Query building
    if password != None:
        queryStart += ", PassHash = %s"
    #final query construction
    query = queryStart+queryEnd 
    return query

#Function for building time inputs for classes    
def timeBuilder(hour, minute):
    print(hour)
    print(minute)
    buildTime = hour + ":" + minute + ":00"
    return buildTime