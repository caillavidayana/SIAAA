<!--
  AsistenteChat.vue
  ==================
  Asistente Virtual Inteligente del Sistema Integrado Administrativo (SIA).
  Diseñado con la identidad visual institucional de la EMI:
    - Azul Marino (#0C2A4F / #123A6B)
    - Amarillo Mostaza / Dorado (#FFC72C / #B98F00)
    - Blanco y neutros (#F4F8FC / #D7E3EF)
  
  Funcionalidades de Voz:
    1. Dictado por micrófono (STT) mediante Web Speech API.
    2. Modo Conversación / Llamada por Voz interactiva (hands-free).
    3. Síntesis de voz (TTS) para escuchar las respuestas del asistente.
-->

<template>
  <template v-if="estaAutenticado">

    <!-- ===================================================
         BOTÓN FLOTANTE (FAB)
    =================================================== -->
    <button
      class="sia-fab"
      :class="{ 'sia-fab--abierto': abierto }"
      @click="toggleChat"
      :title="abierto ? 'Cerrar asistente' : 'Abrir Asistente SIA'"
      aria-label="Asistente SIA"
    >
      <!-- Ícono robot cuando está cerrado -->
      <svg v-if="!abierto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
        <path d="M12 2a2 2 0 0 1 2 2 2 2 0 0 1-2 2 2 2 0 0 1-2-2 2 2 0 0 1 2-2m7 7H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2v3l3-3h4l3 3v-3h2a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2M9 13.5a1.5 1.5 0 0 1-1.5-1.5A1.5 1.5 0 0 1 9 10.5 1.5 1.5 0 0 1 10.5 12 1.5 1.5 0 0 1 9 13.5m6 0a1.5 1.5 0 0 1-1.5-1.5A1.5 1.5 0 0 1 15 10.5a1.5 1.5 0 0 1 1.5 1.5A1.5 1.5 0 0 1 15 13.5z"/>
      </svg>
      <!-- Ícono X cuando está abierto -->
      <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>

      <!-- Badge de notificación -->
      <span v-if="hayMensajeNuevo && !abierto" class="sia-fab__badge"></span>
    </button>


    <!-- ===================================================
         VENTANA DE CHAT
    =================================================== -->
    <transition name="sia-slide">
      <div
        v-if="abierto"
        class="sia-ventana"
        :class="{ 'sia-ventana--expandida': expandido }"
        role="dialog"
        aria-label="Asistente SIA"
      >

        <!-- CABECERA INSTITUCIONAL SIA -->
        <div class="sia-ventana__header">
          <div class="sia-ventana__header-info">
            <div class="sia-ventana__avatar">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="22" height="22">
                <path d="M12 2a2 2 0 0 1 2 2 2 2 0 0 1-2 2 2 2 0 0 1-2-2 2 2 0 0 1 2-2m7 7H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2v3l3-3h4l3 3v-3h2a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2M9 13.5a1.5 1.5 0 0 1-1.5-1.5A1.5 1.5 0 0 1 9 10.5 1.5 1.5 0 0 1 10.5 12 1.5 1.5 0 0 1 9 13.5m6 0a1.5 1.5 0 0 1-1.5-1.5A1.5 1.5 0 0 1 15 10.5a1.5 1.5 0 0 1 1.5 1.5A1.5 1.5 0 0 1 15 13.5z"/>
              </svg>
            </div>
            <div>
              <div class="sia-ventana__titulo-box">
                <span class="sia-ventana__nombre">Asistente SIA</span>
                <span class="sia-ventana__tag-ia">IA</span>
              </div>
              <span class="sia-ventana__estado">
                <span class="sia-ventana__estado-dot"></span>
                En línea · Soporte Institucional
              </span>
            </div>
          </div>

          <!-- Acciones de cabecera -->
          <div class="sia-ventana__header-actions">
            <!-- Botón Expandir / Reducir Ventana -->
            <button
              class="sia-ventana__btn-accion"
              @click="expandido = !expandido"
              :title="expandido ? 'Reducir ventana' : 'Expandir ventana para mayor comodidad'"
            >
              <svg v-if="!expandido" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-14v3h3v2h2V5h-5z"/>
              </svg>
            </button>

            <!-- Botón Nueva Conversación -->
            <button class="sia-ventana__btn-accion" @click="limpiarChat" title="Reiniciar chat">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- BANNER DE MODO LLAMADA / CONVERSACIÓN ACTIVA -->
        <div v-if="modoLlamada" class="sia-banner-llamada">
          <div class="sia-banner-llamada__pulso"></div>
          <div class="sia-banner-llamada__texto">
            <strong>Modo Conversación por Voz Activo</strong>
            <span>{{ hablando ? 'SIA está hablando...' : (grabando ? 'Escuchando tu voz...' : 'Esperando tu consulta...') }}</span>
          </div>
          <button class="sia-banner-llamada__btn-salir" @click="toggleModoLlamada" title="Salir de llamada">Finalizar</button>
        </div>

        <!-- ÁREA DE MENSAJES -->
        <div class="sia-ventana__mensajes" ref="contenedorMensajes">

          <!-- Bienvenida -->
          <div v-if="mensajes.length === 0" class="sia-bienvenida">
            <div class="sia-bienvenida__icono">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="38" height="38">
                <path d="M12 2a2 2 0 0 1 2 2 2 2 0 0 1-2 2 2 2 0 0 1-2-2 2 2 0 0 1 2-2m7 7H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2v3l3-3h4l3 3v-3h2a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2M9 13.5a1.5 1.5 0 0 1-1.5-1.5A1.5 1.5 0 0 1 9 10.5 1.5 1.5 0 0 1 10.5 12 1.5 1.5 0 0 1 9 13.5m6 0a1.5 1.5 0 0 1-1.5-1.5A1.5 1.5 0 0 1 15 10.5a1.5 1.5 0 0 1 1.5 1.5A1.5 1.5 0 0 1 15 13.5z"/>
              </svg>
            </div>
            <p class="sia-bienvenida__titulo">¡Hola{{ nombreUsuario ? ', ' + nombreUsuario : '' }}!</p>
            <p class="sia-bienvenida__texto">
              {{ mensajeBienvenida }}
            </p>
            <div class="sia-bienvenida__nota-voz">
              💡 Puedes escribir tu consulta o <strong>presionar el micrófono 🎙️</strong> para dictar por voz.
            </div>
            <div class="sia-sugerencias">
              <button
                v-for="(sug, i) in sugerencias"
                :key="i"
                class="sia-sugerencia"
                @click="usarSugerencia(sug)"
              >{{ sug }}</button>
            </div>
          </div>

          <!-- Mensajes de conversación -->
          <div
            v-for="(msg, i) in mensajes"
            :key="i"
            :class="['sia-mensaje', msg.rol === 'usuario' ? 'sia-mensaje--usuario' : 'sia-mensaje--bot']"
          >
            <div class="sia-mensaje__burbuja">
              <span class="sia-mensaje__texto" v-html="formatearTexto(msg.texto)"></span>

              <div class="sia-mensaje__footer">
                <!-- Botón escuchar voz para respuestas del asistente -->
                <button
                  v-if="msg.rol === 'bot'"
                  class="sia-mensaje__btn-escuchar"
                  @click="hablarTexto(msg.texto)"
                  title="Reproducir respuesta en voz alta"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="13" height="13">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
                  </svg>
                  Escuchar
                </button>
                <span class="sia-mensaje__hora">{{ msg.hora }}</span>
              </div>
            </div>
          </div>

          <!-- Indicador escribiendo -->
          <div v-if="cargando" class="sia-mensaje sia-mensaje--bot">
            <div class="sia-mensaje__burbuja sia-mensaje__burbuja--typing">
              <div class="sia-typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Banner de Grabación por Voz (micrófono activo) -->
        <div v-if="grabando && !modoLlamada" class="sia-voz-activo-banner">
          <span class="sia-voz-dot"></span>
          <span>Escuchando... Di tu consulta y presiona el micrófono para finalizar</span>
        </div>

        <!-- Banner de Error -->
        <div v-if="errorConexion" class="sia-error-banner">
          ⚠️ No se pudo conectar con el servidor. Reintentando...
        </div>

        <!-- ÁREA DE INPUT CON BOTÓN DE MICRÓFONO -->
        <div class="sia-ventana__input-area">
          <textarea
            ref="inputRef"
            v-model="mensajeActual"
            class="sia-ventana__input"
            placeholder="Escribe o dicta tu consulta..."
            rows="1"
            :disabled="cargando"
            @keydown.enter.exact.prevent="enviarMensaje"
            @keydown.enter.shift.exact="null"
            @input="ajustarAltura"
            maxlength="2000"
          ></textarea>

          <!-- BOTÓN MODO LLAMADA / CONVERSACIÓN CONTINUA (PERSONA HABLANDO) -->
          <button
            type="button"
            class="sia-ventana__btn-voz-continua"
            :class="{ 'sia-ventana__btn-voz-continua--activo': modoLlamada }"
            @click="toggleModoLlamada"
            :title="modoLlamada ? 'Modo Conversación por Voz ACTIVO (clic para apagar)' : 'Iniciar conversación continua tipo llamada con SIA'"
          >
            <!-- Ícono de persona hablando -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="19" height="19">
              <path d="M9 13.75c-2.34 0-7 1.17-7 3.5V19h14v-1.75c0-2.33-4.66-3.5-7-3.5zM9 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm8.5-5.5c0 1.25-.51 2.38-1.34 3.19l1.42 1.42C18.66 10.03 19.5 8.61 19.5 6.5s-.84-3.53-2.08-4.61l-1.42 1.42c.83.81 1.34 1.94 1.34 3.19zm2.5 0c0 2.05-.82 3.91-2.15 5.27l1.42 1.42C21.11 9.94 22 7.82 22 6.5s-.89-3.44-2.23-4.69l-1.42 1.42C19.68 2.59 20.5 4.45 20.5 6.5z"/>
            </svg>
          </button>

          <!-- BOTÓN MICRÓFONO (DICTADO POR VOZ) -->
          <button
            type="button"
            class="sia-ventana__btn-mic"
            :class="{ 'sia-ventana__btn-mic--grabando': grabando }"
            @click="toggleGrabacionManual"
            :title="grabando ? 'Detener dictado' : 'Dictar consulta por voz (Micrófono)'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="19" height="19">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
          </button>

          <!-- BOTÓN ENVIAR -->
          <button
            class="sia-ventana__btn-enviar"
            :disabled="!mensajeActual.trim() || cargando"
            @click="enviarMensaje"
            title="Enviar consulta (Enter)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>

        <div class="sia-ventana__subhint">
          <span>🎙️ Presiona el micrófono para dictar · Enter para enviar</span>
        </div>

      </div>
    </transition>
  </template>
</template>


<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

/* ============================================================
   ESTADO
============================================================ */
const abierto         = ref(false)
const expandido       = ref(false)
const mensajeActual   = ref('')
const mensajes        = ref([])
const cargando        = ref(false)
const errorConexion   = ref(false)
const hayMensajeNuevo = ref(false)
const grabando        = ref(false)
const hablando        = ref(false)
const modoLlamada     = ref(false)

const contenedorMensajes = ref(null)
const inputRef           = ref(null)
let reconocimiento       = null

/* Token reactivo y usuario */
const rawToken = ref(localStorage.getItem('sigta_token') || '')
const rawUsuario = ref(localStorage.getItem('sigta_usuario') || '')

function actualizarSesion() {
  rawToken.value = localStorage.getItem('sigta_token') || ''
  rawUsuario.value = localStorage.getItem('sigta_usuario') || ''
}

watch(() => route.path, () => {
  actualizarSesion()
})

let timer = null
onMounted(() => {
  actualizarSesion()
  window.addEventListener('storage', actualizarSesion)
  timer = setInterval(actualizarSesion, 1000)
})

onUnmounted(() => {
  window.removeEventListener('storage', actualizarSesion)
  if (timer) clearInterval(timer)
  detenerVozTotal()
})

const estaAutenticado = computed(() => {
  if (!route.path || route.path === '/login' || route.path === '/recuperar-contrasena') {
    return false
  }
  return !!rawToken.value
})

const token = computed(() => rawToken.value)

const nombreUsuario = computed(() => {
  try {
    const u = JSON.parse(rawUsuario.value || localStorage.getItem('sigta_usuario') || '{}')
    return u.first_name || u.nombre || u.username || ''
  } catch {
    return ''
  }
})

/* ============================================================
   ROL ACTIVO DETECTADO
============================================================ */
const rolActivo = computed(() => {
  const path = route.path || ''
  if (path.startsWith('/auxiliar-servicios-generales')) return 'AUXILIAR_SERVICIOS_GENERALES'
  if (path.startsWith('/servicios-generales')) return 'SERVICIOS_GENERALES'
  if (path.startsWith('/especialista')) return 'ESPECIALISTA'
  if (path.startsWith('/jefe-utic')) return 'JEFE_UTIC'
  if (path.startsWith('/tesoreria')) return 'TESORERIA'
  if (path.startsWith('/almacen')) return 'ENCARGADO_COMPRAS_ALMACEN'
  if (path.startsWith('/daf')) return 'DAF'
  if (path.startsWith('/admin') || path.startsWith('/superuser')) return 'ADMIN'
  if (path.startsWith('/usuario')) return 'SOLICITANTE'

  try {
    const u = JSON.parse(rawUsuario.value || localStorage.getItem('sigta_usuario') || '{}')
    const roles = Array.isArray(u.roles) ? u.roles.map(r => (typeof r === 'string' ? r : r.codigo)) : []
    const orden = [
      'AUXILIAR_SERVICIOS_GENERALES',
      'ESPECIALISTA',
      'SERVICIOS_GENERALES',
      'JEFE_UTIC',
      'DAF',
      'JEFE_DAF',
      'TESORERIA',
      'ENCARGADO_COMPRAS_ALMACEN',
      'ADMIN',
      'SUPERUSER',
      'DIRECTOR',
      'JEFE_CARRERA',
      'SOLICITANTE'
    ]
    for (const r of orden) {
      if (roles.includes(r)) return r
    }
    if (roles.length > 0) return roles[0]
  } catch {}
  return 'SOLICITANTE'
})

/* ============================================================
   MENSAJE DE BIENVENIDA PERSONALIZADO POR ROL
============================================================ */
const mensajeBienvenida = computed(() => {
  const rol = rolActivo.value
  switch (rol) {
    case 'AUXILIAR_SERVICIOS_GENERALES':
      return 'Soy el asistente técnico de SIA para Mantenimiento. Te ayudo a consultar tus órdenes de trabajo asignadas, recepción de componentes en almacén, diagnósticos y reportes.'
    case 'ESPECIALISTA':
      return 'Soy el asistente técnico de SIA para Soporte UTIC. Te ayudo a monitorear tus tickets asignados, tiempos de SLA, diagnóstico de incidentes y registro de soluciones.'
    case 'SERVICIOS_GENERALES':
      return 'Soy el asistente de gestión de SIA para la Jefatura de Mantenimiento. Te ayudo en la clasificación de solicitudes, supervisión de órdenes en infraestructura y aprobación de informes técnicos.'
    case 'JEFE_UTIC':
      return 'Soy el asistente de supervisión de SIA para la Jefatura UTIC. Te ayudo con la asignación de tickets, control de carga de especialistas y monitoreo de SLAs.'
    case 'ENCARGADO_COMPRAS_ALMACEN':
      return 'Soy el asistente operativo de SIA para Almacén y Adquisiciones. Te ayudo a dar seguimiento a órdenes de compra, actas de recepción y entrega de componentes a los técnicos.'
    case 'DAF':
    case 'JEFE_DAF':
      return 'Soy el asistente financiero de SIA para la DAF. Te ayudo a revisar certificaciones presupuestarias, autorizaciones de compra y control de fondos.'
    case 'TESORERIA':
      return 'Soy el asistente financiero de SIA para Tesorería. Te ayudo a controlar órdenes autorizadas para pago, desembolsos y fondos rotatorios.'
    case 'ADMIN':
    case 'SUPERUSER':
    case 'DIRECTOR':
      return 'Soy el asistente ejecutivo y administrativo de SIA. Te brindo una visión integral de operaciones, métricas globales, seguridad y configuración institucional.'
    case 'SOLICITANTE':
    case 'JEFE_CARRERA':
    default:
      return 'Soy el asistente inteligente del SIA. Puedo orientarte sobre tus tickets activos, procedimientos de mantenimiento, compras y reglas operativas del sistema.'
  }
})

/* ============================================================
   SUGERENCIAS RÁPIDAS DINÁMICAS POR ROL
============================================================ */
const sugerencias = computed(() => {
  const rol = rolActivo.value
  switch (rol) {
    case 'AUXILIAR_SERVICIOS_GENERALES':
      return [
        '¿Cuántas órdenes tengo por recibir?',
        '¿Cuáles órdenes están en reparación?',
        '¿Qué órdenes tengo pendientes de pruebas o informe?',
        '¿Tengo componentes pendientes de recepción en almacén?',
        '¿Cómo registro el diagnóstico y requerimiento de compra?',
      ]
    case 'ESPECIALISTA':
      return [
        '¿Cuántos tickets tengo asignados por recibir?',
        '¿Cuáles tickets están en ejecución o diagnóstico?',
        '¿Qué tickets esperan pruebas o informe final?',
        '¿Cuáles son los SLAs y tiempos de atención asignados?',
        '¿Cómo registro la solución de un ticket técnico?',
      ]
    case 'SERVICIOS_GENERALES':
      return [
        '¿Cuántas solicitudes están pendientes de clasificar o derivar?',
        '¿Cuáles órdenes de mantenimiento están en curso?',
        '¿Qué órdenes tienen informe técnico pendiente de revisión?',
        '¿Cuántos requerimientos requieren compra o caja chica?',
        '¿Cómo designo un auxiliar a una orden de trabajo?',
      ]
    case 'JEFE_UTIC':
      return [
        '¿Cuántos tickets nuevos están sin asignar?',
        '¿Cuál es la carga actual de los especialistas?',
        '¿Qué tickets tienen SLA próximo a vencer o vencido?',
        '¿Cuántos casos están pendientes de validación o cierre?',
        '¿Cómo reasigno un ticket a otro especialista?',
      ]
    case 'ENCARGADO_COMPRAS_ALMACEN':
      return [
        '¿Cuántas compras están en gestión de adquisición?',
        '¿Qué insumos o repuestos están por ingresar a almacén?',
        '¿Qué componentes están listos para entrega al técnico?',
        '¿Cómo emito un acta de recepción y conformidad?',
        '¿Cuál es el procedimiento de entrega de repuestos?',
      ]
    case 'DAF':
    case 'JEFE_DAF':
      return [
        '¿Cuántas solicitudes de compra requieren certificación presupuestaria?',
        '¿Cuáles compras están pendientes de autorización preventiva?',
        '¿Qué solicitudes superan el límite de caja chica?',
        '¿Cómo emito la certificación presupuestaria DAF?',
        '¿Cuál es el presupuesto total comprometido en compras?',
      ]
    case 'TESORERIA':
      return [
        '¿Cuántas solicitudes autorizadas están pendientes de pago?',
        '¿Cuáles compras fueron desembolsadas recientemente?',
        '¿Cuáles son los límites vigentes del fondo rotatorio / caja chica?',
        '¿Cómo registro el comprobante de desembolso y pago?',
        '¿Qué documentación de respaldo exige tesorería?',
      ]
    case 'ADMIN':
    case 'SUPERUSER':
    case 'DIRECTOR':
      return [
        '¿Cuál es el resumen ejecutivo del sistema hoy?',
        '¿Cuántos tickets y mantenimientos activos hay en la EMI?',
        '¿Hay alertas de SLA o incidencias críticas pendientes?',
        '¿Cuál es el estado global de compras y presupuesto?',
        '¿Cómo gestiono usuarios, roles o permisos en el sistema?',
      ]
    case 'SOLICITANTE':
    case 'JEFE_CARRERA':
    default:
      return [
        '¿Cuántos tickets tengo en proceso de atención?',
        '¿Cuáles de mis solicitudes requieren validación o conformidad?',
        '¿Cuál es el estado general de mis requerimientos?',
        '¿Cómo reporto una falla técnica de soporte en mi área?',
        '¿Cómo solicito un trabajo de mantenimiento de infraestructura?',
      ]
  }
})

/* ============================================================
   HELPERS
============================================================ */
function horaActual() {
  return new Date().toLocaleTimeString('es-BO', { hour: '2-digit', minute: '2-digit' })
}

function formatearTexto(texto) {
  if (!texto) return ''
  return texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

async function scrollAbajo() {
  await nextTick()
  if (contenedorMensajes.value) {
    contenedorMensajes.value.scrollTop = contenedorMensajes.value.scrollHeight
  }
}

function ajustarAltura() {
  if (!inputRef.value) return
  inputRef.value.style.height = 'auto'
  inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 120) + 'px'
}

/* ============================================================
   RECONOCIMIENTO DE VOZ (STT) Y SÍNTESIS (TTS)
============================================================ */
function inicializarReconocimiento() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) return null

  const rec = new SpeechRecognition()
  rec.lang = 'es-BO'
  rec.continuous = false
  rec.interimResults = false

  rec.onstart = () => {
    grabando.value = true
  }

  rec.onresult = (event) => {
    const transcripcion = event.results[0][0].transcript
    if (transcripcion) {
      mensajeActual.value = (mensajeActual.value ? mensajeActual.value + ' ' : '') + transcripcion
      ajustarAltura()
      // En modo llamada, enviar automáticamente cuando termina de hablar
      if (modoLlamada.value) {
        nextTick(() => enviarMensaje())
      }
    }
  }

  rec.onerror = (err) => {
    console.warn('Reconocimiento de voz:', err.error)
    grabando.value = false
    if (modoLlamada.value && err.error !== 'aborted') {
      // Reintentar escuchar si está en modo llamada
      setTimeout(() => {
        if (modoLlamada.value && !hablando.value) iniciarEscucha()
      }, 1000)
    }
  }

  rec.onend = () => {
    grabando.value = false
    reconocimiento = null
  }

  return rec
}

function iniciarEscucha() {
  if (hablando.value) return
  try {
    if (reconocimiento) {
      try { reconocimiento.abort() } catch {}
      reconocimiento = null
    }
    reconocimiento = inicializarReconocimiento()
    if (reconocimiento) {
      reconocimiento.start()
    }
  } catch (e) {
    console.warn('Error al iniciar escucha:', e)
    grabando.value = false
  }
}

function detenerEscucha() {
  if (reconocimiento) {
    try { reconocimiento.abort() } catch {}
    reconocimiento = null
  }
  grabando.value = false
}

function toggleGrabacionManual() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    alert('Tu navegador actual no admite Web Speech API para reconocimiento de voz. Te recomendamos Google Chrome o Microsoft Edge.')
    return
  }

  if (grabando.value) {
    detenerEscucha()
  } else {
    iniciarEscucha()
  }
}

