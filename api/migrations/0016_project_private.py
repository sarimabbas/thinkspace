# Generated by Django 2.0.6 on 2018-06-14 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20180613_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
