# Generated by Django 3.1.1 on 2021-02-25 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offender', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mcs_blocked_user',
            name='mcs_blocked_user_dob',
            field=models.CharField(max_length=200),
        ),
    ]