function hablarTexto(texto, callbackAlTerminar = null) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()

  const limpio = texto
    .replace(/<[^>]*>?/gm, '')
    .replace(/[*_#`~•]/g, ' ')
    .replace(/\n/g, ' ')
    .trim()

  const utter = new SpeechSynthesisUtterance(limpio)
  utter.lang = 'es-BO'
  utter.rate = 1.05

  utter.onstart = () => {
    hablando.value = true
    detenerEscucha()
  }

  utter.onend = () => {
    hablando.value = false
    if (callbackAlTerminar) {
      callbackAlTerminar()
    }
  }

  utter.onerror = () => {
    hablando.value = false
  }

  window.speechSynthesis.speak(utter)
}

function toggleModoLlamada() {
  modoLlamada.value = !modoLlamada.value
  if (modoLlamada.value) {
    // Iniciar llamada continua
    iniciarEscucha()
  } else {
    detenerVozTotal()
  }
}

function detenerVozTotal() {
  detenerEscucha()
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel()
  }
  hablando.value = false
}

/* ============================================================
   ACCIONES
============================================================ */
function toggleChat() {
  abierto.value = !abierto.value
  if (abierto.value) {
    hayMensajeNuevo.value = false
    nextTick(() => inputRef.value?.focus())
  } else {
    detenerVozTotal()
    modoLlamada.value = false
  }
}

