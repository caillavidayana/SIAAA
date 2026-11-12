/*
 * utils/voz.js
 * ============
 * Funciones puras del asistente de voz del SIA (sin dependencias del DOM
 * salvo `describirPantalla`, que recibe el documento como parámetro).
 *
 *  - normalizar(texto)            → minúsculas, sin tildes ni signos.
 *  - detectarPalabraActivacion()  → ¿el usuario dijo "SIA"? y qué dijo después.
 *  - detectarComando()            → órdenes locales (detener, describir, navegar…).
 *  - limpiarParaVoz()             → quita emojis / markdown antes de leer en voz alta.
 *  - dividirEnFrases()            → trozos cortos (Chrome corta lecturas largas).
 *  - elegirVoz()                  → mejor voz en español disponible.
 *  - describirPantalla()          → resumen hablado de lo que se ve en pantalla.
 */

export function normalizar(texto = '') {
  return String(texto)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[¿?¡!.,;:"'()«»\-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

/* ------------------------------------------------------------
   PALABRA DE ACTIVACIÓN ("Tati", "Oye Tati", "Hola Tati")
   El reconocedor del navegador puede transcribir el nombre de varias formas
   ("taty", "tatty", "tatis"). Las variantes inequívocas valen solas; las que se
   parecen a otras palabras ("tadi", "paty", "cati") solo cuentan con un saludo antes.
------------------------------------------------------------ */
export const NOMBRE_ASISTENTE = 'Tati'

const PREFIJOS = '(?:oye|oi|oiga|hola|hey|ey|ok|okey|okay|ola|buenas|buenos dias|buenas tardes|buenas noches)'
const NOMBRE_FUERTE = '(?:tati|taty|tatty|tattie|tatie|tatis|tati s)'
const NOMBRE_DEBIL = '(?:tadi|tady|tachi|taki|paty|pati|cati|katy|kati|tatiana)'

const RE_CON_PREFIJO = new RegExp(`(?:^|\\s)${PREFIJOS}\\s+(?:${NOMBRE_FUERTE}|${NOMBRE_DEBIL})(?=\\s|$)`)
const RE_SOLO_NOMBRE = new RegExp(`(?:^|\\s)${NOMBRE_FUERTE}(?=\\s|$)`)

/**
 * @returns {{ detectado: boolean, resto: string }}
 *   resto = lo dicho después del nombre ("oye tatiana cuántos tickets tengo" → "cuantos tickets tengo")
 */
export function detectarPalabraActivacion(texto) {
  const t = normalizar(texto)
  if (!t) return { detectado: false, resto: '' }
  const m = t.match(RE_CON_PREFIJO) || t.match(RE_SOLO_NOMBRE)
  if (!m) return { detectado: false, resto: '' }
  const fin = m.index + m[0].length
  return { detectado: true, resto: t.slice(fin).trim() }
}

/**
 * Recupera el texto original (con tildes) que sigue a la palabra de activación,
 * para enviar al servidor una pregunta bien escrita.
 */
export function restoOriginal(textoOriginal, restoNormalizado) {
  if (!restoNormalizado) return ''
  const palabras = String(textoOriginal).trim().split(/\s+/)
  const n = restoNormalizado.split(' ').length
  return palabras.slice(-n).join(' ').replace(/^[,.;:\s]+/, '')
}

/* ------------------------------------------------------------
   ÓRDENES LOCALES (se resuelven sin IA, al instante)
------------------------------------------------------------ */
const DESTINOS = [
  { clave: 'notificaciones', re: /notificacion|avisos|alertas/ },
  { clave: 'mis-solicitudes', re: /mis solicitudes|mis tickets|mis pedidos|mis requerimientos|solicitudes/ },
  { clave: 'soporte', re: /soporte|tickets?/ },
  { clave: 'mantenimiento', re: /mantenimiento/ },
  { clave: 'compras', re: /compras?/ },
  { clave: 'perfil', re: /perfil|mi cuenta/ },
  { clave: 'configuracion', re: /configuracion|ajustes|preferencias/ },
  { clave: 'dashboard', re: /inicio|panel|dashboard|principal|tablero|escritorio/ },
]

/**
 * @returns {null | { tipo: string, destino?: string }}
 *   tipo: detener | despedida | describir | repetir | abrir | cerrar | navegar | saludo | desactivar | ayuda
 */
export function detectarComando(texto) {
  const t = normalizar(texto)
  if (!t) return null

  if (/^(para|parale|detente|silencio|callate|basta|alto|stop|deja de hablar|ya|suficiente)$/.test(t)) {
    return { tipo: 'detener' }
  }
  if (/(desactiva|apaga|deshabilita)(r)? (el |la )?(asistente|voz|microfono|escucha)|deja de escuchar/.test(t)) {
    return { tipo: 'desactivar' }
  }
  if (/^(adios|chao|chau|hasta luego|nada|nada mas|eso es todo|gracias|muchas gracias|gracias eso es todo|ok gracias|listo gracias|no gracias)$/.test(t)) {
    return { tipo: 'despedida' }
  }
  if (/^(hola|buenas|buenos dias|buenas tardes|buenas noches|que tal|como estas)$/.test(t)) {
    return { tipo: 'saludo' }
  }
  if (/(describe|describeme|describir|explica|explicame|leeme|lee|resume|resumeme|dime que hay en|que hay en|que (se ve|veo|estoy viendo|muestra)|donde estoy|en que (pantalla|pagina|parte) estoy)/.test(t)
      && /(pantalla|pagina|vista|aqui|esto|ventana|estoy|veo|viendo|muestra|ve)/.test(t)) {
    return { tipo: 'describir' }
  }
  if (/^(repite|repitelo|repetir|otra vez|de nuevo|puedes repetir|que dijiste)/.test(t)) {
    return { tipo: 'repetir' }
  }
  if (/^(que puedes hacer|ayuda|que sabes hacer|como funcionas|que comandos)/.test(t)) {
    return { tipo: 'ayuda' }
  }
  if (/(abre|muestra|muestrame|abrir) (el |la )?(chat|asistente|conversacion)/.test(t)) {
    return { tipo: 'abrir' }
  }
  if (/(cierra|cerrar|oculta|esconde) (el |la )?(chat|asistente|conversacion|ventana)/.test(t)) {
    return { tipo: 'cerrar' }
  }
  const nav = t.match(/^(?:llevame|ve|vamos|ir|anda|navega|abre|abrir|muestrame|entra|entrar|quiero ir|cambia)(?: a| al| a la| a las| a los| a mis| hacia)?\s+(.+)$/)
  if (nav) {
    const texto = nav[1].replace(/^(el|la|los|las|mi|mis|mis|seccion de|seccion|pantalla de|opcion de|opcion)\s+/, '').trim()
    const destino = DESTINOS.find(d => d.re.test(texto))
    return { tipo: 'navegar', destino: destino ? destino.clave : null, texto }
  }
  return null
}

/** ¿La pregunta se refiere a lo que el usuario ve en pantalla? (solo entonces se envía la pantalla a la IA) */
export function refiereAPantalla(texto) {
  const t = normalizar(texto)
  return /\b(esta|este|estos|estas|esa|ese|esos|esas)\s+(pantalla|tabla|vista|pagina|lista|panel|seccion|grafico|indicador|indicadores|registro|registros|ticket|tickets|columna|columnas|dato|datos|numero|numeros)\b|\baqui\b|\bacá\b|\baca\b|lo que (veo|hay|sale|aparece|muestra)|en (la )?pantalla|que significa|que quiere decir/.test(t)
}

/* ------------------------------------------------------------
   NAVEGACIÓN POR EL MENÚ
   Busca la opción del menú lateral / barra de navegación que coincide con
   lo pedido ("notificaciones", "historial"…). Solo dentro de menús, y nunca
   opciones de cierre de sesión ni acciones destructivas.
------------------------------------------------------------ */
const OPCIONES_PROHIBIDAS = /cerrar sesion|salir|logout|eliminar|borrar|rechaz|anular|desactiv|bloque/

export function buscarOpcionMenu(doc, { destino = null, texto = '' } = {}, { excluir = '.sia-asistente-raiz' } = {}) {
  const zonas = doc.querySelectorAll('aside, nav, [role="navigation"], [role="tablist"], [class*="sidebar"], [class*="menu"]')
  const vistos = new Set()
  const patron = destino ? DESTINOS.find(d => d.clave === destino)?.re : null
  const pedido = normalizar(texto)
  let mejor = null
  for (const zona of zonas) {
    if (zona.closest(excluir)) continue
    for (const el of zona.querySelectorAll('a, button, [role="menuitem"], [role="tab"]')) {
      if (vistos.has(el) || el.closest(excluir) || !esVisible(el) || el.disabled) continue
      vistos.add(el)
      const original = textoPorPartes(el).replace(/\s+\d+$/, '').trim()   // quita contadores ("Notificaciones 3")
      const etiqueta = normalizar(original)
      if (!etiqueta || etiqueta.length > 40 || OPCIONES_PROHIBIDAS.test(etiqueta)) continue
      let puntaje = null
      if (pedido && etiqueta === pedido) puntaje = 0
      else if (patron && patron.test(etiqueta)) puntaje = 5 + etiqueta.length / 100
      else if (pedido && pedido.length >= 4 && (etiqueta.includes(pedido) || (etiqueta.length >= 4 && pedido.includes(etiqueta)))) {
        puntaje = 10 + Math.abs(etiqueta.length - pedido.length) / 100
      }
      if (puntaje !== null && (!mejor || puntaje < mejor.puntaje)) mejor = { elemento: el, etiqueta: original, puntaje }
    }
  }
  return mejor
}

/* ------------------------------------------------------------
   TEXTO A VOZ
------------------------------------------------------------ */
export function limpiarParaVoz(texto = '') {
  return String(texto)
    .replace(/<[^>]*>/g, ' ')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/\*\*|__|[*_#~>|]/g, ' ')
    .replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}]/gu, ' ')
    .replace(/[•·▪►✔✓→]/g, ', ')
    .replace(/^\s*\d+\.\s+/gm, '')
    // Códigos de expediente: "SOP-2026-0009" → "S O P 2026, número 9"
    .replace(/\b([A-Z]{2,4})-(\d{4})-0*(\d+)\b/g, (_, l, a, n) => `${l.split('').join(' ')} ${a}, número ${n}`)
    .replace(/\b([A-Z]{2,4})-0*(\d+)\b/g, (_, l, n) => `${l.split('').join(' ')} número ${n}`)
    // Plurales opcionales: "ticket(s)" → "tickets", "nuevo(s)" → "nuevos"
    .replace(/(\p{L}+)\((s|es)\)/gu, '$1$2')
    // "informe/cierre" → "informe o cierre" (no toca fechas ni rutas con números)
    .replace(/(\p{L}{2,})\s*\/\s*(\p{L}{2,})/gu, '$1 o $2')
    // Palabras en MAYÚSCULAS (títulos de tabla) se leen como palabras, no letra por letra
    .replace(/\b(\p{Lu}{5,})\b/gu, m => m.charAt(0) + m.slice(1).toLowerCase())
    .replace(/\bSLAs\b/g, 'ese ele a')
    .replace(/\bSLA\b/g, 'ese ele a')
    .replace(/\bSIA\b/g, 'SÍA')
    .replace(/\bUTIC\b/g, 'útic')
    .replace(/\bDAF\b/g, 'daf')
    .replace(/Bs\.?\s?(\d)/g, '$1 bolivianos ')
    .replace(/\s*\n+\s*/g, '. ')
    .replace(/\s+([.,;:])/g, '$1')
    .replace(/([.,;:])\1+/g, '$1')
    .replace(/(\.\s*){2,}/g, '. ')
    .replace(/\s{2,}/g, ' ')
    .replace(/^[\s.,;:]+/, '')
    .trim()
}

