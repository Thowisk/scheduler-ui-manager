import ast
from .models import Task



class TaskWaitingList:
    """
    waiting list, used to store all dependencies of each tasks and notice all tasks of an execution with its status.
    """
    dependencies = None

    def __init__(self):
        """
        creates a TaskDependencies object for all children present in the database
        """
        TaskWaitingList.dependencies = []
        [TaskWaitingList.dependencies.append(
            TaskDependencies(task.pk, ast.literal_eval(task.dependency), ast.literal_eval(task.satisfaction_pattern))) for task in
            Task.objects.all().filter(is_child=True)]

    @staticmethod
    def has_been_exec(task_id, state):
        """
        notice all TaskDependencies that an task has been executed and gives along with the id of that task, the return code
        :param task_id: the task_id that has been executed
        :param state: the task return code
        :return: None
        """
        if TaskWaitingList.dependencies is not None:
            [d.change_dependency_state(task_id, state) for d in TaskWaitingList.dependencies]


class TaskDependencies:
    """
    used to store dependencies and a satisfaction pattern,
    used to know if a task can be executed according to its dependencies.
    """

    def __init__(self, id, dependencies, satisfaction_pattern=None):
        """

        :param id: task id (task.pk)
        :param dependencies: task dependencies (task.dependencies)
        :param satisfaction_pattern: task satisfaction_pattern (task.satisfaction_patter)
        """
        self.saved_dependencies = dependencies
        if satisfaction_pattern is None:
            self.satisfaction_pattern = [(int(d), 0) for d in dependencies]
        else:
            self.satisfaction_pattern = satisfaction_pattern
        self.id = id
        self.dependencies = []
        for d in dependencies:
            self.dependencies.append((int(d), None))

    def change_dependency_state(self, id, new_state):
        """
        changes the state of the dependency related with the id parameter
        :param id: the parent id
        :param new_state: the new state
        :return: None
        """

        # TODO any return code -1

        for i in range(len(self.dependencies)):
            if self.dependencies[i][0] == id:
                self.dependencies[i] = (id, new_state)

    def is_executable(self):
        """
        :return: a boolean, True if the task is indeed executable, False otherwise
        """
        i = 0
        for d in self.dependencies:
            if d != self.satisfaction_pattern[i]:
                return False
            i += 1
        return True

    def reset_dependencies(self):
        """
        reset de dependencies, used when the task is executed to wait again for it's parent(s) to execute.
        :return: None
        """
        self.__init__(self.id, self.saved_dependencies, self.satisfaction_pattern)
