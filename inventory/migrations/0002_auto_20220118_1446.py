# Generated by Django 3.2.6 on 2022-01-18 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipt',
            name='item_qty',
        ),
        migrations.AlterField(
            model_name='receipt',
            name='date',
            field=models.DateField(),
        ),
    ]