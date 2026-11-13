# Revisión del frontend de SIA-AI

Base: `mejora-frontend-sia-ai`, commit `47f036a0e4b580ea160b5731caf796b47fcce833`.
Rama de trabajo: `mejora/chat-tarjetas-accesibilidad`.

## MODIFICACION1 — Chat y estados

Se conserva AsistenteChat.vue y el motor de Tati. Se ajustan cabecera, burbujas,
tipografía y distribución. Los tres puntos se muestran desde el envío hasta el
primer contenido. Durante el streaming aparece «Recibiendo respuesta» y se
mantiene bloqueado otro envío hasta terminar. `finally` limpia la espera tanto
en éxito como en error o cancelación. Se conserva el escape de HTML y los saltos
de línea existentes; las cadenas largas se ajustan al ancho.

## MODIFICACION2 — Resultados estructurados

El backend actual entrega `{respuesta}` o NDJSON con `{delta}` y
`{fin, respuesta}`. **No entrega registros estructurados**. Por ello las
respuestas actuales siguen en texto y no se generan tarjetas a partir de su
contenido, aunque mencione solicitudes, códigos, estados o responsables.

La presentación admite, de forma opcional, colecciones explícitas de nivel
superior `solicitudes`, `tickets` y `equipos` en la respuesta JSON o el evento
`fin`. No se cambia la petición ni se exige modificar el contrato actual.
Cada objeto puede proporcionar `identificador`, `codigo` o `id`; `descripcion`,
`asunto` o `nombre`; y `estado`, `responsable` (texto) y `fecha` (texto).
Los objetos anidados ambiguos se omiten. No se inventa un responsable ni una
fecha. Se conserva la fecha recibida sin interpretar su zona horaria.

Pendiente, En proceso (`en_proceso` también) y Resuelto tienen etiquetas y
colores; los demás estados conservan el texto original con estilo neutro.
La incorporación de datos reales desde Django requeriría otra tarea de backend.

## MODIFICACION3 — Accesibilidad y adaptación

Controles de voz y envío etiquetados, estados pulsados, foco visible,
retorno de foco al minimizar/cerrar, entrada con ayuda asociada y región de
historial navegable por teclado. Los anuncios de estado son independientes de
los fragmentos de streaming. Se respeta la preferencia de movimiento reducido.
En móvil, la entrada ocupa una fila completa y los botones tienen 44 px.
Minimizar conserva el historial y la activación por nombre; cerrar también
cancela la conversación en curso usando la función existente de Tati.

## Validación ejecutada

- `cd frontend && npm run build`: correcto; advertencia de tamaño de chunks
  también presente en la compilación previa al trabajo de esta sesión.
- `node --test frontend/src/utils/*.test.js`: 23 pruebas correctas, incluidas
  14 de voz sin modificar y 6 de resultados estructurados.
- Chromium real, componente montado con Vue Router en una página aislada:
  espera y tres puntos, JSON, texto largo, ausencia de tarjetas para texto,
  anchos 320/375/768 px y escritorio, foco al minimizar, conservación de mensajes,
  error HTTP, NDJSON, respuesta final y tarjeta explícita sin campos ausentes.
  Las respuestas de estas comprobaciones fueron simuladas, nunca registros reales.
- Sin errores JavaScript en las comprobaciones de navegador.
- `git diff --check` y comparación con la base de backend, Modelfile,
  `voz.js` y `voz.test.js`: sin cambios en los archivos protegidos.

El navegador de pruebas y sus capturas están fuera del checkout, en
`/workspace/siaaa-local/`; no añaden dependencias al proyecto.

## Demostración al ingeniero

1. Iniciar Django y Vite según README; autenticarse y abrir Tati.
2. Enviar una consulta con la red ralentizada: observar los puntos de espera,
   el estado al llegar el primer fragmento y el bloqueo de envío hasta el final.
   Una respuesta larga debe permitir desplazamiento sin desbordamiento lateral.
3. Simular una respuesta HTTP 500 al endpoint de chat usando herramientas de
   prueba del navegador: comprobar mensaje de error y desaparición de los puntos.
4. Usar Tab y Shift+Tab para recorrer los controles; minimizar y reabrir para
   comprobar foco e historial. Probar anchos 320 y 375 px y expandir/reducir.
5. Para las tarjetas, usar únicamente una respuesta interceptada de prueba con
   una colección explícita `tickets`, cuyos objetos tengan `estado` Pendiente,
   En proceso y Resuelto. Identificarla como simulación. Comprobar campos ausentes
   y una respuesta normal de texto, que no debe producir tarjetas.
6. En Chrome/Edge con permiso de micrófono, probar «Oye Tati», dictado,
   conversación continua, Esc, interrupción y «Escuchar». Las pruebas unitarias
   cubren activación, órdenes, síntesis textual y eco, pero no prueban un micrófono
   físico ni la calidad de la voz audible.

## Límites y fallos previos

No se modificaron autenticación, permisos, endpoints, Django ni Ollama. Las
comprobaciones visuales no validan una inferencia real de Ollama ni el servicio
externo de síntesis. El entorno de onboarding ya había registrado 11 fallos y
11 errores en 76 pruebas Django antes de esta tarea; esta entrega no cambia
backend ni afirma resolverlos. No se repitió esa suite ajena al alcance.
