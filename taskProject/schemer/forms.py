from django import forms
from .models import Task
from django.forms.widgets import NumberInput, ClearableFileInput



class TaskForm(forms.ModelForm):

    cyclic_choices = [
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
    ]


    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=NumberInput(attrs={'type': 'time'}))
    dependency = forms.ChoiceField(required=False)
    label = forms.CharField(required=False)
    cyclic_on = forms.ChoiceField(required=False, choices=cyclic_choices)
    interval = forms.IntegerField(required=False)
    # file = forms.FilePathField(widget=ClearableFileInput(), path='/')
    # /!\ # possible XSS attack with ClearableFileInput widget /!\

    class Meta:
        model = Task
        fields = ('dependency', 'file', 'date', 'time', 'label', 'cyclic_on', 'interval', 'option', )
        help_texts = {
            'cyclic_on': '<br> <i> No selection will result in a single execution of that task. </i>'
        }