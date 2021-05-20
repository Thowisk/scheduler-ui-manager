# Generated by Django 2.2.1 on 2021-04-28 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemer', '0011_auto_20210419_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='file',
            field=models.FilePathField(default=None, path=None),
        ),
        migrations.AlterField(
            model_name='task',
            name='cyclic_on',
            field=models.CharField(blank=True, choices=[('seconds', 'seconds'), ('minutes', 'minutes'), ('hours', 'hours'), ('days', 'days'), ('weeks', 'weeks')], max_length=10, null=True),
        ),
    ]