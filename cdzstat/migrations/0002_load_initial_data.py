import os
from pathlib import Path

from django.db import migrations
from django.core import serializers


def load_fixture_user_agent(apps, scheme_editor):
    current_path = Path().absolute()
    fixture_file = os.path.join(
        current_path,
        'cdzstat',
        'fixtures',
        'UserAgentFixture.json'
    )

    with open(fixture_file, 'rb') as fin:
        objects = serializers.deserialize('json', fin, ignorenonexistent=True)
        for obj in objects:
            obj.save()


def unload_fixture_user_agent(apps, scheme_editor):
    UserAgent = apps.get_model('cdzstat', 'UserAgent')
    UserAgent.objects.all().delete()


def load_exception_path(apps, scheme_editor):
    ExceptionPath = apps.get_model('cdzstat', 'ExceptionPath')
    ExceptionPath.objects.create(except_type='regex', path='^/admin/.*')


def unload_exception_path(apps, scheme_editor):
    ExceptionPath = apps.get_model('cdzstat', 'ExceptionPath')
    ExceptionPath.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('cdzstat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            load_fixture_user_agent,
            reverse_code=unload_fixture_user_agent
        ),
        migrations.RunPython(
            load_exception_path,
            reverse_code=unload_exception_path
        ),
    ]
