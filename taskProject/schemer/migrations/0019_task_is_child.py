# Generated by Django 2.2.1 on 2021-05-19 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemer', '0018_auto_20210512_1346'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_child',
            field=models.BooleanField(default=False),
        ),
    ]
