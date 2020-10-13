from database_connector import ConnectDB, DisconnectDB
class Attendance:
    """Contains functionality for recording attendance"""
    
    def __init__(self, database_cursor):
        self.db_cursor = database_cursor
    
    def get_avalible_classes(self):
        query = "SELECT * FROM Classes"
        self.db_cursor.execute(query)
        classes = []
        for result in self.db_cursor:
            classes.append(result)
        return classes
        
        
#Serverside test code
DB = ConnectDB()
cursor = DB.cursor()
AttendObj = Attendance(cursor)
result = AttendObj.get_avalible_classes()