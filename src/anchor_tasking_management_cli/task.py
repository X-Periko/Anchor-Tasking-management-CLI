class Task:
    def __init__(self, name, description, deadline, priority):
        self.name = name
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.done = False

    def edit_task(self, description, deadline, priority):
        self.description = description
        self.deadline = deadline
        self.priority = priority
        return "Task edited with succes"

    