# Generated by Django 5.0.1 on 2024-02-05 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_fingerprint_tools'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tool',
            name='fingerprints',
        ),
        migrations.AlterField(
            model_name='fingerprint',
            name='tools',
            field=models.ManyToManyField(related_name='fingerprints', to='backend.tool'),
        ),
    ]
