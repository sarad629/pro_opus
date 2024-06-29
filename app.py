from flask import Flask, render_template, url_for, request, redirect, session
import gzip, os, calendar, datetime
import database
from task import Task

app = Flask(__name__)
app.secret_key = '0{mCbO;"43:sy8~J'

app.before_first_request(database.user_table)

if __name__ == '__main__':
    app.run()

taskList = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/account")
def account():
    return render_template("account.html")

def saveTasks():
    with gzip.open('saveTasks.txt', 'wt') as file:
        for date, tasks in taskList.items():
            file.write(date)
            file.write("\a")
            file.write(str((len(tasks))))
            file.write("\a")
            for task in tasks:
                idStr = str(task.id)
                file.write(idStr)
                file.write("\a")
                file.write(task.title)
                file.write("\a")
                file.write(task.desc)
                file.write("\a")
                file.write(task.due)
                file.write("\a")
                file.write("\a")

def readTask():
    global taskList
    if not os.path.isfile('saveTasks.txt'):
        return 
    with gzip.open('saveTasks.txt', 'rt') as file:
        fileString = file.read().split("\a")
        fileString.reverse()
        while True:
            try:
                date = fileString.pop()
                taskList[date] = []
                lengthTasks = int(fileString.pop())

                while lengthTasks > 0:
                    fileString.pop()
                    title = fileString.pop()
                    desc = fileString.pop()
                    due = fileString.pop()

                    newTask = Task(title, desc, due)
                    taskList[date].append(newTask)
                    fileString.pop()

                    lengthTasks = lengthTasks - 1

            except IndexError:
                break
    
@app.route("/tasks", methods=['GET','POST'])
def task():
    if 'username' in session:
        username = session["username"]

        if request.method == "POST":
            if "new-task-title" in request.form.keys():
                due = request.form['due-date']
                title = request.form['new-task-title']
                taskDesc = request.form['new-task-desc']
                if len(title) > 0:
                    database.create_task(title, taskDesc, due, username)
                    #newTask = Task(task, taskDesc, due)
                    return redirect("/tasks" + "?due=" + due, code=302)
                
                else:
                    return 'Enter text next time, <a href="/tasks">Click me to go back</a>', 400
                
            elif "to-delete-task" in request.form.keys():
                index = request.form['to-delete-task']
                due = request.form['due-date']
                if len(index) > 0:
                    index = int(index)
                    database.delete_task(username, index)
                    #Index is task id
                    return redirect("/tasks" + "?due=" + due, code=302)

                else:
                    return 'No tasks to delete, <a href="/tasks">Click me to go back</a>', 400
        else:
            due = request.args.get('due', datetime.datetime.now().strftime("%d-%m-%Y"))
            userTaskList = database.get_task(username, due)


            return render_template("tasks.html", taskList=userTaskList, enumerate=enumerate, dueDate=due)         
    
    else:
        session['loginStatus'] = "Login to create Tasks"
        return redirect("/profile", code=302)
    

@app.route("/calendar")
def calendaire():

    date = datetime.datetime.now()
    year = int(request.args.get('year', date.year))
    month = int(request.args.get('month', date.month))

    #if statement for checking if date exists in the month (if day is more than for selected months maximum date, make it is less or equal than)
    
    c = calendar.Calendar(6)
    #Represents the day, sunday

    output = """<table>
        <tr>
        <th>Sun</th>
            <th>Mon</th>
            <th>Tue</th>
            <th>Wed</th>
            <th>Thu</th>
            <th>Fri</th>
            <th>Sat</th>
        </tr>\n"""

    for t in c.itermonthdays4(year, month):
        if t[3] == 6:
            output += "\t<tr>\n"

        taskDate = f"{t[2]:02d}-{t[1]:02d}-{t[0]}"
        userTaskArray = []
        if 'username' in session:
            userTaskArray = database.get_task(session['username'], taskDate)
        
        if len(userTaskArray) > 0:
            output +="\t\t<td class=\"contains-task\">"
        else:
            output +="\t\t<td>"

        if t[1] == month:
            if t[2] < 10:
                output += "0" + str(t[2])

            else:
                output += str(t[2])
        else: 
            output += str("&nbsp;")

        output += "</td>\n"

        if t[3] == 5:
            output+= "\t</tr>\n"

    output += "\n </table>"

    monthDays = [31,28,31,30,31,30,31,31,30,31,30,31]
    currentDay = date.day

    if monthDays[month-1] < currentDay:
        currentDay = monthDays[month-1]
        if calendar.isleap(year) and month == 2:
            currentDay = 29

    return render_template("calendar.html", 
                           date=datetime.datetime.fromisoformat(f"{year}-{month:02d}-{currentDay:02d}"), 
                           monthHTMLCalendar=output)

