# Generated by Django 3.1.1 on 2020-09-09 09:16

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Browser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('data', models.CharField(db_index=True, max_length=128)),
                ('version', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ColorParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_depth', models.IntegerField()),
                ('pixel_depth', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ExternalReferer',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('data', models.TextField(db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('host', models.CharField(db_index=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ip', models.GenericIPAddressField(db_index=True, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('path', models.TextField(db_index=True)),
                ('host', models.ManyToManyField(to='cdzstat.Host')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScreenSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SessionData',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('key', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('browser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.browser')),
                ('color_param', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cdzstat.colorparam')),
                ('ip', models.ManyToManyField(to='cdzstat.IpAddress', verbose_name='Ip address')),
                ('screen_size', models.ManyToManyField(to='cdzstat.ScreenSize')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SystemInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('os_version', models.CharField(blank=True, max_length=64, null=True)),
                ('platform', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeZoneInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('abbr', models.CharField(max_length=8, verbose_name='abbreviation')),
                ('offset', models.FloatField()),
                ('isdst', models.BooleanField(verbose_name='Is Daylight Saving Time')),
                ('text', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='UserAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('is_bot', models.BooleanField(default=False)),
                ('data', models.TextField(db_index=True, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='WindowSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('entry_point', models.BooleanField(default=False)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('response_time', models.FloatField(blank=True, null=True)),
                ('processing_time', models.IntegerField(help_text='Measure in milliseconds. Start: domLoading End: domComplete', null=True)),
                ('loading', models.IntegerField(help_text='Measure in milliseconds. Start: responseStart, End: responseEnd', null=True)),
                ('external_referer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cdzstat.externalreferer')),
                ('host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.host')),
                ('path', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.node')),
                ('referer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referer', to='cdzstat.node')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.sessiondata')),
            ],
            options={
                'verbose_name': 'Transition',
                'verbose_name_plural': 'Transitions',
            },
        ),
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=32)),
                ('tz_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.timezoneinfo')),
            ],
        ),
        migrations.AddField(
            model_name='sessiondata',
            name='system_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.systeminfo'),
        ),
        migrations.AddField(
            model_name='sessiondata',
            name='time_zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.timezone'),
        ),
        migrations.AddField(
            model_name='sessiondata',
            name='user_agent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cdzstat.useragent', verbose_name='User-Agent'),
        ),
        migrations.AddField(
            model_name='sessiondata',
            name='user_lang',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.userlang'),
        ),
        migrations.AddField(
            model_name='sessiondata',
            name='window_size',
            field=models.ManyToManyField(to='cdzstat.WindowSize'),
        ),
        migrations.CreateModel(
            name='Adjacency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('o', models.IntegerField(verbose_name='Order')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdzstat.node')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdzstat.sessiondata')),
                ('transition', models.ManyToManyField(to='cdzstat.Transition')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
