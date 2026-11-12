import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  normalizar, detectarPalabraActivacion, restoOriginal, detectarComando,
  limpiarParaVoz, dividirEnFrases, elegirVoz, frasesParaVoz, extraerFrases, refiereAPantalla, esEco, esOrdenDeParar,
} from './voz.js'

test('normalizar quita tildes, signos y mayúsculas', () => {
  assert.equal(normalizar('¿Cuántos TICKETS tengo, SIA?'), 'cuantos tickets tengo sia')
})

test('detecta el nombre de la asistente en sus variantes', () => {
  for (const frase of ['Tati', 'Oye Tati', 'hola tati', 'Hey, Tati', 'Taty', 'Tatty', 'oye tadi', 'Hola Paty', 'buenos días Tati']) {
    assert.equal(detectarPalabraActivacion(frase).detectado, true, frase)
  }
})

test('no se activa con palabras parecidas sin saludo', () => {
  for (const frase of ['paty llegó', 'la cati vino', 'tatuaje', 'patio', 'hola a todos', 'oye SIA', '']) {
    assert.equal(detectarPalabraActivacion(frase).detectado, false, frase)
  }
})

test('devuelve lo dicho después del nombre', () => {
  const r = detectarPalabraActivacion('Oye Tati, ¿cuántos tickets tengo?')
  assert.equal(r.resto, 'cuantos tickets tengo')
  assert.equal(restoOriginal('Oye Tati, ¿cuántos tickets tengo?', r.resto), '¿cuántos tickets tengo?')
  assert.equal(detectarPalabraActivacion('hola tati').resto, '')
  assert.equal(detectarPalabraActivacion('bueno tati qué hay pendiente').resto, 'que hay pendiente')
})

test('reconoce órdenes locales', () => {
  assert.deepEqual(detectarComando('Para'), { tipo: 'detener' })
  assert.deepEqual(detectarComando('silencio'), { tipo: 'detener' })
  assert.deepEqual(detectarComando('Describe esta pantalla'), { tipo: 'describir' })
  assert.deepEqual(detectarComando('¿Dónde estoy?'), { tipo: 'describir' })
  assert.deepEqual(detectarComando('¿qué hay en la pantalla?'), { tipo: 'describir' })
  assert.deepEqual(detectarComando('repítelo'), { tipo: 'repetir' })
  assert.deepEqual(detectarComando('gracias, eso es todo'), { tipo: 'despedida' })
  assert.equal(detectarComando('llévame a notificaciones').destino, 'notificaciones')
  assert.equal(detectarComando('ve al inicio').destino, 'dashboard')
  assert.equal(detectarComando('abre mis solicitudes').destino, 'mis-solicitudes')
  assert.deepEqual(detectarComando('llévame al historial'), { tipo: 'navegar', destino: null, texto: 'historial' })
  assert.deepEqual(detectarComando('cierra el chat'), { tipo: 'cerrar' })
  assert.deepEqual(detectarComando('desactiva el asistente'), { tipo: 'desactivar' })
})

test('las preguntas normales no son órdenes locales', () => {
  assert.equal(detectarComando('¿Cuántos tickets tengo en proceso?'), null)
  assert.equal(detectarComando('para qué sirve la caja chica'), null)
})

test('limpia emojis y markdown antes de leer en voz alta', () => {
  const t = limpiarParaVoz('🤖 **Asistente SIA:**\n\n• Tienes **3** tickets\n• SLA: 4h')
  assert.ok(!/[*•🤖]/u.test(t), t)
  assert.match(t, /Tienes 3 tickets/)
  assert.match(t, /ese ele a/)
})

test('divide textos largos en frases cortas', () => {
  const largo = 'Primera frase corta. ' + 'palabra '.repeat(60) + 'fin.'
  const trozos = dividirEnFrases(largo, 120)
  assert.equal(trozos[0], 'Primera frase corta.')
  assert.ok(trozos.every(t => t.length <= 121), JSON.stringify(trozos))
  assert.ok(trozos.length > 3)
})