@app.route("/profile",  methods=["GET", "POST"])
def profile():
    if 'username' in session:
        username = session["username"]
        
        if request.method == "GET":
            return render_template("profile.html", username=username)
        
        if request.method == "POST":
            if 'logout' in request.form:
                logoutStatus = request.form['logout']

                session.pop("username") 
                return redirect("/profile", code=302)

            else:
                return redirect("/profile", code=302)
    
    else:
        if request.method == "POST":
            session.pop("loginStatus", None)

            if "username-login" in request.form and "password-login" in request.form:
                username = request.form["username-login"]
                password = request.form["password-login"]

                if "new-user" in request.form:
                    #Creating new user if not exists
                    if database.create_user(username, password):
                        session['username'] = username
                        return render_template("profile.html", username=username)
                    
                    else:
                        return "User already exists", 400

                else:
                    #Logging In
                    if database.check_user(username, password):
                        session['username'] = username
                        return render_template("profile.html", username=username)

                    else:
                        return "Invalid Login", 400
 
            else:
                return "Not logged in to begin with... your problem", 400

        elif request.method == "GET": 
            return render_template("login.html")
            
        else:
            return render_template("login.html"), 400

@app.errorhandler(404)
def page_not_found(error):
    return render_template('pnf.html'), 404

#Replace tasklist index with due, userarray thiny to be changed to deatabase func, get_task/delete_taskl
@app.route("/api", methods=["GET", "POST", "DELETE"])
def api():
    #Need username to do api stuff, add in request get part and retreive due
    #Figure out why taskList is empty
    if 'username' in session:
        username = session["username"]
        
        if request.method == "GET":
            userTaskArray = []
                  
            #Could use request.args.get if we make the api more functional
            #Default
            id = int(request.args.get("id", -1, type=int))
            
            #Used if given JSON fetch info, otherwise results to the default above
            if request.headers.get('id'):
                print("got the json header for id")
                id = int(request.headers.get('id'))
                userTaskList = database.get_task_by_id(username, id)
                for task in userTaskList:
                    print(task.serialize())
                    userTaskArray.append(task.serialize())
                print("here")
                #Error
                #Second solution would be to make all the IDs a unique string
                return redirect("/ap?id=%d" % id, code=302)
            
            if request.headers.get('due'):
                print("got the json header for due")
                due = request.headers.get('due')
                userTaskList = database.get_task(username, due)
                for task in userTaskList:
                    print(task.due)
                print(due)   
                
            #Needs to pull information from taskList but its empty :/
            """for dates in taskList.keys():
                print("got date")
                for task in taskList[dates]:
                    print("got tasks")
                    if id == task.id and due == task.due:
                        print(task.serializ())
                        return task.serialize(), 200
                    elif id == task.id:
                        print(task.serializ())
                        return task.serialize(), 200
                    elif due == task.due:
                        print(task.serializ())
                        return task.serialize(),200
                    else:
                        #Just prints all the tasks with that due date
                        userTaskArray.append(task.serialize()) """

            if id == -1:
                return {"tronald dump and boe jiden": userTaskArray}, 200
            
            else:
                return "Id not found/doesn't exist", 404 
        
        elif request.method == "POST":
            if request.content_type == "application/json":
                if "title" in request.json and "desc" in request.json and "due" in request.json:
                    postTask = Task(request.json["title"], request.json["desc"], request.json["due"])
                    
                    due = request.json["due"]
                    if  due not in taskList:
                        taskList[due] = []
                    taskList[due].insert(0, postTask)
                    saveTasks()

                else:
                    return "Missing data", 400
                
            elif request.content_type == "application/x-www-form-urlencoded":
                print(request.form)

            else:
                return "", 400
            
            return "", 200
        
        elif request.method == "DELETE":
            if request.content_type == "application/json":
                if "id" in request.json:
                    id = request.json["id"]

                    for dates in taskList.keys():
                        for index, task in enumerate(taskList[dates]):
                            if id == task.id:
                                taskList[dates].pop(index)
                                print() 
                                saveTasks()
                                return f"Task with an id of {id} deleted", 200
                        
                    return "Id not found", 400

                else:
                    return "Id missing", 400
                
            else:
                return "No you can't", 400
        
        else:
            return "too bad", 200

    else:
        return render_template("login.html"), 400