/** Divide en frases de máx. `max` caracteres (Chrome corta utterances largas ~15 s). */
export function dividirEnFrases(texto, max = 180) {
  const frases = String(texto).match(/[^.!?;]+[.!?;]*/g) || []
  const trozos = []
  for (let f of frases) {
    f = f.trim()
    if (!f) continue
    while (f.length > max) {
      let corte = f.lastIndexOf(',', max)
      if (corte < max / 3) corte = f.lastIndexOf(' ', max)
      if (corte <= 0) corte = max
      trozos.push(f.slice(0, corte + 1).trim())
      f = f.slice(corte + 1).trim()
    }
    if (f) trozos.push(f)
  }
  return trozos
}

const ABREVIATURAS = /\b(bs|sr|sra|srta|dr|dra|ing|lic|nro|no|num|etc|ej|pag|av|cel|tel|cod|aprox)$/i

/**
 * Separa las frases completas de un texto que llega por partes (respuesta en streaming).
 * Corta en . ! ? ; : seguidos de espacio, o en saltos de línea, sin cortar abreviaturas
 * ("Bs. 50") ni números ("3.5"). Devuelve { frases, resto }; con final=true entrega todo.
 */
export function extraerFrases(buffer, final = false, min = 20) {
  const frases = []
  const re = /[.!?;:](?=\s)|\n/g
  let inicio = 0
  let m
  while ((m = re.exec(buffer))) {
    const fin = m.index + 1
    const candidato = buffer.slice(inicio, fin).trim()
    if (!candidato) { inicio = fin; continue }
    if (m[0] === '.' && ABREVIATURAS.test(buffer.slice(inicio, m.index).trim())) continue
    if (candidato.length >= min || m[0] === '\n') {
      frases.push(candidato)
      inicio = fin
    }
  }
  let resto = buffer.slice(inicio)
  if (final && resto.trim()) { frases.push(resto.trim()); resto = '' }
  return { frases, resto }
}

