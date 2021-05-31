from django.shortcuts import render
from django.http import HttpResponse
from .models import Task
from .forms import TaskForm
from .schedulerclient import SchedulerClient
from .taskdependencies import TaskWaitingList, TaskDependencies
# Create your views here.

def showTasks(request, connected=False):
    if request.method == "POST":
        form = TaskForm(request.POST)
        print(form.errors)
        print(form.cleaned_data)
        if form.is_valid():
            task = form.save(commit=False)
            if form.cleaned_data['option'] == 0:
                if form.cleaned_data['is_child'] or form.cleaned_data['cyclic_on'] != '':
                    form.save(commit=True)
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
                    interval=form.cleaned_data['interval']
                )
                SchedulerClient.update(form.cleaned_data['option'], task)
    else:
        form = TaskForm(None) # a bit sketchy
    return render(request, 'schemer/showTasks.html', {'tasks': Task.objects.all().order_by('time'), 'form': form, 'connected': connected})


def connect(request):
    connected = False
    if SchedulerClient.conn is None:
        try:
            SchedulerClient.start()
            TaskWaitingList()
            connected = True
        except:
            connected = 'failure'
    else:
        SchedulerClient.shutdown()
    return showTasks(request, connected=connected)

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
                    print("yes")
                task.reset_dependencies()
    return HttpResponse(status=200)