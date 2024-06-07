from django.apps import AppConfig


class ModelApplicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "model_application"
