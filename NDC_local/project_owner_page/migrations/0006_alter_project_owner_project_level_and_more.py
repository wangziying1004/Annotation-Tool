# Generated by Django 4.2.11 on 2024-04-08 02:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("project_owner_page", "0005_alter_project_owner_project_level_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project_owner",
            name="project_level",
            field=models.IntegerField(default=2),
        ),
        migrations.AlterField(
            model_name="project_owner",
            name="project_max_tasks",
            field=models.IntegerField(default=10),
        ),
    ]
