# Generated by Django 5.0.1 on 2024-02-05 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_fingerprint_kind_alter_tool_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='fingerprint',
            name='tools',
            field=models.ManyToManyField(to='backend.tool'),
        ),
    ]
