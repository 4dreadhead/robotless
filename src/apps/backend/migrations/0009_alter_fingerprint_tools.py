# Generated by Django 4.2.10 on 2024-02-15 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_alter_fingerprint_tools_alter_fingerprint_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fingerprint',
            name='tools',
            field=models.ManyToManyField(blank=True, related_name='fingerprints', to='backend.tool'),
        ),
    ]