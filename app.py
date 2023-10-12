from flask import Flask, render_template, url_for, request, redirect, session
import calendar, datetime, os, database
from task import Task

app = Flask(__name__)

app.secret_key = '0{mCbO;"43:sy8~J'

if __name__ == '__main__':
    app.run()

app.before_first_request(database.user_table)
    
taskList = {} 

@app.route("/")
def home():
    return render_template("home.html")


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
                    return redirect("/tasks" + "?due=" + due, code=302)
                #https://dmitripavlutin.com/fetch-with-json/
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
        
#Replace tasklist index with due, userarray thiny to be changed to deatabase func, get_task/delete_taskl
@app.route("/api", methods=["GET", "POST", "DELETE"])
def api():
    #Need username to do api stuff, add in request get part and retreive due
    if 'username' in session:
        username = session["username"]
        taskArray = []
        
        if request.method == "GET":
            if request.content_type == "application/json": #Error occuring here
                if "due" in request.json and "username" in request.json:
                    
                    
                    task_id = request.json["id"]
                    due = request.json["due"]

                    userTaskArray = database.get_task(username, due)
                    task = database.get_task(username, due, 2)
                    print(task.id)
                    
                    for due in userTaskArray[due]:
                        for task in userTaskArray[due][task]:
                            if task_id == task.id:
                                print(task.id)
                                return task.serialize(), 200
                                
                            else:
                                taskArray.append(task.serialize()) 
                                return "Id not found, here are some tasks", 300
    
                else:
                    return "No due date inputed", 400
                
            else:
                return {"Example Task": "Example Result"}, 300
            
        elif request.method == "POST":
            if request.content_type == "application/json":
                if "title" in request.json and "desc" in request.json and "due" in request.json:
                    
                    postTask = Task(request.json["title"], request.json["desc"], request.json["due"])
                    
                    due = request.json["due"]
                    userTaskArray = database.get_task(username, due)
                    
                    if  due not in userTaskArray.index(due):
                        userTaskArray = []

                    database.create_task(request.json["title"], request.json["desc"], due, username)

                else:
                    return "Missing data", 400
                
            elif request.content_type == "application/x-www-form-urlencoded":
                print(request.form)

            else:
                return "", 400
        
        elif request.method == "DELETE":
            if request.content_type == "application/json":
                if "id" in request.json:
                    task_id = request.json["id"]

                    userTaskArray = database.get_task(username, request.json["due"])
                    
                    for dates in userTaskArray.index(due):
                        for index, task in enumerate(userTaskArray.index(due).index(dates)):
                            if task_id == task.id:
                                database.delete_task(username, id)
                                print(task_id)
                                return f"Task with an id of {task_id} deleted", 200
                        
                    return "Id not found", 400

                else:
                    return "Id missing", 400
                
            else:
                return "Only JSON API requests are permitted", 400
        
        else:
            return "Too bad", 200

    else:
        return render_template("login.html"), 300
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('pnf.html'), 404