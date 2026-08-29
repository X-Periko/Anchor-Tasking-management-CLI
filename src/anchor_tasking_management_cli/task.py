class Task:
    def __init__(self, description, deadline, priority):
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.donde = False

    def edit_task(self, description, deadline, priority):
        self.description = description
        self.deadline = deadline
        self.priority = priority
        return "Task edited with succes"

    