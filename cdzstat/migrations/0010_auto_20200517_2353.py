# Generated by Django 3.0.5 on 2020-05-17 17:53
from datetime import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdzstat', '0009_auto_20200517_2323'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessiondata',
            old_name='ua',
            new_name='user_agent',
        ),
        migrations.AddField(
            model_name='useragent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.now, verbose_name='Время создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useragent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения'),
        ),
    ]
