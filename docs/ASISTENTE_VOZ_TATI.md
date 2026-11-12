# Tati — Asistente de voz del SIA

Tati es la asistente virtual del SIA. Se activa diciendo su nombre, como Alexa,
mientras la plataforma está abierta en el navegador.

## Requisitos

| Requisito | Detalle |
|---|---|
| Navegador | Google Chrome o Microsoft Edge (Firefox no tiene reconocimiento de voz). |
| Conexión segura | `https://` en producción. En desarrollo funciona en `http://localhost`. Por IP sin HTTPS el micrófono se bloquea. |
| Micrófono | Permiso concedido en el candado de la barra de direcciones. |
| Internet | El reconocimiento de voz del navegador y la voz colombiana (servidor) lo necesitan. |
| Backend | `pip install -r requirements.txt` (incluye `edge-tts`). |

## Uso

1. Abrir el chat (botón azul, abajo a la derecha) y pulsar el **ícono de oreja** de la cabecera.
   La preferencia queda guardada en el navegador.
2. Decir **"Oye Tati"** (o "Hola Tati", "Tati") en cualquier pantalla, aunque el chat esté cerrado.
   Suena un tono y responde: *"Hola, ¿qué necesitas?"*.
3. Hacer la pregunta. También se puede decir todo junto: *"Tati, ¿cuántos tickets tengo?"*.
4. Tras responder, escucha 7 segundos más para una pregunta de seguimiento sin repetir su nombre.
5. **Esc** o la **×** de la burbuja la callan / cancelan.

El botón de la persona hablando (junto al micrófono) inicia una **conversación continua**
sin tener que decir "Tati" en cada pregunta.

### Órdenes de voz

| Decir | Qué hace |
|---|---|
| "Describe esta pantalla" / "¿Dónde estoy?" | Lee el título, indicadores y tablas de la vista actual. |
| "Llévame a historial / tickets / informes / notificaciones…" | Abre esa opción del **menú lateral del rol** (como si se hiciera clic). Si el rol no la tiene, dice qué opciones existen. Nunca pulsa "Cerrar sesión" ni acciones como eliminar o rechazar. |
| "Repite" | Repite la última respuesta. |
| "Abre el chat" / "Cierra el chat" | Muestra u oculta la ventana. |
| "¿Qué puedes hacer?" | Explica sus funciones. |
| "Gracias, eso es todo" | Se despide y vuelve a esperar su nombre. |
| "Desactiva el asistente" | Apaga la activación por voz. |

## Cómo funciona

```
Micrófono (Web Speech API, es-BO) ─► "Tati" detectado ─► tono + saludo
        ▲                                                   │
        └──── vuelve a esperar ◄── voz de Tati ◄── respuesta ◄┘
                                     │                  │
                     /api/asistente/voz/        órdenes locales o
                     (edge-tts, es-CO Salomé;   /api/asistente/chat/
                      respaldo: voz del          (modo voz + pantalla)
                      navegador)
```

- Las respuestas de la IA llegan **por partes** (streaming, NDJSON): el chat las muestra
  mientras se escriben y Tati empieza a hablar con la primera frase completa. Si la IA
  tarda más de 2,5 s, Tati dice "Un momento, lo reviso.".
- La pantalla actual solo se envía a la IA cuando la pregunta se refiere a ella
  ("¿qué significa esta tabla?"), para que responda más rápido.
- Frontend: `frontend/src/components/AsistenteChat.vue` (motor de voz) y
  `frontend/src/utils/voz.js` (detección del nombre, órdenes, limpieza de texto,
  descripción de pantalla). Pruebas: `node --test src/utils/*.test.js`.
- Backend: `backend/asistente/voz.py` (voz colombiana con caché en memoria) y
  `backend/asistente/views.py`. Pruebas: `python manage.py test asistente --settings=config.settings_tests`.

## Configuración (variables de entorno del backend)

| Variable | Por defecto | Uso |
|---|---|---|
| `TATI_VOZ` | `es-CO-SalomeNeural` | Voz de Tati (`es-CO-GonzaloNeural` es la masculina). |
| `TATI_VELOCIDAD` | `-5%` | Velocidad de la voz (más baja = más pausada y cálida). |
| `TATI_TONO` | `-4Hz` | Tono de la voz (más bajo = más grave y suave). |
| `OLLAMA_MODEL` | `sigta-ai` | Modelo de IA (creado con `ollama create sigta-ai -f Modelfile`). Si no está, responde el motor de respaldo. |
| `OLLAMA_KEEP_ALIVE` | `2h` | Tiempo que el modelo queda cargado en memoria entre preguntas. |
| `OLLAMA_PRECALENTAR` | `1` | Al arrancar el servidor carga el modelo en segundo plano (`0` para desactivar). |
| `OLLAMA_TIMEOUT_PRIMER_TOKEN` | `15` | Segundos máximos hasta la primera palabra (chat escrito); si no llega, responde el respaldo. |
| `OLLAMA_TIMEOUT_PRIMER_TOKEN_VOZ` | `15` | Igual, para preguntas por voz. |
| `OLLAMA_MAX_TOKENS_VOZ` | `180` | Largo máximo de una respuesta hablada. |

## Rendimiento de la IA (equipo sin GPU)

- El `Modelfile` tiene ~3.700 tokens de instrucciones. La **primera** consulta tras cargar el
  modelo tarda más de un minuto en CPU; por eso el servidor lo **precalienta** al arrancar.
  Después, Ollama reutiliza ese trabajo y las respuestas empiezan en 1–4 s.
- El modelo ocupa ~2,5 GB de RAM. Con poca memoria libre todo se vuelve lento: cerrar
  programas pesados o reducir el `Modelfile` ayuda.
- Tras cambiar el `Modelfile`: `ollama create sigta-ai -f Modelfile`.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| "No tiene permiso para usar el micrófono" | Candado de la barra de direcciones → Micrófono → Permitir, y volver a pulsar la oreja. |
| "Haz clic una vez en la página para que Tati pueda hablar" | El navegador bloquea el audio hasta el primer clic tras recargar. |
| "El micrófono solo funciona con una conexión segura" | Publicar con HTTPS (`deploy/nginx/certificado.sh`) o usar `localhost`. |
| Suena con otra voz (española/mexicana) | El servidor no pudo generar la voz colombiana (sin internet o `edge-tts` desactualizado: `pip install -U edge-tts`). |
| Se activa sin querer | Alguien dijo "Tati" cerca. Apagar la oreja cuando no se use. |

## Limitaciones

- Solo escucha mientras la plataforma está abierta en una pestaña del navegador.
- `edge-tts` usa el servicio de voces de Microsoft Edge; si Microsoft lo cambia,
  hay que actualizar la librería. Mientras tanto Tati habla con la voz del navegador.
