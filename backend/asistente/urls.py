"""
asistente/urls.py

Rutas del módulo Asistente IA.
Se registran bajo el prefijo: api/asistente/
"""

from django.urls import path
from .views import ChatAsistenteView, VozTatiView


urlpatterns = [

    # POST /api/asistente/chat/
    path(
        "chat/",
        ChatAsistenteView.as_view(),
        name="asistente-chat",
    ),

    # POST /api/asistente/voz/  (voz colombiana de Tati)
    path(
        "voz/",
        VozTatiView.as_view(),
        name="asistente-voz",
    ),
]
