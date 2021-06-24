import rpyc
from .models import Task
from .utils import *
from .taskdependencies import TaskWaitingList


class SchedulerClient:
    conn = None

    @staticmethod
    def start():
        """
        connects to an rpyc service and gives all the non-child tasks to this service
        :return:
        """
        SchedulerClient.conn = rpyc.connect('localhost', 42069,
                                            config={'allow_public_attrs': True, 'allow_all_attrs': True})
        all_entries = Task.objects.all().order_by('pk').filter(is_child=False)
        for task in all_entries:
            SchedulerClient.add_job(task)
        TaskWaitingList()

    @staticmethod
    def shutdown():
        """
        clears the service and disconnects
        :return:
        """
        SchedulerClient.conn.root.clean_scheduler()
        SchedulerClient.conn = None

    @staticmethod
    def add_job(task, child=False):
        """
        adds a task to the service
        :param task: the task object in django ORM
        :param child: ?
        :return:
        """
        if not child:
            if task.cyclic_on in ['seconds', 'minutes', 'hours', 'days', 'weeks']:
                params = {'cycle_on': task.cyclic_on,
                            'interval': task.interval,
                            'next_run_time': date_and_time_to_datetime(task.date, task.time).__str__(),
                            'args': [task.file],
                            'pk': task.pk
                            }
                SchedulerClient.conn.root.add_job(**params)
        else:
            params = {'instant_exec': True, 'args': [task.file], 'pk': task.pk}
            SchedulerClient.conn.root.add_job(**params)

    @staticmethod
    def update(job_id, new_task):
        """
        gonna be deleted unused
        :param job_id:
        :param new_task:
        :return:
        """
        params = {'cycle_on': new_task.cyclic_on,
                  'interval': new_task.interval,
                  'next_run_time': date_and_time_to_datetime(new_task.date, new_task.time).__str__(),
                  'args': [new_task.file],
                  }
        SchedulerClient.conn.root.pause_job(str(job_id))
        SchedulerClient.conn.root.modify_job(str(job_id), **params)
        if params['cycle_on'] != None:
            SchedulerClient.conn.root.reschedule_job(str(job_id), jobstore=None, trigger='interval', **params)
        SchedulerClient.conn.root.resume_job(str(job_id))

    @staticmethod
    def remove_job(job_id):
        """
        removes a task from the service
        :param job_id: the task id
        :return:
        """
        try:
            SchedulerClient.conn.root.remove_job(str(job_id))
        except:
            print(' /!\\ Couldn\'t get a connection to the scheduler service /!\\')



class SchedulerService(rpyc.Service):

    def exposed_add_job(self, *args ,**kwargs):
        return scheduler.add_job(*args, **kwargs)

    def exposed_remove_job(self, *args, **kwargs):
        return scheduler.remove_job(*args, **kwargs)

    ...

