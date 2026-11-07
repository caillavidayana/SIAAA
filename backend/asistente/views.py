"""
asistente/views.py

Endpoint principal del asistente de IA del sistema SIGTA.

Ruta: POST /api/asistente/chat/
Autenticación: Token requerido (IsAuthenticated).
Body JSON: { "mensaje": "texto del usuario" }
Respuesta: { "respuesta": "texto del asistente" }

El endpoint es tolerante a fallos: si Ollama no está disponible,
devuelve un mensaje de contingencia con HTTP 200 para no
interrumpir la experiencia del usuario en el frontend.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .contexto import obtener_contexto
from .servicios import consultar_ollama


# ==============================================================
# VISTA PRINCIPAL
# ==============================================================

class ChatAsistenteView(APIView):
    """
    Recibe el mensaje del usuario, inyecta el contexto operativo
    real del sistema, consulta Ollama y retorna la respuesta.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # ----------------------------------------------------------
        # 1. Validar entrada
        # ----------------------------------------------------------
        mensaje = request.data.get("mensaje", "").strip()

        if not mensaje:
            return Response(
                {"error": "El campo 'mensaje' es requerido y no puede estar vacío."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(mensaje) > 2000:
            return Response(
                {"error": "El mensaje no puede superar los 2000 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------------
        # 2. Obtener contexto del sistema para el usuario actual
        # ----------------------------------------------------------
        try:
            contexto = obtener_contexto(request.user)
        except Exception:
            # Si falla la consulta de contexto, continúa sin él
            contexto = "Contexto del sistema no disponible en este momento."

        # ----------------------------------------------------------
        # 3. Construir el prompt completo
        # ----------------------------------------------------------
        prompt = (
            f"{contexto}\n\n"
            f"=== PREGUNTA DEL USUARIO ===\n"
            f"{mensaje}\n"
            f"=== FIN DE PREGUNTA ==="
        )

        # ----------------------------------------------------------
        # 4. Consultar Ollama
        # ----------------------------------------------------------
        respuesta = consultar_ollama(prompt)

        # ----------------------------------------------------------
        # 5. Retornar respuesta
        # ----------------------------------------------------------
        return Response(
            {"respuesta": respuesta},
            status=status.HTTP_200_OK,
        )