function limpiarChat() {
  mensajes.value = []
  errorConexion.value = false
  detenerVozTotal()
}

function usarSugerencia(texto) {
  mensajeActual.value = texto
  enviarMensaje()
}

async function enviarMensaje() {
  const texto = mensajeActual.value.trim()
  if (!texto || cargando.value) return

  detenerEscucha()

  mensajes.value.push({ rol: 'usuario', texto, hora: horaActual() })
  mensajeActual.value = ''
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
  await scrollAbajo()

  cargando.value = true
  errorConexion.value = false

  try {
    const res = await fetch('/api/asistente/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token.value}`,
      },
      body: JSON.stringify({ mensaje: texto }),
    })

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }

    const data = await res.json()
    const respuesta = data.respuesta || 'No obtuve respuesta del servidor.'

    mensajes.value.push({ rol: 'bot', texto: respuesta, hora: horaActual() })

    // Si está en modo llamada, reproducir automáticamente y luego volver a escuchar
    if (modoLlamada.value) {
      hablarTexto(respuesta, () => {
        if (modoLlamada.value) {
          setTimeout(() => iniciarEscucha(), 600)
        }
      })
    }

    if (!abierto.value) {
      hayMensajeNuevo.value = true
    }

  } catch (err) {
    errorConexion.value = true
    mensajes.value.push({
      rol: 'bot',
      texto: 'En este momento no puedo conectarme con el asistente IA. Por favor intenta en unos minutos.',
      hora: horaActual(),
    })
  } finally {
    cargando.value = false
    await scrollAbajo()
  }
}
</script>