/**
 * Prepara una respuesta para leerla en voz alta: la limpia y, si es muy larga,
 * lee solo el comienzo (hasta `max` caracteres, cortando en una frase completa)
 * y avisa que el detalle está en el chat. Devuelve las frases a leer.
 */
export function frasesParaVoz(texto, { max = 600, trozo = 180 } = {}) {
  let limpio = limpiarParaVoz(texto)
  if (limpio.length > max) {
    const corte = Math.max(limpio.lastIndexOf('. ', max), limpio.lastIndexOf('? ', max), limpio.lastIndexOf('! ', max))
    limpio = (corte > max / 3 ? limpio.slice(0, corte + 1) : limpio.slice(0, limpio.lastIndexOf(' ', max)) + '.')
      + ' El resto te lo dejé escrito en el chat.'
  }
  return dividirEnFrases(limpio, trozo)
}

const VOCES_MASCULINAS = /gonzalo|jorge|raul|pablo|alvaro|diego|tomas|carlos|juan|lorenzo|enrique|gerardo|federico|alonso|emilio|manuel|arnau|dario|saul|teo|andres|alex|mateo|sergio|luciano|cecilio|rodrigo|yago/i

/**
 * Elige la voz del navegador más parecida a Tati: español de Colombia primero,
 * luego Latinoamérica, después España; prefiere voces femeninas y neuronales.
 */
