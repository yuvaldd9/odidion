"""
handle the server database

users:
first name | last name | username | password(hashed) | ip | setting(formated)

"""
import sqlite3 as lite
import os
def create_dataBase(conn, create_cmd):
    """
    creates the table in the db file
    """
    if conn:
        cursor = conn.cursor()
        cursor.execute(create_cmd)
        conn.commit()
        #print '[sql management] Table Created...'
def connect_dataBase(db_dir, create_cmd):

    """
    returns the connection object
    """
    just_created = False #flag of is the db is already exist
    
    if not os.path.isfile(db_dir):
        #create the db file in the directory
        with open(db_dir , 'w') as f:
            just_created = True
            #print 'database handler created -- ' , db_dir  

    try:
        conn = lite.connect(db_dir)
    except lite.Error, e:
        #print "Error %s:" % db_dir
        sys.exit(1)
    finally:
        if just_created:
            #create the table 
            create_dataBase(conn, create_cmd)
        return True
def get_data(db_dir, command, args = None):
    """
    return fecthall from the database according to the 
    """
    with lite.connect((db_dir)) as conn:
        try:
            cursor = conn.cursor()
            if args:
                cursor.execute(command,args)
            else:
                cursor.execute(command)
                data = cursor.fetchall()
                #print '[sql management] got all of the data requested according to:\n--- %s ---\n the data: %s'%(command, data)
                return data
        except:
            return None
    
def set_data(db_dir, command, args = None):
    """
    change, deleted, inserted the data according the command
    """
    #print command
    with lite.connect((db_dir)) as conn:
        #try:
            cursor = conn.cursor()
            if args:
                cursor.execute(command,args)
            else:
                cursor.execute(command)
            conn.commit()
            #print '[sql management] set successfully the data according to:\n--- %s ---'%(command )
            return True
        #except:
            return False
    return False

def check_if_value_exist(db_dir, table_name,row, value):
    print '------------CHECKIG EXISTECE_______'
    #try:
    cmd = """SELECT %s FROM %s  WHERE %s = \'%s\'"""%(row, table_name, row, value)
    print cmd
    with lite.connect((db_dir)) as conn:
        cursor = conn.cursor()
        cursor.execute(cmd)
        result = cursor.fetchone()
        print result
        if result:
            return True
        return False
    #except:    
    #    return False