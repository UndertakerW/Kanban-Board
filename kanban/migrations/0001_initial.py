# Generated by Django 4.1.5 on 2023-03-21 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('color_scheme', models.IntegerField()),
                ('creator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='participant', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('taskname', models.TextField(max_length=50)),
                ('description', models.TextField(max_length=500)),
                ('creation_date', models.DateField()),
                ('due_date', models.DateField()),
                ('status', models.IntegerField()),
                ('priority', models.IntegerField()),
                ('assignee', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('register_type', models.CharField(max_length=20)),
                ('authentication_status', models.BooleanField(default=False)),
                ('profile_description', models.TextField(max_length=50, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profile_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
