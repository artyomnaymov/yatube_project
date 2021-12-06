# Generated by Django 2.2.16 on 2021-12-04 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_follow'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_following_author'),
        ),
        migrations.AlterModelTable(
            name='follow',
            table='follow',
        ),
    ]
