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
import json

from django.http import HttpResponse, StreamingHttpResponse

from . import voz
from .contexto import obtener_contexto
from .servicios import INSTRUCCION_IDENTIDAD, consultar_ollama, consultar_ollama_stream


# ==============================================================
# VISTA PRINCIPAL
# ==============================================================

MAX_PANTALLA = 1500

INSTRUCCION_VOZ = (
    "=== FORMATO DE RESPUESTA (MODO VOZ) ===\n"
    "Tu respuesta se leerá en voz alta. Responde en máximo tres frases cortas y directas, "
    "sin emojis, sin listas, sin viñetas, sin asteriscos ni formato markdown. "
    "Di los números con claridad y no repitas la pregunta."
)

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
        es_voz = str(request.data.get("modo", "")).strip().lower() == "voz"
        pantalla = str(request.data.get("pantalla", "") or "").strip()[:MAX_PANTALLA]

        bloque_pregunta = (
            f"=== PREGUNTA DEL USUARIO ===\n"
            f"{mensaje}\n"
            f"=== FIN DE PREGUNTA ==="
        )
        # Prompt original: lo usa el motor de respaldo (búsqueda por palabras clave),
        # sin instrucciones extra que puedan desviar la detección del tema.
        prompt = f"{contexto}\n\n{bloque_pregunta}"

        # Prompt para la IA: identidad de Tati, pantalla actual y estilo hablado.
        # Orden pensado para la caché de Ollama: lo que casi no cambia va primero
        # (identidad, estilo, contexto); lo que cambia en cada pregunta, al final.
        partes = [INSTRUCCION_IDENTIDAD]
        if es_voz:
            partes.append(INSTRUCCION_VOZ)
        partes.append(contexto)
        if pantalla:
            partes.append(
                "=== PANTALLA QUE EL USUARIO ESTÁ VIENDO ===\n"
                f"{pantalla}\n"
                "=== FIN PANTALLA ==="
            )
        partes.append(bloque_pregunta)
        prompt_ia = "\n\n".join(partes)

        # ----------------------------------------------------------
        # 4. Consultar Ollama
        # ----------------------------------------------------------
        if request.data.get("stream"):
            return self._responder_por_partes(prompt_ia, prompt, es_voz)

        respuesta = consultar_ollama(prompt_ia, prompt_respaldo=prompt, voz=es_voz)

        # ----------------------------------------------------------
        # 5. Retornar respuesta
        # ----------------------------------------------------------
        return Response(
            {"respuesta": respuesta},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _responder_por_partes(prompt_ia, prompt_respaldo, es_voz):
        """
        Respuesta en NDJSON (una línea JSON por trozo):
            {"delta": "texto parcial"} ... {"fin": true, "respuesta": "texto completo"}
        """
        def generar():
            partes = []
            for trozo in consultar_ollama_stream(prompt_ia, prompt_respaldo=prompt_respaldo, voz=es_voz):
                partes.append(trozo)
                yield json.dumps({"delta": trozo}, ensure_ascii=False) + "\n"
            yield json.dumps({"fin": True, "respuesta": "".join(partes).strip()}, ensure_ascii=False) + "\n"

        respuesta = StreamingHttpResponse(generar(), content_type="application/x-ndjson; charset=utf-8")
        respuesta["Cache-Control"] = "no-cache"
        respuesta["X-Accel-Buffering"] = "no"  # nginx: enviar cada trozo sin acumular
        return respuesta


# ==============================================================
# VOZ DE TATI (texto → audio MP3, voz colombiana)
# ==============================================================

class VozTatiView(APIView):
    """
    POST /api/asistente/voz/
    Body JSON: { "texto": "frase a leer" }
    Respuesta: audio/mpeg  ·  503 si el servicio de voz no está disponible
    (el frontend usa entonces la voz del navegador).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        texto = str(request.data.get("texto", "")).strip()
        if not texto:
            return Response({"error": "El campo 'texto' es requerido."}, status=status.HTTP_400_BAD_REQUEST)
        if len(texto) > voz.MAX_CARACTERES:
            return Response(
                {"error": f"El texto no puede superar los {voz.MAX_CARACTERES} caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            audio = voz.sintetizar(texto)
        except voz.VozNoDisponible:
            return Response(
                {"error": "La voz de Tati no está disponible en este momento."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        respuesta = HttpResponse(audio, content_type="audio/mpeg")
        respuesta["Cache-Control"] = "private, max-age=86400"
        return respuesta
