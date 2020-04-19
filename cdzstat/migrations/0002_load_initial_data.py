import os
from pathlib import Path

from django.db import migrations
from django.core import serializers


def load_fixture(apps, scheme_editor):
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


def unload_fixture(apps, scheme_editor):
    UserAgent = apps.get_model('cdzstat', 'UserAgent')
    UserAgent.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('cdzstat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
