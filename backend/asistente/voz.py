"""
asistente/voz.py

Síntesis de voz de "Tati" (voz colombiana) mediante edge-tts.

edge-tts usa el servicio de voces neuronales de Microsoft Edge (requiere
internet en el servidor). Si falla, el endpoint responde 503 y el frontend
usa la voz del navegador como respaldo, así la asistente nunca queda muda.

Variables de entorno opcionales:
    TATI_VOZ        Voz a usar (por defecto es-CO-SalomeNeural).
    TATI_VELOCIDAD  Ajuste de velocidad, p. ej. "+4%" o "-5%".
    TATI_TONO       Ajuste de tono, p. ej. "+0Hz".
"""

import asyncio
import hashlib
import os
import re
import threading
from collections import OrderedDict

VOZ = os.getenv("TATI_VOZ", "es-CO-SalomeNeural")
VELOCIDAD = os.getenv("TATI_VELOCIDAD", "-5%")   # un poco más pausada: más cálida
TONO = os.getenv("TATI_TONO", "-4Hz")          # un poco más grave: más suave y envolvente
TIMEOUT_SEGUNDOS = 15
MAX_CARACTERES = 600          # el frontend envía frase por frase
MAX_CACHE = 300               # frases en memoria (saludos, avisos frecuentes)

_RE_VELOCIDAD = re.compile(r"^[+-]\d{1,2}%$")
_RE_TONO = re.compile(r"^[+-]\d{1,3}Hz$")

_cache: "OrderedDict[str, bytes]" = OrderedDict()
_cache_lock = threading.Lock()


class VozNoDisponible(Exception):
    """El servicio de voz no respondió o no está instalado."""


def _clave(texto: str) -> str:
    return hashlib.sha256(f"{VOZ}|{VELOCIDAD}|{TONO}|{texto}".encode("utf-8")).hexdigest()


async def _generar(texto: str) -> bytes:
    import edge_tts  # import diferido: el resto del sistema funciona aunque no esté instalado

    velocidad = VELOCIDAD if _RE_VELOCIDAD.match(VELOCIDAD) else "+0%"
    tono = TONO if _RE_TONO.match(TONO) else "+0Hz"
    comunicador = edge_tts.Communicate(texto, VOZ, rate=velocidad, pitch=tono)
    partes = []
    async for trozo in comunicador.stream():
        if trozo.get("type") == "audio":
            partes.append(trozo["data"])
    return b"".join(partes)


def sintetizar(texto: str) -> bytes:
    """
    Devuelve el audio MP3 del texto con la voz de Tati.
    Lanza VozNoDisponible si no se pudo generar.
    """
    texto = (texto or "").strip()[:MAX_CARACTERES]
    if not texto:
        raise ValueError("Texto vacío")

    clave = _clave(texto)
    with _cache_lock:
        if clave in _cache:
            _cache.move_to_end(clave)
            return _cache[clave]

    try:
        audio = asyncio.run(asyncio.wait_for(_generar(texto), TIMEOUT_SEGUNDOS))
    except Exception as exc:  # red caída, servicio cambiado, librería ausente…
        raise VozNoDisponible(str(exc)) from exc

    if not audio:
        raise VozNoDisponible("El servicio de voz no devolvió audio.")

    with _cache_lock:
        _cache[clave] = audio
        while len(_cache) > MAX_CACHE:
            _cache.popitem(last=False)
    return audio
