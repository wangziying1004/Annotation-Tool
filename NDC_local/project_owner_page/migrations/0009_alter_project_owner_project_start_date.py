# Generated by Django 4.2.11 on 2024-04-22 08:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("project_owner_page", "0008_project_owner_project_level_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project_owner",
            name="project_start_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
