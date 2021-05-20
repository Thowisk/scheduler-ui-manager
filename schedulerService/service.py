import datetime
import rpyc
import subprocess
import os
import dao

from utils import *
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from rpyc.utils.server import ThreadedServer
from apscheduler.schedulers.background import BackgroundScheduler

DEFAULT_SERVICE_ROOT = 'C:/Users/'+ os.getlogin() + '/Documents/schedulerService/'

class SchedulerService(rpyc.Service):

    def exposed_add_job(self, **kwargs):
        try:
            if kwargs['instant_exec']:
                job = scheduler.add_job(exec_task, args=kwargs['args'], id='single_'+str(kwargs['pk']))
                return job
        except:
            cycle_param = {kwargs['cycle_on']: kwargs['interval']}
            job = scheduler.add_job(exec_task, trigger='interval', next_run_time=kwargs['next_run_time'], **cycle_param, args=kwargs['args'], id=str(kwargs['pk']) )
            print(str(job) + ' added successfully')
            return job

    def exposed_modify_job(self, job_id, **params):
        if params['dependency']:
            new_id = ''
            for job in scheduler.get_jobs():
                if str(job.id).split('_')[0] == job_id:
                    try:
                        if str(job.id).split('_')[1] == 'parentof':
                            new_id = str(job.id) + ',' + params['child_id']
                    except:
                        new_id = str(job.id) + '_parentof_' + params['child_id']
                    self.exposed_remove_job(str(job.id))
                    task = dao.TaskDao.get_task(str(job.id).split('_')[0])
                    params = {'cycle_on': task['cyclic_on'],
                              'interval': task['interval'],
                              'next_run_time': date_and_time_to_datetime(task['date'], task['time']).__str__(),
                              'args': [task['file']],
                              'pk': new_id}
                    self.exposed_add_job(**params)
        else:
            job = None
            if params['cycle_on'] not in ['seconds', 'minutes', 'hours', 'days', 'weeks']:
                job = scheduler.modify_job(job_id,  args=params['args'], id='single_' + str(job_id))
            else:
                job = scheduler.modify_job(job_id,  args=params['args'])
            print(str(job) + ' modified successfully')
            return job

    def exposed_reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args):
        cycle_param = {trigger_args['cycle_on']: trigger_args['interval']}
        job = scheduler.reschedule_job(job_id, jobstore, trigger, **cycle_param)
        return job

    def exposed_pause_job(self, job_id, jobstore=None):
        job = scheduler.pause_job(job_id, jobstore)
        return job

    def exposed_resume_job(self, job_id, jobstore=None):
        job = scheduler.resume_job(job_id, jobstore)
        return job

    def exposed_remove_job(self, job_id, jobstore=None):
       job = scheduler.remove_job(job_id, jobstore)
       return job

    def exposed_get_job(self, job_id):
        return scheduler.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)

def exec_task(to_exec):
    res = 2 # file not found default return code
    file_extension = to_exec.split('/')[-1].split('.')[-1]
    if file_extension == 'py':
        res = subprocess.run('python ' + to_exec)
    elif file_extension == 'bat':
        res = subprocess.run(to_exec)
    return {'script': to_exec, 'result': res}

def log(task_id, task_info):
    with open(DEFAULT_SERVICE_ROOT + 'logs/LOG', 'a') as file:
        file.write('[' + datetime.now().__str__() + '] {task_id: ' + str(task_id) + ', return_code: ' + str(task_info['result'].returncode) + ', script: ' + task_info['script'].split('/')[-1] + ' }\n')

def listener(event):
    log(str(event.job_id).split('_')[0], event.retval)
    id_parts = str(event.job_id).split('_')
    if len(id_parts) == 3:
        for child_id in str(id_parts[2]).split(','):
            child_task = dao.TaskDao.get_task(child_id)
            scheduler.add_job(exec_task, args=[child_task['file']], id=str(child_task['id']))

if __name__ == '__main__':
    scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': '100'})
    scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()
    protocol_config = {'allow_public_attrs': True, 'allow_all_attrs': True}
    server = ThreadedServer(SchedulerService, port=42069, protocol_config=protocol_config)
    try:
        print("server started")
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()