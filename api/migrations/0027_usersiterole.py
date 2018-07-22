# Generated by Django 2.0.7 on 2018-07-19 13:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20180614_2144'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSiteRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.TextField()),
                ('users', models.ManyToManyField(related_name='site_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
