# Generated by Django 3.0.5 on 2020-05-03 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cdzstat', '0005_auto_20200503_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalReferer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField(db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='external_referer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cdzstat.ExternalReferer'),
        ),
    ]
