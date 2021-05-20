from django import forms
from .models import Task
from django.forms.widgets import NumberInput, ClearableFileInput



class TaskForm(forms.ModelForm):

    def __init__(self, request):
        super().__init__(request)
        TaskForm.pks_choices = [(str(task.pk), str(task.pk)) for task in Task.objects.all()]

    pks_choices = [(str(task.pk), str(task.pk)) for task in Task.objects.all()]

    cyclic_choices = [
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
    ]


    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=NumberInput(attrs={'type': 'time'}))
    dependency = forms.ChoiceField(required=False, choices=pks_choices)
    label = forms.CharField(required=False)
    cyclic_on = forms.ChoiceField(required=False, choices=cyclic_choices, help_text='<br> <i> No selection will result in a single execution of that task. </i>')
    interval = forms.IntegerField(required=False)
    # file = forms.FilePathField(widget=ClearableFileInput(), path='/')
    # /!\ # possible XSS attack with ClearableFileInput widget /!\
    is_child = forms.BooleanField(label='Child task ?', required=False)

    class Meta:
        model = Task
        fields = ('is_child', 'dependency', 'file', 'date', 'time', 'label', 'cyclic_on', 'interval', 'option', )