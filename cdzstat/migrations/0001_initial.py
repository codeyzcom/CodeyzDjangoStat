# Generated by Django 3.0.5 on 2020-04-19 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('host', models.CharField(db_index=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('ip', models.GenericIPAddressField(db_index=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('path', models.TextField(db_index=True)),
                ('host', models.ManyToManyField(to='cdzstat.Host')),
            ],
        ),
        migrations.CreateModel(
            name='UserAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('is_bot', models.BooleanField(default=False)),
                ('data', models.TextField(db_index=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dt_create', models.DateTimeField(auto_now_add=True, verbose_name='Date and Time create entry')),
                ('status_code', models.IntegerField()),
                ('response_time', models.FloatField()),
                ('host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.Host')),
                ('ip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.IpAddress', verbose_name='Ip address')),
                ('path', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.Path')),
                ('ua', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cdzstat.UserAgent', verbose_name='User-Agent')),
            ],
        ),
        migrations.CreateModel(
            name='ExceptionPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('state', models.BooleanField(default=True)),
                ('except_type', models.CharField(choices=[('regex', 'By regular expression'), ('match', 'Direct match')], default='match', max_length=5)),
                ('path', models.TextField(db_index=True)),
                ('host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.Host')),
            ],
        ),
    ]
