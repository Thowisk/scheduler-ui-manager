import ast
from .models import Task


class TaskWaitingList:
    dependencies = None

    def __init__(self):
        TaskWaitingList.dependencies = []
        [TaskWaitingList.dependencies.append(TaskDependencies(task.pk, ast.literal_eval(task.dependency))) for task in Task.objects.all().filter(is_child=True)]

    @staticmethod
    def has_been_exec(task_id, state):
        if TaskWaitingList.dependencies is not None:
            [d.change_dependency_state(task_id, state) for d in TaskWaitingList.dependencies]

class TaskDependencies:
    def __init__(self, id, dependencies, satisfaction_pattern=None):
        self.saved_dependencies = dependencies
        if satisfaction_pattern is None:
            self.satisfaction_pattern = [(int(d), 0) for d in dependencies]
        else:
            self.satisfaction_pattern = satisfaction_pattern
        self.id = id
        self.dependencies = []
        for d in dependencies:
            self.dependencies.append((int(d), -1))

    def change_dependency_state(self, id, new_state):
        for i in range(len(self.dependencies)):
            if self.dependencies[i][0] == id:
                self.dependencies[i] = (id, new_state)

        # for d in self.dependencies:
        #     print(d)
        #     print(d[0] == str(id))
        #     if d[0] == str(id):
        #         d = (id, new_state)

    def is_executable(self):
        i=0
        for d in self.dependencies:
            if d != self.satisfaction_pattern[i]:
                return False
            i+=1
        return True

    def reset_dependencies(self):
        self.__init__(self.id, self.saved_dependencies, self.satisfaction_pattern)


