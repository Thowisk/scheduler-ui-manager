import json
import ast
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Task
from .forms import TaskForm
from .schedulerclient import SchedulerClient
from .taskdependencies import TaskWaitingList
# Create your views here.

connected = SchedulerClient.conn is None

def showTasks(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        print(form.errors)
        print(form.cleaned_data)
        if form.is_valid():
            task = form.save(commit=False)
            if form.cleaned_data['option'] == 0:
                if form.cleaned_data['is_child'] or form.cleaned_data['cyclic_on'] != '':
                    if task.dependency != []:
                        task.satisfaction_pattern = [(parent_id, 0) for parent_id in ast.literal_eval(task.dependency)]
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
                    satisfaction_pattern=[(parent_id, 0) for parent_id in form.cleaned_data['dependency']]
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
                i+=1
            d['dependency'] = dep
        d['file'] = task.file
        data.append(d)
    data = json.dumps(data)
    print(data)
    view_on_diagram = 0
    return render(request, 'schemer/base.html', {'tasks': tasks, 'form': form, 'connected': connected, 'diagram_data': data, 'diagram_view': view_on_diagram})


def connect(request):
    if SchedulerClient.conn is None:
        try:
            SchedulerClient.start()
            TaskWaitingList()
            connected = 1
            return HttpResponse(status=200)
        except:
            connected = 'failure'
            return HttpResponse(status=500)
    else:
        SchedulerClient.shutdown()
        connected = 0
        return HttpResponse(status=201)

# http://127.0.0.1:8000/schemer/job_return?id=100&status=0|1|2

def job_return(request):
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


def diagram_data_return(request):
    info = request.POST.dict()
    if info['new'] == '1':
        new_task = Task(file=info['file'], date=info['date'], time=info['time'], label= info['label'], cyclic_on=info['cyclic_on'], interval=info['interval'])
        new_task.save()
    return HttpResponse(status=200)