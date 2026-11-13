// MODIFICACION2: aceptar solo colecciones explícitas; nunca inferir registros del texto de IA.
const texto = valor => typeof valor === 'string' && valor.trim() ? valor.trim() : null
const identificador = valor => texto(valor) ?? (typeof valor === 'number' && Number.isFinite(valor) ? String(valor) : null)
const ESTADOS = {
  pendiente: ['Pendiente', 'pendiente'],
  en_proceso: ['En proceso', 'proceso'],
  'en proceso': ['En proceso', 'proceso'],
  resuelto: ['Resuelto', 'resuelto'],
}

export function normalizarResultados(datos) {
  if (!datos || typeof datos !== 'object' || Array.isArray(datos)) return []
  return [['solicitudes', 'Solicitud'], ['tickets', 'Ticket'], ['equipos', 'Equipo']].flatMap(([clave, tipo]) => {
    if (!Array.isArray(datos[clave])) return []
    return datos[clave].flatMap(registro => {
      if (!registro || typeof registro !== 'object' || Array.isArray(registro)) return []
      const id = identificador(registro.identificador) ?? identificador(registro.codigo) ?? identificador(registro.id)
      const descripcion = texto(registro.descripcion) ?? texto(registro.asunto) ?? texto(registro.nombre)
      const responsable = texto(registro.responsable) // Objetos sin esquema conocido se omiten.
      const fecha = texto(registro.fecha) // Conservar el valor sin inventar fecha ni zona horaria.
      const original = texto(registro.estado)
      const claveEstado = original?.toLowerCase()
      const [estado, tono] = Object.hasOwn(ESTADOS, claveEstado) ? ESTADOS[claveEstado] : [original, 'neutro']
      if (![id, descripcion, responsable, fecha, estado].some(Boolean)) return []
      return [{ tipo, id, descripcion, responsable, fecha, estado, tono }]
    })
  })
}
