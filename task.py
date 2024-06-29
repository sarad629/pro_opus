import datetime

class Task:
    def __init__ (self, title, desc, due, task_id):
        self.title = title
        self.desc = desc
        self.id = task_id
        self.date_created = datetime.datetime.now()
        self.due = due

    def serialize(self):
        return {
            "title": self.title,
            "description": self.desc,
            "id": self.id,
            "due": self.due,
        }