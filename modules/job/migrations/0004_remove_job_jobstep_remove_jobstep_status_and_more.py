# Generated by Django 4.0.3 on 2022-08-22 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0003_alter_job_end_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='jobStep',
        ),
        migrations.RemoveField(
            model_name='jobstep',
            name='status',
        ),
        migrations.AddField(
            model_name='jobhistory',
            name='actual',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobhistory',
            name='status',
            field=models.IntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='jobhistory',
            name='end_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='jobhistory',
            name='start_Time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
