# Generated by Django 4.2.4 on 2023-08-22 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_comment_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(max_length=1000),
        ),
    ]