<style scoped>
/* ============================================================
   BOTÓN FLOTANTE (FAB) — IDENTIDAD INSTITUCIONAL EMI / SIA
============================================================ */
.sia-fab {
  position: fixed !important;
  bottom: 28px !important;
  right: 28px !important;
  z-index: 999999 !important;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFC72C;
  border: 2px solid rgba(255, 199, 44, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 22px rgba(12, 42, 79, 0.45);
  transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease;
  outline: none;
}

.sia-fab:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 28px rgba(12, 42, 79, 0.6);
  border-color: #FFC72C;
}

.sia-fab--abierto {
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFC72C;
  border: 2px solid #FFC72C;
  box-shadow: 0 4px 18px rgba(12, 42, 79, 0.45);
}

.sia-fab__badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #FFC72C;
  border: 2px solid #0C2A4F;
  animation: pulso 1.5s infinite;
}

@keyframes pulso {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.35); opacity: 0.8; }
}


/* ============================================================
   VENTANA DE CHAT — ESTILO SISTEMA SIA
============================================================ */
.sia-ventana {
  position: fixed;
  bottom: 98px;
  right: 28px;
  z-index: 9998;
  width: 390px;
  max-height: 600px;
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  background: #FFFFFF;
  box-shadow: 0 14px 44px rgba(12, 42, 79, 0.28);
  border: 1px solid #D7E3EF;
  overflow: hidden;
  font-family: inherit;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), max-height 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sia-ventana--expandida {
  width: 620px;
  max-height: 720px;
}

