import json
import ast
from django.shortcuts import render
from django.http import HttpResponse
from .models import Task
from .forms import TaskForm
from .schedulerclient import SchedulerClient
from .taskdependencies import TaskWaitingList


def show_tasks(request):
    """
    :param request contains the form
    returns the main page with the form from the tab listing the tasks.
    gives the template information about :
        - existing tasks 'tasks'
        - the form 'form'
        - service connection status 'connected'
        - a json like object with the necessary information to build the network diagram 'diagram_data'
        -
    """
    if request.method == "POST":
        form = TaskForm(request.POST)
        print(form.errors)
        print(form.cleaned_data)
        if form.is_valid():
            task = form.save(commit=False)
            if form.cleaned_data['option'] == 0:
                if form.cleaned_data['is_child'] or form.cleaned_data['cyclic_on'] != '':
                    if task.dependency != []:
                        task.satisfaction_pattern = [(int(parent_id), 0) for parent_id in ast.literal_eval(task.dependency)]
                    else:
                        task.satisfaction_pattern = []
                    task.save()
                elif form.cleaned_data['cyclic_on'] == '':
                    SchedulerClient.add_job(task)
            elif form.cleaned_data['option'] < 0:
                Task.objects.filter(pk=form.cleaned_data['option'] * -1).delete()
                SchedulerClient.remove_job(form.cleaned_data['option'] * -1)
            else:
                Task.objects.filter(pk=form.cleaned_data['option']).update(
                    file=form.cleaned_data['file'],
                    date=form.cleaned_data['date'],
                    time=form.cleaned_data['time'],
                    label=form.cleaned_data['label'],
                    cyclic_on=form.cleaned_data['cyclic_on'],
                    interval=form.cleaned_data['interval'],
                    dependency=form.cleaned_data['dependency'],
                    satisfaction_pattern=[(int(parent_id), 0) for parent_id in form.cleaned_data['dependency']]
                )
    form = TaskForm()
    tasks = Task.objects.all().order_by('time')
    data = []
    for task in tasks:
        d = {}
        d['id'] = task.pk
        d['label'] = task.pk
        if task.satisfaction_pattern is None:
            dep = []
            dependency_list = ast.literal_eval(task.dependency)
            for dd in dependency_list:
                dep.append({'parent': dd, 'val': 0})
            d['dependency'] = dep
        else:
            dep = []
            dependency_list = ast.literal_eval(task.dependency)
            satisfaction_pattern_list = ast.literal_eval(task.satisfaction_pattern)
            i = 0
            for dd in dependency_list:
                dep.append({'parent': dd, 'val': satisfaction_pattern_list[i][1]})
                i += 1
            d['dependency'] = dep
        d['file'] = task.file
        data.append(d)
    data = json.dumps(data)
    # print(data)
    view_on_diagram = 0
    return render(request, 'schemer/base.html',
                  {'tasks': tasks, 'form': form, 'connected': int(SchedulerClient.conn is not None),
                   'diagram_data': data})


def connect(request):
    """
    GET route with no arguments, used as a trigger.
    starts or shuts down the service executing the tasks.
    return to the client a code about the connection status with the service executing the tasks.
    """
    if SchedulerClient.conn is None:
        try:
            SchedulerClient.start()
            TaskWaitingList()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)
    else:
        SchedulerClient.shutdown()
        return HttpResponse(status=201)


def job_return(request):
    """
    route GET with the job id 'id' which has been executed and it's return code 'state'.
    alter the TaskDependencies object linked to the children of the task which has been executed and check if any child can
    be executed, if so the TaskDependencies object is reset
    :param request: 'id', 'state"
    """
    if TaskWaitingList.dependencies == None:
        TaskWaitingList()
    task_id = int(request.GET.get('id', None))
    state = int(request.GET.get('state', None))
    Task.objects.filter(pk=task_id).update(state=state)
    all_entries = Task.objects.all()
    TaskWaitingList.has_been_exec(task_id, state)
    for task in TaskWaitingList.dependencies:
        if task.is_executable():
            for task_to_exec in all_entries:
                if task_to_exec.pk == task.id:
                    SchedulerClient.add_job(task_to_exec, child=True)
                task.reset_dependencies()
    return HttpResponse(status=200)


def diagram_new_task(request):
    """
    route POST that creates a new task from the diagram tab,
    :param request: takes a 'file', 'date', 'time', 'label', 'cyclic_on' and an 'interval' parameter.
    """
    info = request.POST.dict()
    new_task = Task(file=info['file'], date=info['date'], time=info['time'], label=info['label'],
                    cyclic_on=info['cyclic_on'], interval=info['interval'])
    new_task.save()
    return HttpResponse(status=200)


def diagram_remove_task(request):
    """
    route DELETE that removes a task,
    :param request: takes one argument 'id', the task id.
    """
    info = request.POST.dict()
    tasks = Task.objects.all()
    for task in tasks:
        if task.pk == int(info['id']):
            task.delete()
            break
    return HttpResponse(status=200)


def diagram_new_dependency(request):
    """
    route POST that creates a dependency to a non-child or child task,
    :param request: takes 2 arguments 'from' the parent id, and 'to' the child id.
    """
    info = request.POST.dict()
    tasks = Task.objects.all()
    for task in tasks:
        if task.pk == int(info['to']):
            dep_list = ast.literal_eval(task.dependency)
            dep_list.append(int(info['from']))
            task.dependency = str(dep_list)
            satis_pat_list = ast.literal_eval(task.satisfaction_pattern)
            satis_pat_list.append((int(info['from']), 0))
            task.satisfaction_pattern = str(satis_pat_list)
            task.is_child = True
            task.save()
            break
    return HttpResponse(status=200)


def diagram_edit_dependency(request):
    """
    route PUT that edits an existing dependency by changing the wished return code,
    :param request: takes 2 parameters, a string 'id' representing the dependency like 'from->to' and the wished
    return code 'returncode'
    """
    tasks = Task.objects.all()
    info = request.POST.dict()
    dependency = info['id']
    from_, to = dependency.split('->')
    for task in tasks:
        if task.pk == int(to):
            satis_pattern_list = ast.literal_eval(task.satisfaction_pattern)
            for val in satis_pattern_list:
                if int(from_) in val:
                    if info['returncode'] == 'Any':
                        satis_pattern_list[satis_pattern_list.index(val)] = (int(from_), -1)
                    else:
                        satis_pattern_list[satis_pattern_list.index(val)] = (int(from_), int(info['returncode']))
                    task.satisfaction_pattern = satis_pattern_list
                    task.save()
                    break
            break
    return HttpResponse(status=200)


def diagram_remove_dependencies(request):
    """
    route DELETE that removes at least one dependency to a child task,
    :param request: takes n parameters, n being the number of dependencies being deleted and the value is the id of
    the dependency like 'from->to'.
    example:    '0=101->102
                &1=102->103
                &2=103->104'
    """
    tasks = Task.objects.all()
    info = request.POST.dict()
    for key in info:
        from_, to = info[key].split('->')
        for task in tasks:
            if task.pk == int(to):
                dep_list = ast.literal_eval(task.dependency)
                satis_pattern_list = ast.literal_eval(task.satisfaction_pattern)
                dep_list.remove(int(from_))
                for val in satis_pattern_list:
                    if from_ in val:
                        satis_pattern_list.remove(val)
                task.dependency = dep_list
                task.satisfaction_pattern = satis_pattern_list
                if len(dep_list) == 0:
                    task.is_child = False
                task.save()
                break
    return HttpResponse(status=200)
