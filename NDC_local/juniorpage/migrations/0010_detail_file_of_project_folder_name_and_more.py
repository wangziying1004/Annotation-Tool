# Generated by Django 4.2.11 on 2024-04-29 04:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("juniorpage", "0009_remove_detail_file_of_project_project_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="detail_file_of_project",
            name="folder_name",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="project_level",
            name="folder_name",
            field=models.CharField(default="", max_length=30),
        ),
    ]
