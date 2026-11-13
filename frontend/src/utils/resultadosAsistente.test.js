// MODIFICACION2: validar datos parciales, estados desconocidos y ausencia de registros inventados.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { normalizarResultados } from './resultadosAsistente.js'

test('el contrato actual de texto no produce tarjetas, aunque mencione registros', () => {
  for (const datos of [null, {}, { respuesta: 'Ticket SOP-1 resuelto por Ana el lunes' }, { respuesta: '{"tickets":[{"id":1}]}' }]) {
    assert.deepEqual(normalizarResultados(datos), [])
  }
})
test('conserva solo campos reales de colecciones explícitas', () => {
  assert.deepEqual(normalizarResultados({ tickets: [{ codigo: 'SOP-1', asunto: 'Sin red', estado: 'EN_PROCESO' }] }), [
    { tipo: 'Ticket', id: 'SOP-1', descripcion: 'Sin red', estado: 'En proceso', tono: 'proceso', responsable: null, fecha: null },
  ])
})
test('conserva estado desconocido y fecha original sin interpretaciones', () => {
  const [r] = normalizarResultados({ equipos: [{ id: 0, estado: 'En revisión', fecha: '2026-11-12', responsable: 'Ana' }] })
  assert.equal(r.id, '0'); assert.equal(r.estado, 'En revisión'); assert.equal(r.tono, 'neutro')
  assert.equal(r.fecha, '2026-11-12'); assert.equal(r.responsable, 'Ana')
})
test('ignora campos anidados ambiguos y registros inválidos', () => {
  assert.deepEqual(normalizarResultados({ solicitudes: [null, [], 'Pendiente', {}, { responsable: { nombre: 'Ana' }, estado: { nombre: 'Resuelto' } }] }), [])
  assert.deepEqual(normalizarResultados({ tickets: 'texto', datos: { tickets: [{ id: 1 }] } }), [])
})
test('los tres estados usan etiquetas explícitas y se aceptan datos incompletos', () => {
  const r = normalizarResultados({ solicitudes: [{ estado: 'Pendiente' }, { estado: 'En proceso' }, { estado: 'Resuelto' }] })
  assert.deepEqual(r.map(x => x.tono), ['pendiente', 'proceso', 'resuelto'])
  assert.ok(r.every(x => x.id === null && x.responsable === null && x.fecha === null))
})

test('estados que coinciden con propiedades de Object conservan texto seguro', () => {
  for (const estado of ['__proto__', 'constructor', 'toString']) {
    assert.equal(normalizarResultados({ tickets: [{ estado }] })[0].tono, 'neutro')
  }
})
