from django import forms
from .models import Task
from django.forms.widgets import NumberInput, ClearableFileInput



class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.pks_choices = [(str(task.pk), str(task.pk)) for task in Task.objects.all()]
        print(self.pks_choices)

        self.cyclic_choices = [
            ('seconds', 'seconds'),
            ('minutes', 'minutes'),
            ('hours', 'hours'),
            ('days', 'days'),
            ('weeks', 'weeks'),
        ]

        self.fields['date'] = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
        self.fields['time'] = forms.TimeField(widget=NumberInput(attrs={'type': 'time'}))
        self.fields['dependency'] = forms.MultipleChoiceField(required=False, choices=self.pks_choices, )
        self.fields['label'] = forms.CharField(required=False)
        self.fields['cyclic_on'] = forms.ChoiceField(required=False, choices=self.cyclic_choices, help_text='<br> <i> No selection will result in a single execution of that task. </i>')
        self.fields['interval'] = forms.IntegerField(required=False)
        self.fields['is_child'] = forms.BooleanField(label='Child task ?', required=False)

    class Meta:
        model = Task
        fields = ('is_child', 'dependency', 'file', 'label','date', 'time', 'cyclic_on', 'interval', 'option', )