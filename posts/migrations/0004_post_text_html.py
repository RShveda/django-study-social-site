# Generated by Django 3.0.3 on 2020-09-16 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20200902_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='text_html',
            field=models.TextField(default=''),
        ),
    ]
