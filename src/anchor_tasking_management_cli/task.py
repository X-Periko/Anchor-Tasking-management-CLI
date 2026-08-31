class Task:
    def __init__(self, name, description, deadline, priority):
        self.name = name
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.done = False