@media (max-width: 660px) {
  .sia-ventana--expandida {
    width: calc(100vw - 24px);
    right: 12px;
  }
}

@media (max-width: 480px) {
  .sia-ventana {
    width: calc(100vw - 24px);
    right: 12px;
    bottom: 90px;
    max-height: 75vh;
  }
}

/* ---- Cabecera Azul Institucional ---- */
.sia-ventana__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFFFFF;
  flex-shrink: 0;
  border-bottom: 2px solid #FFC72C;
}

.sia-ventana__header-info {
  display: flex;
  align-items: center;
  gap: 11px;
}

.sia-ventana__avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 199, 44, 0.15);
  border: 1.5px solid #FFC72C;
  color: #FFC72C;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sia-ventana__titulo-box {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sia-ventana__nombre {
  display: block;
  font-weight: 700;
  font-size: 14.5px;
  line-height: 1.2;
  color: #FFFFFF;
  letter-spacing: 0.3px;
}

.sia-ventana__tag-ia {
  background: #FFC72C;
  color: #0C2A4F;
  font-weight: 800;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 8px;
  line-height: 1.3;
}

.sia-ventana__estado {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #C2DBF2;
}

.sia-ventana__estado-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #4CAF50;
  animation: pulso 2s infinite;
}

.sia-ventana__header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sia-ventana__btn-accion {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: #FFFFFF;
  cursor: pointer;
  padding: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sia-ventana__btn-accion:hover {
  background: rgba(255, 199, 44, 0.25);
  border-color: #FFC72C;
  color: #FFC72C;
}

.sia-ventana__btn-accion--modo-llamada {
  background: #FFC72C !important;
  color: #0C2A4F !important;
  border-color: #FFC72C !important;
  animation: pulso 1.3s infinite;
}

/* ---- Banner de Llamada / Conversación Continua ---- */
.sia-banner-llamada {
  background: linear-gradient(90deg, #FFF8DA 0%, #FFF0B8 100%);
  border-bottom: 1px solid #FFD760;
  padding: 8px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.sia-banner-llamada__pulso {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #B98F00;
  animation: pulso 1s infinite;
}

.sia-banner-llamada__texto {
  flex: 1;
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.sia-banner-llamada__texto strong {
  font-size: 11.5px;
  color: #0C2A4F;
}

.sia-banner-llamada__texto span {
  font-size: 10.5px;
  color: #5B7189;
}

.sia-banner-llamada__btn-salir {
  background: #0C2A4F;
  color: #FFFFFF;
  border: none;
  border-radius: 12px;
  font-size: 10.5px;
  padding: 4px 10px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.15s;
}

.sia-banner-llamada__btn-salir:hover {
  background: #123A6B;
}

/* ---- Área de Mensajes ---- */
.sia-ventana__mensajes {
  flex: 1;
  overflow-y: auto;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
  background: #F4F8FC;
}

.sia-ventana__mensajes::-webkit-scrollbar {
  width: 5px;
}
.sia-ventana__mensajes::-webkit-scrollbar-thumb {
  background: #C2DBF2;
  border-radius: 3px;
}

/* ---- Bienvenida ---- */
.sia-bienvenida {
  text-align: center;
  padding: 10px 6px;
}

.sia-bienvenida__icono {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFC72C;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  box-shadow: 0 4px 14px rgba(12, 42, 79, 0.2);
}

.sia-bienvenida__titulo {
  font-weight: 700;
  font-size: 15px;
  color: #0C2A4F;
  margin: 0 0 6px;
}

.sia-bienvenida__texto {
  font-size: 13px;
  color: #5B7189;
  line-height: 1.45;
  margin: 0 0 10px;
}

.sia-bienvenida__nota-voz {
  background: #FFF8DA;
  border: 1px dashed #FFD760;
  border-radius: 12px;
  padding: 7px 12px;
  font-size: 11.5px;
  color: #6A5200;
  margin-bottom: 12px;
}

.sia-sugerencias {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sia-sugerencia {
  background: #FFFFFF;
  border: 1px solid #D7E3EF;
  border-radius: 16px;
  padding: 8px 14px;
  font-size: 12.5px;
  color: #123A6B;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.sia-sugerencia:hover {
  background: #DDE9F5;
  border-color: #123A6B;
  transform: translateX(3px);
}

/* ---- Burbujas de Chat ---- */
.sia-mensaje {
  display: flex;
}

.sia-mensaje--usuario {
  justify-content: flex-end;
}

.sia-mensaje--bot {
  justify-content: flex-start;
}

.sia-mensaje__burbuja {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 13.5px;
  line-height: 1.48;
}

.sia-mensaje--usuario .sia-mensaje__burbuja {
  background: linear-gradient(135deg, #123A6B 0%, #0C2A4F 100%);
  color: #FFFFFF;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(12, 42, 79, 0.2);
}

.sia-mensaje--bot .sia-mensaje__burbuja {
  background: #FFFFFF;
  color: #14304F;
  border: 1px solid #D7E3EF;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.sia-mensaje__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 5px;
  gap: 8px;
}

.sia-mensaje__btn-escuchar {
  background: #F0F6FC;
  border: 1px solid #D7E3EF;
  color: #123A6B;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 10px;
  transition: all 0.15s;
}

.sia-mensaje__btn-escuchar:hover {
  background: #FFC72C;
  color: #0C2A4F;
  border-color: #B98F00;
}

.sia-mensaje__hora {
  font-size: 10px;
  opacity: 0.65;
  margin-left: auto;
}

/* ---- Indicador de escritura ---- */
.sia-mensaje__burbuja--typing {
  padding: 12px 18px;
}

.sia-typing {
  display: flex;
  gap: 5px;
  align-items: center;
}

.sia-typing span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #123A6B;
  animation: typing 1.2s infinite;
}

.sia-typing span:nth-child(2) { animation-delay: 0.2s; }
.sia-typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
  30%            { transform: translateY(-6px); opacity: 1; }
}

/* ---- Banner de Voz Activo ---- */
.sia-voz-activo-banner {
  background: #FFF8DA;
  color: #6A5200;
  font-size: 11.5px;
  font-weight: 500;
  padding: 8px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 1px solid #FFD760;
  flex-shrink: 0;
}

.sia-voz-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #E53935;
  animation: pulso 1s infinite;
}

/* ---- Banner de Error ---- */
.sia-error-banner {
  background: #FFF3E0;
  color: #E65100;
  font-size: 11.5px;
  padding: 6px 14px;
  text-align: center;
  flex-shrink: 0;
}

/* ---- Área de Entrada de Mensaje ---- */
.sia-ventana__input-area {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid #D7E3EF;
  background: #FFFFFF;
  flex-shrink: 0;
}

.sia-ventana__input {
  flex: 1;
  resize: none;
  border: 1.5px solid #D7E3EF;
  border-radius: 20px;
  padding: 9px 14px;
  font-size: 13.5px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  line-height: 1.4;
  max-height: 110px;
  overflow-y: auto;
  color: #14304F;
  background: #F4F8FC;
}

.sia-ventana__input:focus {
  border-color: #123A6B;
  background: #FFFFFF;
}

/* Botón Modo Conversación Continua por Voz (Persona hablando) */
.sia-ventana__btn-voz-continua {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #F0F6FC;
  color: #123A6B;
  border: 1.5px solid #D7E3EF;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.sia-ventana__btn-voz-continua:hover {
  background: #DDE9F5;
  border-color: #123A6B;
  color: #0C2A4F;
}

.sia-ventana__btn-voz-continua--activo {
  background: #FFC72C !important;
  color: #0C2A4F !important;
  border-color: #B98F00 !important;
  animation: pulso 1.3s infinite;
}

/* Botón Micrófono */
.sia-ventana__btn-mic {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #F0F6FC;
  color: #123A6B;
  border: 1.5px solid #D7E3EF;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.sia-ventana__btn-mic:hover {
  background: #DDE9F5;
  border-color: #123A6B;
  color: #0C2A4F;
}

.sia-ventana__btn-mic--grabando {
  background: #E53935 !important;
  color: #FFFFFF !important;
  border-color: #C62828 !important;
  animation: pulso 1s infinite;
}

/* Botón Enviar */
.sia-ventana__btn-enviar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFC72C;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.15s, opacity 0.15s;
}

.sia-ventana__btn-enviar:hover:not(:disabled) {
  transform: scale(1.06);
}

.sia-ventana__btn-enviar:disabled {
  background: #D7E3EF;
  color: #8CA0B4;
  cursor: not-allowed;
}

.sia-ventana__subhint {
  font-size: 10.5px;
  color: #8CA0B4;
  text-align: center;
  padding: 0 10px 8px;
  background: #FFFFFF;
  flex-shrink: 0;
}

/* Transición */
.sia-slide-enter-active,
.sia-slide-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.sia-slide-enter-from,
.sia-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.97);
}
</style>
