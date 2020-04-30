# Generated by Django 3.0.5 on 2020-04-30 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Browser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(db_index=True, max_length=128)),
                ('version', models.CharField(max_length=32)),
            ],
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
            name='Platform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=32)),
            ],
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
            name='SystemInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('os_version', models.CharField(max_length=64)),
                ('platform', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=32)),
            ],
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
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('is_bot', models.BooleanField(default=False)),
                ('data', models.TextField(db_index=True, unique=True)),
            ],
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
            name='UserParam',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('browser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.Browser')),
                ('color_param', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.ColorParam')),
                ('screen_size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.ScreenSize')),
                ('system_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.SystemInfo')),
                ('time_zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.TimeZone')),
                ('user_lang', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.UserLang')),
                ('window_size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.WindowSize')),
            ],
        ),
        migrations.AddField(
            model_name='timezone',
            name='tz_info',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cdzstat.TimeZoneInfo'),
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
