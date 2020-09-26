import mysql.connector

#Connecting to the database
mydb = mysql.connector.connect(
    host ="oyd-database.ckc4mk1cvfc5.us-east-1.rds.amazonaws.com",
    user="admin",
    password="databaseadmin"
    )

#Example of executing a parameterized call
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE %s" % ("StudentDatabase"))