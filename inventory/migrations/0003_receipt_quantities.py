# Generated by Django 3.2.6 on 2022-01-29 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20220118_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='quantities',
            field=models.CharField(default='null', max_length=500),
            preserve_default=False,
        ),
    ]
