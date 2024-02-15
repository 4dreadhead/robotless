# Generated by Django 4.2.10 on 2024-02-15 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_alter_fingerprint_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fingerprint',
            name='tools',
            field=models.ManyToManyField(blank=True, null=True, related_name='fingerprints', to='backend.tool'),
        ),
        migrations.AlterField(
            model_name='fingerprint',
            name='value',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
