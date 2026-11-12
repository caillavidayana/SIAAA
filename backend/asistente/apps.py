from django.apps import AppConfig


class AsistenteConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"
    name = "asistente"
    verbose_name = "Asistente IA"

    def ready(self):
        # Carga el modelo de IA en segundo plano al arrancar el servidor
        # (no se ejecuta en migraciones ni en pruebas).
        from .servicios import precalentar_en_segundo_plano

        precalentar_en_segundo_plano()
