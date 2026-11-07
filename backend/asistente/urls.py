"""
asistente/urls.py

Rutas del módulo Asistente IA.
Se registran bajo el prefijo: api/asistente/
"""

from django.urls import path
from .views import ChatAsistenteView


urlpatterns = [

    # POST /api/asistente/chat/
    path(
        "chat/",
        ChatAsistenteView.as_view(),
        name="asistente-chat",
    ),
]