export function elegirVoz(voces = []) {
  const es = voces.filter(v => /^es([-_]|$)/i.test(v.lang))
  if (!es.length) return null
  const orden = ['es-co', 'es-419', 'es-mx', 'es-us', 'es-ve', 'es-pe', 'es-ec', 'es-bo', 'es-ar', 'es-cl', 'es-es']
  const puntaje = v => {
    const lang = v.lang.toLowerCase().replace('_', '-')
    let p = orden.indexOf(lang)
    if (p === -1) p = orden.length
    const nombre = v.name.normalize('NFD').replace(/[̀-ͯ]/g, '')
    if (VOCES_MASCULINAS.test(nombre)) p += 0.6
    // Las voces "Natural"/"Online"/Google suenan mucho mejor
    if (/natural|online|neural|google/i.test(nombre)) p -= 0.5
    return p
  }
  return [...es].sort((a, b) => puntaje(a) - puntaje(b))[0]
}

/* ------------------------------------------------------------
   DESCRIPCIÓN DE PANTALLA
------------------------------------------------------------ */
function textoVisible(el) {
  if (!el) return ''
  return (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim()
}

/** Texto de un elemento separando sus partes (<b>Nuevos</b><em>3</em> → "Nuevos 3"). */
function textoPorPartes(el) {
  const partes = []
  const recorrer = (n) => {
    for (const c of n.childNodes) {
      if (c.nodeType === 3) partes.push(c.textContent.trim())
      else if (c.nodeType === 1) recorrer(c)
    }
  }
  recorrer(el)
  return partes.filter(Boolean).join(' ')
}

function esVisible(el) {
  if (!el || !el.getClientRects || !el.getClientRects().length) return false
  const st = el.ownerDocument?.defaultView?.getComputedStyle?.(el)
  return !st || (st.visibility !== 'hidden' && st.display !== 'none')
}

/**
 * Lee la pantalla actual (sin incluir el propio asistente) y devuelve:
 *  - hablado: texto corto para decir en voz alta
 *  - resumen: texto algo más detallado para enviar como contexto a la IA
 */
export function describirPantalla(doc, { excluir = '.sia-asistente-raiz' } = {}) {
  const raiz = doc.querySelector('main') || doc.querySelector('#app') || doc.body
  const fuera = el => el.closest(excluir) || !esVisible(el)

  const encabezados = [...raiz.querySelectorAll('h1, h2, h3')]
    .filter(el => !fuera(el))
    .map(textoVisible)
    .filter(t => t && t.length < 90)
  const unicos = [...new Set(encabezados)].slice(0, 6)

  // Indicadores con números: tarjetas de resumen (<small>Etiqueta</small><b>3</b>)
  // y cabeceras de columnas kanban ("Nuevos 3").
  const indicadores = []
  const agregar = (t) => {
    t = t.replace(/\s+/g, ' ').trim()
    if (t && /\d/.test(t) && t.length <= 80 && !indicadores.includes(t)) indicadores.push(t)
  }
  const selectorIndicadores = '[class*="stats"] > *, [class*="kpi"], [class*="metric"], [class*="column-head"], [class*="contador"]'
  for (const el of raiz.querySelectorAll(selectorIndicadores)) {
    if (fuera(el) || el.querySelector('table')) continue
    const etiqueta = el.querySelector('small, dt, label, h4')
    const valor = el.querySelector('b, strong, dd, em')
    if (etiqueta && valor && !etiqueta.contains(valor) && !valor.contains(etiqueta)) {
      agregar(`${textoVisible(etiqueta)}: ${textoVisible(valor)}`)
    } else {
      agregar(textoPorPartes(el))
    }
    if (indicadores.length >= 8) break
  }

  const tablas = [...raiz.querySelectorAll('table')].filter(el => !fuera(el)).slice(0, 2).map(tabla => {
    const columnas = [...tabla.querySelectorAll('thead th')].map(textoVisible)
      .filter(c => c && !/^(acci[oó]n|acciones|opciones|ver)$/i.test(c)).slice(0, 6)
    const filas = [...tabla.querySelectorAll('tbody tr')].filter(tr => tr.querySelectorAll('td').length > 1)
    const ejemplos = filas.slice(0, 3).map(tr =>
      [...tr.querySelectorAll('td')].map(textoVisible).filter(Boolean).slice(0, 4).join(', '))
    return { columnas, total: filas.length, ejemplos }
  })

  const titulo = unicos[0] || (doc.title || '').replace(/\s*[|-].*$/, '').trim()

  const partes = []
  partes.push(titulo ? `Estás en la pantalla ${titulo}.` : 'Estás en una pantalla del sistema.')
  if (unicos.length > 1) partes.push(`Secciones: ${unicos.slice(1).join(', ')}.`)
  if (indicadores.length) partes.push(`Indicadores: ${indicadores.slice(0, 6).join('; ')}.`)
  for (const t of tablas) {
    if (t.total === 0) {
      partes.push('Hay una tabla, sin registros por ahora.')
    } else {
      partes.push(`Hay una tabla con ${t.total} ${t.total === 1 ? 'registro' : 'registros'}${t.columnas.length ? ', con columnas ' + t.columnas.join(', ') : ''}.`)
      if (t.ejemplos[0]) partes.push(`El primero es: ${t.ejemplos[0]}.`)
    }
  }
  if (partes.length === 1) partes.push('No encontré tablas ni indicadores en esta vista.')

  const resumen = [
    `Título: ${titulo || 'sin título'}`,
    unicos.length > 1 ? `Secciones: ${unicos.slice(1).join(' | ')}` : '',
    indicadores.length ? `Indicadores: ${indicadores.join(' | ')}` : '',
    ...tablas.map(t => `Tabla (${t.total} filas) columnas: ${t.columnas.join(', ')}; ejemplos: ${t.ejemplos.join(' || ')}`),
  ].filter(Boolean).join('\n').slice(0, 1500)

  return { hablado: partes.join(' '), resumen, titulo }
}

/** Nombres de las opciones del menú visible (para decirle al usuario qué puede abrir). */
export function opcionesMenu(doc, { excluir = '.sia-asistente-raiz' } = {}) {
  const nombres = []
  for (const zona of doc.querySelectorAll('aside, nav, [role="navigation"], [class*="sidebar"]')) {
    if (zona.closest(excluir)) continue
    for (const el of zona.querySelectorAll('a, button, [role="menuitem"]')) {
      if (el.closest(excluir) || !esVisible(el)) continue
      const nombre = textoPorPartes(el).replace(/\s+\d+$/, '').trim()
      const n = normalizar(nombre)
      if (n.length >= 3 && n.length <= 40 && !OPCIONES_PROHIBIDAS.test(n) && !/^[^a-z]*$/.test(n) && !nombres.includes(nombre)) {
        nombres.push(nombre)
      }
    }
  }
  return nombres.slice(0, 8)
}

/**
 * Mientras Tati habla, el micrófono puede captar su propia voz por los parlantes.
 * Se considera eco si la mayoría de las palabras oídas aparecen en lo que ella está diciendo.
 */
export function esEco(oido, dicho) {
  const palabras = normalizar(oido).split(' ').filter(p => p.length >= 3)
  if (!palabras.length) return true
  const enDicho = new Set(normalizar(dicho).split(' '))
  const coinciden = palabras.filter(p => enDicho.has(p)).length
  return coinciden / palabras.length >= 0.5
}

/** Órdenes para interrumpir a Tati mientras habla o piensa. */
export function esOrdenDeParar(texto) {
  return /^(?:(?:oye |ok |hey )?tati,? )?(para|parale|detente|silencio|callate|basta|alto|stop|cancela|cancelar|deja de hablar|ya basta|suficiente)( por favor)?$/.test(normalizar(texto))
}