test('elige una voz colombiana y femenina cuando existe', () => {
  const edge = [
    { lang: 'es-ES', name: 'Microsoft Helena' },
    { lang: 'es-MX', name: 'Microsoft Dalia Online (Natural) - Spanish (Mexico)' },
    { lang: 'es-CO', name: 'Microsoft Gonzalo Online (Natural) - Spanish (Colombia)' },
    { lang: 'es-CO', name: 'Microsoft Salome Online (Natural) - Spanish (Colombia)' },
  ]
  assert.match(elegirVoz(edge).name, /Salome/)
  const chrome = [
    { lang: 'en-US', name: 'Google US English' },
    { lang: 'es-ES', name: 'Google español' },
    { lang: 'es-US', name: 'Google español de Estados Unidos' },
  ]
  assert.equal(elegirVoz(chrome).name, 'Google español de Estados Unidos')
  assert.equal(elegirVoz([{ lang: 'en-US', name: 'x' }]), null)
})

test('resume respuestas largas antes de leerlas', () => {
  const corta = frasesParaVoz('**Tienes 3 tickets.** Dos están vencidos.')
  assert.deepEqual(corta, ['Tienes 3 tickets.', 'Dos están vencidos.'])
  const larga = frasesParaVoz(Array.from({ length: 30 }, (_, i) => `Esta es la frase número ${i + 1} de la respuesta.`).join(' '))
  assert.equal(larga.at(-1), 'El resto te lo dejé escrito en el chat.')
  assert.ok(larga.join(' ').length < 700)
})

test('extrae frases completas de una respuesta que llega por partes', () => {
  // importado arriba
  let r = extraerFrases('En este momento no hay tickets nuevos. Tres tickets están en aten')
  assert.deepEqual(r.frases, ['En este momento no hay tickets nuevos.'])
  assert.equal(r.resto.trim(), 'Tres tickets están en aten')
  r = extraerFrases('El monto aprobado es de Bs. 350.5 para la compra del equipo. Lue')
  assert.deepEqual(r.frases, ['El monto aprobado es de Bs. 350.5 para la compra del equipo.'])
  r = extraerFrases('Hola. Sí', true)
  assert.deepEqual(r.frases, ['Hola. Sí'])
  r = extraerFrases('Pasos a seguir en el sistema:\n1. Abre el ticket\n')
  assert.deepEqual(r.frases, ['Pasos a seguir en el sistema:', '1. Abre el ticket'])
})

test('solo envía la pantalla a la IA cuando la pregunta se refiere a ella', () => {
  for (const q of ['¿Qué significa esta tabla?', 'explícame estos indicadores', '¿qué hay aquí?', 'resume lo que veo']) {
    assert.equal(refiereAPantalla(q), true, q)
  }
  for (const q of ['¿Cuántos tickets tengo?', '¿Cómo reasigno un ticket?']) {
    assert.equal(refiereAPantalla(q), false, q)
  }
})

test('pronuncia códigos, plurales, barras y mayúsculas de forma natural', () => {
  assert.equal(limpiarParaVoz('El ticket SOP-2026-0009 está abierto.'), 'El ticket S O P 2026, número 9 está abierto.')
  assert.equal(limpiarParaVoz('Hay 0 ticket(s) nuevo(s).'), 'Hay 0 tickets nuevos.')
  assert.equal(limpiarParaVoz('Cuatro pendientes de informe/cierre.'), 'Cuatro pendientes de informe o cierre.')
  assert.equal(limpiarParaVoz('Columnas TICKET, ASUNTO, PRIORIDAD.'), 'Columnas Ticket, Asunto, Prioridad.')
  assert.equal(limpiarParaVoz('Fecha 10/11/2026 y el SIA.'), 'Fecha 10/11/2026 y el SÍA.')
})

test('distingue el eco de la propia voz de una orden del usuario', () => {
  const dicho = 'Para reasignar un ticket, abre el detalle y elige otro especialista.'
  assert.equal(esEco('para reasignar un ticket', dicho), true)
  assert.equal(esEco('para', dicho), true)          // "para" aparece en lo que dice: es eco
  assert.equal(esEco('oye tati', dicho), false)
  assert.equal(esEco('silencio', dicho), false)
  assert.equal(esOrdenDeParar('Silencio'), true)
  assert.equal(esOrdenDeParar('Tati, para por favor'), true)
  assert.equal(esOrdenDeParar('para qué sirve la caja chica'), false)
})
