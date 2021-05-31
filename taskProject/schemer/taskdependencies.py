import ast
from .models import Task


class Dependencies:
    dependencies = None

    def __init__(self):
        Dependencies.dependencies = []
        [Dependencies.dependencies.append(Dependency(task.pk, ast.literal_eval(task.dependency))) for task in Task.objects.all().filter(is_child=True)]


class Dependency:
    def __init__(self, id, dependencies, satisfaction_pattern=None):
        if satisfaction_pattern is None:
            self.satisfaction_pattern = [(d, 0) for d in dependencies]
        else:
            self.satisfaction_pattern = satisfaction_pattern
        self.id = id
        self.dependencies = []
        for d in dependencies:
            self.dependencies.append((d, -1))

    def change_dependency_state(self, id, new_state):
        for d in self.dependencies:
            if d[0] == id:
                d = (id, new_state)

    def is_executable(self):
        i=0
        for d in self.dependencies:
            if d is not self.satisfaction_pattern[i]:
                return False
            i+=1
        return True
