import rpyc
from .models import Task
from .utils import *


class SchedulerClient:
    conn = None

    @staticmethod
    def start():
        SchedulerClient.conn = rpyc.connect('localhost', 42069,
                                            config={'allow_public_attrs': True, 'allow_all_attrs': True})
        all_entries = Task.objects.all()
        for task in all_entries:
            SchedulerClient.add_job(task)

    @staticmethod
    def add_job(task):
        try:
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
        except:
            print(' /!\\ Couldn\'t get a connection to the scheduler service /!\\')

    @staticmethod
    def update(job_id, new_task):
        try:
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
        except:
            print(' /!\\ Couldn\'t get a connection to the scheduler service /!\\')

    @staticmethod
    def remove_job(job_id):
        try:
            SchedulerClient.conn.root.remove_job(str(job_id))
        except:
            print(' /!\\ Couldn\'t get a connection to the scheduler service /!\\')