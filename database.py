import sqlite3
from task import Task

class Users:
    def __init__(self, username, password, display_name):
        self.username = username
        self.password = password
        self.display_name = display_name

def user_table():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY ASC,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    display_name TEXT
    )""")

    result = cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY ASC,
                    title TEXT NOT NULL,
                    description TEXT,
                    due TEXT NOT NULL,
                    user_id INT NOT NULL)""")
    
    connection.commit()

def create_user(username, password):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    result = cursor.execute ("SELECT username FROM users WHERE username = '%s' " % (username))

    if result.fetchone() is None:
        cursor.execute("""INSERT INTO users (username, password, user_id) VALUES (
                        '%s',
                        '%s',
                        NULL
                    
        ) """ % (username, password))

        connection.commit()
        return True
    
    else:
        return False

def check_user(username, password):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    result = cursor.execute("SELECT username FROM users WHERE username = '%s' AND password = '%s'" % (username, password))
    return result.fetchone() is not None

def create_task(title, description, due, username):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    result = cursor.execute("SELECT user_id FROM users WHERE username = '%s'"  % (username))

    user_id = result.fetchone()[0]

    result = cursor.execute("""
    INSERT INTO tasks (title, description, due, user_id) VALUES (
                            '%s',
                            '%s',
                            '%s',
                            '%d'
    )
    """ % (title, description, due, user_id))

    connection.commit()



def get_task (username, due):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    result = cursor.execute("SELECT user_id FROM users WHERE username = '%s'"  % (username))
    user_id = result.fetchone()[0]

    result = cursor.execute("""SELECT * FROM tasks WHERE user_id = %d AND due = '%s' """ % (user_id, due))
    
    userTaskList = result.fetchall()
    
    userTaskArray = []
    for task in userTaskList:
        taskId = task[0]
        taskTitle = task[1]
        taskDescription = task[2]
        taskDate = task[3]
        #taskUserId = task[4]
        newTask = Task(taskTitle, taskDescription, taskDate, taskId)
        userTaskArray.append(newTask)

    return userTaskArray

def get_task_by_id (username, task_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    result = cursor.execute("SELECT user_id FROM users WHERE username = '%s'"  % (username))
    user_id = result.fetchone()[0]

    result = cursor.execute("""SELECT * FROM tasks WHERE user_id = %d AND task_id = %d """ % (user_id, task_id))
    
    userTaskList = result.fetchall()
    
    userTaskArray = []
    for task in userTaskList:
        taskId = task[0]
        taskTitle = task[1]
        taskDescription = task[2]
        taskDate = task[3]
        newTask = Task(taskTitle, taskDescription, taskDate, taskId)
        userTaskArray.append(newTask)

    return userTaskArray
    
def delete_task(username, task_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    result = cursor.execute("SELECT user_id FROM users WHERE username = '%s'"  % (username))
    user_id = result.fetchone()[0]

    result = cursor.execute("DELETE FROM tasks WHERE user_id = %d AND task_id = %d " % (user_id, task_id))
    connection.commit()
