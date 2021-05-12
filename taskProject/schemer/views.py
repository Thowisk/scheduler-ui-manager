from django.shortcuts import render
from .models import Task
from .forms import TaskForm
from .schedulerclient import SchedulerClient
# Create your views here.

def showTasks(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        print(form.errors)
        print(form.cleaned_data)
        if form.is_valid():
            task = form.save(commit=False)
            if form.cleaned_data['option'] == 0:
                if form.cleaned_data['cyclic_on'] != None:
                    form.save(commit=True)
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
        form = TaskForm()
    return render(request, 'schemer/showTasks.html', {'tasks': Task.objects.all().order_by('time'), 'form': form,})