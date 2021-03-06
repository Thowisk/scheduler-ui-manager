# Generated by Django 2.2.1 on 2021-04-13 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemer', '0005_auto_20210413_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='day',
            field=models.CharField(blank=True, choices=[('monday', 'monday'), ('tuesday', 'tuesday'), ('wednesday', 'wednesday'), ('thursday', 'thursday'), ('friday', 'friday'), ('saturday', 'saturday'), ('sunday', 'sunday')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='month',
            field=models.CharField(blank=True, choices=[('january', 'january'), ('february', 'february'), ('march', 'march'), ('april', 'april'), ('may', 'may'), ('july', 'july'), ('august', 'august'), ('september', 'september'), ('october', 'october'), ('november', 'november'), ('december', 'december')], max_length=20, null=True),
        ),
    ]
