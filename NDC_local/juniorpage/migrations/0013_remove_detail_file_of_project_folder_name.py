# Generated by Django 4.2.11 on 2024-05-06 14:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("juniorpage", "0012_detail_file_of_project_folder_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="detail_file_of_project",
            name="folder_name",
        ),
    ]
