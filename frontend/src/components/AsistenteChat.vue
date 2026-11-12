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
  <div v-if="estaAutenticado" class="sia-asistente-raiz">

    <!-- ===================================================
         BURBUJA DE VOZ (visible con el chat cerrado)
    =================================================== -->
    <transition name="sia-fade">
      <div
        v-if="!abierto && burbujaVisible"
        class="sia-burbuja-voz"
        :class="'sia-burbuja-voz--' + estadoVoz"
        role="status"
        aria-live="polite"
      >
        <div class="sia-burbuja-voz__cabecera">
          <span class="sia-burbuja-voz__onda" aria-hidden="true"><i></i><i></i><i></i><i></i></span>
          <strong>{{ textoEstadoVoz }}</strong>
          <button class="sia-burbuja-voz__cerrar" @click="cancelarConversacion" title="Cancelar (Esc)" aria-label="Cancelar">×</button>
        </div>
        <p v-if="textoBurbuja" class="sia-burbuja-voz__texto">{{ textoBurbuja }}</p>
      </div>
    </transition>

    <!-- Aviso de voz con el chat cerrado (permisos, conexión) -->
    <transition name="sia-fade">
      <div v-if="avisoVoz && !abierto" class="sia-aviso-voz" role="alert">
        <span>{{ avisoVoz }}</span>
        <button @click="avisoVoz = ''" aria-label="Cerrar aviso">×</button>
      </div>
    </transition>

    <!-- ===================================================
         BOTÓN FLOTANTE (FAB)
    =================================================== -->
    <button
      class="sia-fab"
      :class="{
        'sia-fab--abierto': abierto,
        'sia-fab--espera': estadoVoz === 'espera' && !abierto,
        'sia-fab--voz': burbujaVisible && !abierto,
      }"
      @click="toggleChat"
      :title="abierto ? 'Cerrar asistente' : (estadoVoz === 'espera' ? `Di «Oye ${NOMBRE_ASISTENTE}» o haz clic para abrir` : `Abrir a ${NOMBRE_ASISTENTE}`)"
      :aria-label="`Asistente ${NOMBRE_ASISTENTE}`"
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
      <!-- Indicador "escuchando en segundo plano" -->
      <span v-if="estadoVoz === 'espera' && !abierto" class="sia-fab__oido" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="11" height="11">
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
          <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
      </span>
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
        :aria-label="`Asistente ${NOMBRE_ASISTENTE}`"
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
                <span class="sia-ventana__nombre">{{ NOMBRE_ASISTENTE }} · Asistente SIA</span>
                <span class="sia-ventana__tag-ia">IA</span>
              </div>
              <span class="sia-ventana__estado">
                <span class="sia-ventana__estado-dot"></span>
                {{ vozActiva ? `Di «Oye ${NOMBRE_ASISTENTE}» para hablarme` : 'En línea · Soporte Institucional' }}
              </span>
            </div>
          </div>

          <!-- Acciones de cabecera -->
          <div class="sia-ventana__header-actions">
            <!-- Interruptor de activación por voz ("Oye Tati") -->
            <button
              class="sia-ventana__btn-accion"
              :class="{ 'sia-ventana__btn-accion--activo': vozActiva }"
              @click="toggleVozActiva"
              :aria-pressed="vozActiva"
              :title="vozActiva ? `Activación por voz ENCENDIDA (clic para apagar)` : `Encender activación por voz: di «Oye ${NOMBRE_ASISTENTE}»`"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M17 20c-.29 0-.56-.06-.76-.15-.71-.37-1.21-.88-1.71-2.38-.51-1.56-1.47-2.29-2.39-3-.79-.61-1.61-1.24-2.32-2.53C9.29 10.98 9 9.93 9 9c0-2.8 2.2-5 5-5s5 2.2 5 5h2c0-3.93-3.07-7-7-7S7 5.07 7 9c0 1.26.38 2.65 1.07 3.9.91 1.65 1.98 2.48 2.85 3.15.81.62 1.39 1.07 1.71 2.05.6 1.82 1.37 2.84 2.73 3.55.51.23 1.07.35 1.64.35 2.21 0 4-1.79 4-4h-2c0 1.1-.9 2-2 2zM7.64 2.64L6.22 1.22C4.23 3.21 3 5.96 3 9s1.23 5.79 3.22 7.78l1.41-1.41C6.01 13.74 5 11.49 5 9s1.01-4.74 2.64-6.36zM11.5 9c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5-1.12-2.5-2.5-2.5-2.5 1.12-2.5 2.5z"/>
              </svg>
            </button>

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
            <strong>Conversación por voz con {{ NOMBRE_ASISTENTE }}</strong>
            <span>{{ hablando ? `${NOMBRE_ASISTENTE} está hablando...` : (estadoVoz === 'pensando' ? 'Pensando...' : (transcripcionParcial || 'Te escucho...')) }}</span>
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
              <template v-if="vozActiva">
                🎙️ Activación por voz encendida: di <strong>«Oye {{ NOMBRE_ASISTENTE }}»</strong> en cualquier pantalla y te respondo.
              </template>
              <template v-else-if="soportaReconocimiento">
                💡 Puedes escribir, dictar con el micrófono o
                <button type="button" class="sia-bienvenida__link" @click="toggleVozActiva">encender la activación por voz</button>
                para llamarme diciendo <strong>«Oye {{ NOMBRE_ASISTENTE }}»</strong>.
              </template>
              <template v-else>
                💡 Para hablar con {{ NOMBRE_ASISTENTE }} por voz usa Google Chrome o Microsoft Edge.
              </template>
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
                  @click="leerMensaje(msg.texto)"
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

        <!-- Banner de voz (dictado o conversación iniciada con "Oye Tati") -->
        <div v-if="(dictando || estadoVoz === 'escuchando' || hablando) && !modoLlamada" class="sia-voz-activo-banner">
          <span class="sia-voz-dot"></span>
          <span class="sia-voz-activo-banner__texto">
            <template v-if="dictando">{{ mensajeActual ? 'Dictando…' : 'Escuchando… di tu consulta' }}</template>
            <template v-else-if="hablando">{{ NOMBRE_ASISTENTE }} está hablando…</template>
            <template v-else>{{ transcripcionParcial || 'Le escucho, mi señor… ordene' }}</template>
          </span>
          <button
            v-if="!dictando"
            class="sia-voz-activo-banner__btn"
            @click="cancelarConversacion"
            title="Cancelar (Esc)"
          >{{ hablando ? 'Detener' : 'Cancelar' }}</button>
        </div>

        <!-- Aviso de voz (permisos, conexión) -->
        <div v-if="avisoVoz" class="sia-error-banner sia-error-banner--voz">
          <span>🎙️ {{ avisoVoz }}</span>
          <button @click="avisoVoz = ''" aria-label="Cerrar aviso">×</button>
        </div>

        <!-- Banner de Error -->
        <div v-if="errorConexion" class="sia-error-banner">
          ⚠️ No se pudo conectar con el servidor. Intenta nuevamente en unos segundos.
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
            @input="ajustarAltura"
            maxlength="2000"
          ></textarea>

          <!-- BOTÓN MODO LLAMADA / CONVERSACIÓN CONTINUA (PERSONA HABLANDO) -->
          <button
            type="button"
            class="sia-ventana__btn-voz-continua"
            :class="{ 'sia-ventana__btn-voz-continua--activo': modoLlamada }"
            @click="toggleModoLlamada"
            :title="modoLlamada ? 'Conversación por voz ACTIVA (clic para terminar)' : `Conversar por voz con ${NOMBRE_ASISTENTE} sin decir su nombre cada vez`"
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
            :class="{ 'sia-ventana__btn-mic--grabando': dictando }"
            @click="toggleGrabacionManual"
            :title="dictando ? 'Detener dictado' : 'Dictar consulta por voz (Micrófono)'"
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
          <span>{{ vozActiva ? `🎙️ Di «Oye ${NOMBRE_ASISTENTE}» · Esc para cancelar · Enter para enviar` : '🎙️ Presiona el micrófono para dictar · Enter para enviar' }}</span>
        </div>

      </div>
    </transition>
  </div>
</template>


<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NOMBRE_ASISTENTE, detectarPalabraActivacion, restoOriginal, detectarComando,
  limpiarParaVoz, elegirVoz, frasesParaVoz, describirPantalla, dividirEnFrases, extraerFrases,
  buscarOpcionMenu, refiereAPantalla, opcionesMenu, esEco, esOrdenDeParar,
} from '../utils/voz.js'

const route = useRoute()
const router = useRouter()

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
const modoLlamada     = ref(false)

const contenedorMensajes = ref(null)
const inputRef           = ref(null)

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
      return 'Soy Tati, tu asistente técnica de SIA para Mantenimiento. Te ayudo a consultar tus órdenes de trabajo asignadas, recepción de componentes en almacén, diagnósticos y reportes.'
    case 'ESPECIALISTA':
      return 'Soy Tati, tu asistente técnica de SIA para Soporte UTIC. Te ayudo a monitorear tus tickets asignados, tiempos de SLA, diagnóstico de incidentes y registro de soluciones.'
    case 'SERVICIOS_GENERALES':
      return 'Soy Tati, tu asistente de gestión de SIA para la Jefatura de Mantenimiento. Te ayudo en la clasificación de solicitudes, supervisión de órdenes en infraestructura y aprobación de informes técnicos.'
    case 'JEFE_UTIC':
      return 'Soy Tati, tu asistente de supervisión de SIA para la Jefatura UTIC. Te ayudo con la asignación de tickets, control de carga de especialistas y monitoreo de SLAs.'
    case 'ENCARGADO_COMPRAS_ALMACEN':
      return 'Soy Tati, tu asistente operativa de SIA para Almacén y Adquisiciones. Te ayudo a dar seguimiento a órdenes de compra, actas de recepción y entrega de componentes a los técnicos.'
    case 'DAF':
    case 'JEFE_DAF':
      return 'Soy Tati, tu asistente financiera de SIA para la DAF. Te ayudo a revisar certificaciones presupuestarias, autorizaciones de compra y control de fondos.'
    case 'TESORERIA':
      return 'Soy Tati, tu asistente financiera de SIA para Tesorería. Te ayudo a controlar órdenes autorizadas para pago, desembolsos y fondos rotatorios.'
    case 'ADMIN':
    case 'SUPERUSER':
    case 'DIRECTOR':
      return 'Soy Tati, tu asistente ejecutiva y administrativa de SIA. Te brindo una visión integral de operaciones, métricas globales, seguridad y configuración institucional.'
    case 'SOLICITANTE':
    case 'JEFE_CARRERA':
    default:
      return 'Soy Tati, la asistente inteligente del SIA. Puedo orientarte sobre tus tickets activos, procedimientos de mantenimiento, compras y reglas operativas del sistema.'
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
   MOTOR DE VOZ — "Oye Tati"
   ------------------------------------------------------------
   Estados (estadoVoz):
     inactivo   → no escucha nada.
     espera     → escucha en segundo plano esperando el nombre "Tati".
     escuchando → captura la consulta del usuario.
     pensando   → consultando al servidor.
     hablando   → Tati lee la respuesta (el micrófono se pausa para
                  no escucharse a sí misma).
   Un único reconocedor activo a la vez: cada instancia comprueba
   `rec === r` antes de actuar, así los eventos tardíos de una
   instancia anterior nunca pisan a la nueva.
============================================================ */
const SpeechRecognitionAPI = typeof window !== 'undefined'
  ? (window.SpeechRecognition || window.webkitSpeechRecognition)
  : null
const soportaReconocimiento = !!SpeechRecognitionAPI
const soportaSintesis = typeof window !== 'undefined' && 'speechSynthesis' in window
const CLAVE_PREF_VOZ = 'sia_voz_activa'
const MENSAJE_SIN_SOPORTE = 'Tu navegador no permite el reconocimiento de voz. Usa Google Chrome o Microsoft Edge.'
const MENSAJE_SIN_HTTPS = 'El micrófono solo funciona con una conexión segura (https:// o localhost). Pide que el sistema se publique con HTTPS.'

/** Comprueba que el navegador y la conexión permitan usar el micrófono; si no, muestra el motivo. */
function puedeUsarMicrofono() {
  if (!soportaReconocimiento) { avisoVoz.value = MENSAJE_SIN_SOPORTE; return false }
  if (typeof window !== 'undefined' && window.isSecureContext === false) { avisoVoz.value = MENSAJE_SIN_HTTPS; return false }
  return true
}

function leerPreferenciaVoz() {
  try { return localStorage.getItem(CLAVE_PREF_VOZ) === '1' } catch { return false }
}
function guardarPreferenciaVoz(valor) {
  try { localStorage.setItem(CLAVE_PREF_VOZ, valor ? '1' : '0') } catch {}
}

const vozActiva            = ref(soportaReconocimiento && window.isSecureContext !== false && leerPreferenciaVoz())
const estadoVoz            = ref('inactivo')
const dictando             = ref(false)
const transcripcionParcial = ref('')
const textoHablando        = ref('')
const avisoVoz             = ref('')

const hablando = computed(() => estadoVoz.value === 'hablando')

const burbujaVisible = computed(() => ['escuchando', 'pensando', 'hablando'].includes(estadoVoz.value))
const textoEstadoVoz = computed(() => {
  switch (estadoVoz.value) {
    case 'escuchando': return transcripcionParcial.value ? 'Le escucho…' : 'Ordene, ¿en qué puedo ayudarle?'
    case 'pensando':   return 'Pensando…'
    case 'hablando':   return `${NOMBRE_ASISTENTE} está hablando`
    default:           return ''
  }
})
const textoBurbuja = computed(() => {
  if (estadoVoz.value === 'hablando') {
    const t = limpiarParaVoz(textoHablando.value)
    return t.length > 240 ? t.slice(0, 237) + '…' : t
  }
  return transcripcionParcial.value
})

let rec = null
let finHablaEn = 0
let ultimoDicho = ''
let idiomaReconocimiento = 'es-BO'
let fallosSeguidos = 0
let errorEnSesion = false
let bufferConsulta = ''
let textoBaseDictado = ''
let turnoVoz = 0
let ultimaActivacion = 0
let tReinicio = null, tSilencio = null, tSinVoz = null, tActivacion = null

function limpiarTimers() {
  clearTimeout(tSilencio); clearTimeout(tSinVoz); clearTimeout(tActivacion)
  tSilencio = tSinVoz = tActivacion = null
}

const estadoReposo = () => (vozActiva.value ? 'espera' : 'inactivo')

function debeEscuchar() {
  if (!soportaReconocimiento || !estaAutenticado.value) return false
  // Solo escucha la pestaña visible y activa (con varias pestañas del SIA, responde una sola).
  if (typeof document !== 'undefined' && document.visibilityState === 'hidden') return false
  if (!esPestanaActiva()) return false
  if (estadoVoz.value === 'hablando' || estadoVoz.value === 'pensando') {
    // Mientras habla o piensa sigue escuchando, solo para "Tati…" o "para" (interrumpir).
    return !dictando.value && (vozActiva.value || modoLlamada.value)
  }
  return dictando.value || estadoVoz.value === 'escuchando' || estadoVoz.value === 'espera'
}

/* ---------------- Una sola pestaña escuchando ---------------- */
const ID_PESTANA = Math.random().toString(36).slice(2)
const CLAVE_PESTANA = 'sia_voz_pestana'
function reclamarPestana() {
  try { localStorage.setItem(CLAVE_PESTANA, ID_PESTANA) } catch {}
}
function esPestanaActiva() {
  try {
    const v = localStorage.getItem(CLAVE_PESTANA)
    return !v || v === ID_PESTANA
  } catch { return true }
}
function alCambiarPestanaActiva(e) {
  if (e.key !== CLAVE_PESTANA) return
  if (!e.newValue && document.visibilityState === 'visible') {
    // La pestaña que escuchaba se cerró: esta toma el relevo.
    reclamarPestana()
    programarReinicio(300)
  } else if (!esPestanaActiva()) {
    // Otra pestaña del SIA pasó a primer plano: esta deja de escuchar.
    if (['escuchando', 'pensando', 'hablando'].includes(estadoVoz.value)) cancelarConversacion()
    detenerReconocimiento()
  }
}
function soltarPestana() {
  try { if (localStorage.getItem(CLAVE_PESTANA) === ID_PESTANA) localStorage.removeItem(CLAVE_PESTANA) } catch {}
}

/* ---------------- Reconocimiento (micrófono) ---------------- */
function arrancarReconocimiento() {
  clearTimeout(tReinicio)
  if (rec || !debeEscuchar()) return

  const r = new SpeechRecognitionAPI()
  r.lang = idiomaReconocimiento
  r.continuous = true
  r.interimResults = true
  r.maxAlternatives = 3

  r.onstart = () => { errorEnSesion = false }
  r.onresult = (e) => {
    if (rec !== r) return
    fallosSeguidos = 0
    if (avisoVoz.value.startsWith('Sin conexión')) avisoVoz.value = ''
    procesarResultado(e)
  }
  r.onerror = (e) => { if (rec === r) manejarErrorReconocimiento(e.error) }
  r.onend = () => {
    if (rec !== r) return
    rec = null
    if (!errorEnSesion) fallosSeguidos = 0
    // Chrome corta la escucha continua cada cierto tiempo: se reanuda sola.
    programarReinicio(fallosSeguidos ? Math.min(500 * 2 ** fallosSeguidos, 15000) : 250)
  }

  rec = r
  try {
    r.start()
  } catch (err) {
    console.warn('No se pudo iniciar el micrófono:', err)
    rec = null
    fallosSeguidos++
    programarReinicio(1000)
  }
}

function programarReinicio(ms = 250) {
  clearTimeout(tReinicio)
  if (debeEscuchar()) tReinicio = setTimeout(arrancarReconocimiento, ms)
}

function detenerReconocimiento() {
  clearTimeout(tReinicio)
  const r = rec
  rec = null
  if (r) { try { r.abort() } catch {} }
}

function manejarErrorReconocimiento(error) {
  switch (error) {
    case 'no-speech':
    case 'aborted':
      return // normal: nadie habló o se reinició a propósito
    case 'not-allowed':
    case 'service-not-allowed':
      apagarVozPorError(`${NOMBRE_ASISTENTE} no tiene permiso para usar el micrófono. Permítelo desde el candado de la barra de direcciones y vuelve a activar la voz.`)
      return
    case 'audio-capture':
      apagarVozPorError('No se detectó ningún micrófono. Conecta uno y vuelve a activar la voz.')
      return
    case 'language-not-supported':
      idiomaReconocimiento = 'es-ES'
      return
    case 'network':
      errorEnSesion = true
      fallosSeguidos++
      if (fallosSeguidos >= 2) avisoVoz.value = 'Sin conexión con el servicio de voz. Reintentando…'
      return
    default:
      errorEnSesion = true
      fallosSeguidos++
      console.warn('Reconocimiento de voz:', error)
  }
}

function apagarVozPorError(mensaje) {
  vozActiva.value = false
  guardarPreferenciaVoz(false)
  modoLlamada.value = false
  dictando.value = false
  limpiarTimers()
  detenerHabla()
  detenerReconocimiento()
  estadoVoz.value = 'inactivo'
  avisoVoz.value = mensaje
}

function procesarResultado(e) {
  let finalTxt = ''
  let interino = ''
  const alternativas = []
  for (let i = e.resultIndex; i < e.results.length; i++) {
    const res = e.results[i]
    if (res.isFinal) {
      finalTxt += res[0].transcript + ' '
      for (let k = 1; k < res.length; k++) alternativas.push(res[k].transcript)
    } else {
      interino += res[0].transcript + ' '
    }
  }
  finalTxt = finalTxt.trim()
  interino = interino.trim()

  if (dictando.value) return manejarDictado(finalTxt, interino)
  if (estadoVoz.value === 'hablando' || estadoVoz.value === 'pensando') return manejarInterrupcion(finalTxt, alternativas)
  if (estadoVoz.value === 'espera') return buscarPalabraActivacion(finalTxt, interino, alternativas)
  if (estadoVoz.value === 'escuchando') return acumularConsulta(finalTxt, interino)
}

/* ---------------- Interrumpir a Tati ("Tati…", "para", "silencio") ---------------- */
function manejarInterrupcion(finalTxt, alternativas) {
  if (!finalTxt) return
  const dicho = estadoVoz.value === 'hablando' ? textoHablando.value : ''
  for (const texto of [finalTxt, ...alternativas]) {
    if (esEco(texto, dicho)) continue // es su propia voz captada por los parlantes
    if (esOrdenDeParar(texto)) {
      ++turnoVoz
      if (controlConsulta) { controlConsulta.porUsuario = true; controlConsulta.abort() }
      detenerHabla()
      if (modoLlamada.value) pasarAEscuchar(0)
      else volverAReposo()
      return
    }
    const det = detectarPalabraActivacion(texto)
    if (det.detectado) {
      ++turnoVoz
      if (controlConsulta) { controlConsulta.porUsuario = true; controlConsulta.abort() }
      detenerHabla()
      detenerReconocimiento()
      ultimaActivacion = 0
      activarAsistente(restoOriginal(texto, det.resto))
      return
    }
  }
}

/* ---------------- Palabra de activación ---------------- */
function buscarPalabraActivacion(finalTxt, interino, alternativas) {
  clearTimeout(tActivacion)
  const candidatos = finalTxt ? [finalTxt, ...alternativas] : [interino]
  for (const texto of candidatos) {
    const det = detectarPalabraActivacion(texto)
    if (!det.detectado) continue
    const resto = restoOriginal(texto, det.resto)
    if (finalTxt) {
      activarAsistente(resto)
    } else {
      // Resultado provisional: si el usuario deja de hablar 1,2 s, se activa igual.
      tActivacion = setTimeout(() => activarAsistente(resto), 1200)
    }
    return
  }
}

function activarAsistente(resto) {
  const ahora = Date.now()
  if (ahora - ultimaActivacion < 700) return // evita doble disparo (provisional + final)
  ultimaActivacion = ahora
  clearTimeout(tActivacion)
  avisoVoz.value = ''
  sonarTono()

  if (resto && detectarComando(resto)?.tipo !== 'saludo') {
    procesarConsulta(resto)
  } else {
    decirYEscuchar(frasesSaludo(), 8000)
  }
}

/* ---------------- Captura de la consulta ---------------- */
function acumularConsulta(finalTxt, interino) {
  // Los primeros segundos tras hablar, el micrófono puede captar el final de su propia voz.
  if (Date.now() - finHablaEn < 2500 && ultimoDicho && esEco(finalTxt || interino, ultimoDicho)) return
  if (finalTxt) bufferConsulta = `${bufferConsulta} ${finalTxt}`.trim()
  transcripcionParcial.value = `${bufferConsulta} ${interino}`.trim()
  if (!transcripcionParcial.value) return
  clearTimeout(tSinVoz)
  clearTimeout(tSilencio)
  // Tras una pausa breve se considera terminada la frase.
  tSilencio = setTimeout(finalizarConsulta, interino ? 2000 : 1100)
}

function finalizarConsulta() {
  let texto = (bufferConsulta || transcripcionParcial.value).trim()
  const det = detectarPalabraActivacion(texto)
  if (det.detectado) texto = restoOriginal(texto, det.resto)
  if (!texto || detectarComando(texto)?.tipo === 'saludo') {
    decirYEscuchar(FRASE_DIME, 8000)
    return
  }
  sonarTono('fin') // "te escuché"
  procesarConsulta(texto)
}

function pasarAEscuchar(timeoutMs) {
  limpiarTimers()
  // Sesión de micrófono nueva: lo oído mientras hablaba no se mezcla con la pregunta.
  detenerReconocimiento()
  bufferConsulta = ''
  transcripcionParcial.value = ''
  textoHablando.value = ''
  estadoVoz.value = 'escuchando'
  if (timeoutMs) {
    tSinVoz = setTimeout(() => {
      if (estadoVoz.value === 'escuchando' && !transcripcionParcial.value) volverAReposo()
    }, timeoutMs)
  }
  // Pausa corta para que el micrófono no capte el final de la voz de Tati.
  programarReinicio(300)
}

function volverAReposo() {
  limpiarTimers()
  detenerReconocimiento()
  bufferConsulta = ''
  transcripcionParcial.value = ''
  textoHablando.value = ''
  estadoVoz.value = estadoReposo()
  programarReinicio(300)
}

async function decirYEscuchar(texto, timeoutMs) {
  limpiarTimers()
  detenerReconocimiento()
  const turno = ++turnoVoz
  estadoVoz.value = 'hablando'
  const completo = await hablar(texto)
  if (!completo || turno !== turnoVoz) return
  pasarAEscuchar(timeoutMs)
}

async function procesarConsulta(texto) {
  limpiarTimers()
  detenerReconocimiento()
  bufferConsulta = ''
  transcripcionParcial.value = texto
  estadoVoz.value = 'pensando'
  const turno = ++turnoVoz

  // Órdenes locales (describir pantalla, navegar, repetir…): respuesta instantánea, sin IA.
  const comando = detectarComando(texto)
  if (comando?.tipo === 'detener') { volverAReposo(); return }
  let seguirEscuchando = true
  let respuesta
  const local = comando ? ejecutarComando(comando) : null
  if (local) {
    seguirEscuchando = local.seguir
    respuesta = local.respuesta
    registrarIntercambio(texto, respuesta)
  }

  let completo
  if (local) {
    if (turno !== turnoVoz) return
    estadoVoz.value = 'hablando'
    completo = await hablar(respuesta)
  } else {
    completo = await consultarYHablar(texto, turno)
  }
  if (!completo || turno !== turnoVoz) return

  if (modoLlamada.value) pasarAEscuchar(0)                            // llamada: sigue escuchando sin límite
  else if (vozActiva.value && seguirEscuchando) pasarAEscuchar(7000)  // unos segundos para una pregunta de seguimiento
  else volverAReposo()
}

/**
 * Consulta a la IA y Tati empieza a hablar en cuanto llega la primera frase
 * completa (no espera la respuesta entera). Devuelve lo mismo que hablar().
 */
async function consultarYHablar(texto, turno) {
  const mio = ++idHabla
  detenerSalidaAudio()
  textoHablando.value = ''
  const cola = crearColaFrases()
  let caracteres = 0
  let recortado = false
  let hubo = false

  const encolar = (fragmento) => {
    if (recortado || mio !== idHabla) return
    for (const frase of dividirEnFrases(limpiarParaVoz(fragmento), 180)) {
      if (caracteres + frase.length > LIMITE_VOZ) {
        recortado = true
        cola.push(AVISO_DETALLE_CHAT)
        break
      }
      caracteres += frase.length
      cola.push(frase)
      textoHablando.value = `${textoHablando.value} ${frase}`.trim()
    }
    hubo = true
    if (estadoVoz.value === 'pensando' && turno === turnoVoz) estadoVoz.value = 'hablando'
  }

  const reproduccion = reproducirFrases(cola, mio)
  // Si la IA tarda, Tati avisa en vez de quedarse en silencio.
  const espera = setTimeout(() => {
    if (!hubo && mio === idHabla && turno === turnoVoz) {
      cola.push(FRASE_ESPERA)
      textoHablando.value = FRASE_ESPERA
      if (estadoVoz.value === 'pensando') estadoVoz.value = 'hablando'
    }
  }, 2500)
  const respuesta = await consultarServidor(texto, { voz: true, alFrase: encolar })
  clearTimeout(espera)
  if (!hubo) encolar(respuesta) // respuesta sin streaming (error o respaldo)
  textoHablando.value = respuesta
  cola.cerrar()
  return reproduccion
}

/* ---------------- Órdenes locales ---------------- */
const NOMBRES_DESTINO = {
  dashboard: 'el inicio',
  notificaciones: 'tus notificaciones',
  'mis-solicitudes': 'tus solicitudes',
  soporte: 'soporte técnico',
  mantenimiento: 'mantenimiento',
  compras: 'compras',
  perfil: 'tu perfil',
  configuracion: 'la configuración',
}

/** Busca la ruta de una sección según el área (rol) en la que está el usuario. */
function rutaDestino(destino) {
  const prefijo = (route.path || '').split('/')[1] || 'usuario'
  const candidatos = {
    dashboard: [`/${prefijo}/dashboard`],
    notificaciones: [`/${prefijo}/notificaciones`],
    'mis-solicitudes': [`/${prefijo}/mis-solicitudes`],
    soporte: [`/${prefijo}/soporte`, `/${prefijo}/tickets`],
    mantenimiento: [`/${prefijo}/mantenimiento`],
    compras: [`/${prefijo}/compras`, `/${prefijo}/requerimientos`],
    perfil: [`/${prefijo}/perfil`],
    configuracion: [`/${prefijo}/configuracion`, `/${prefijo}/preferencias`],
  }[destino] || []
  for (const ruta of candidatos) {
    try {
      const r = router.resolve(ruta)
      if (r.matched.length && !r.matched.some(m => m.path.includes(':pathMatch'))) return ruta
    } catch {}
  }
  return null
}

function ultimaRespuestaBot() {
  for (let i = mensajes.value.length - 1; i >= 0; i--) {
    if (mensajes.value[i].rol === 'bot') return mensajes.value[i].texto
  }
  return ''
}

/** Ejecuta una orden local. Devuelve { respuesta, seguir } (seguir = escuchar una pregunta de seguimiento). */
function ejecutarComando(comando) {
  switch (comando.tipo) {
    case 'despedida':
      modoLlamada.value = false
      return { respuesta: 'Con mucho gusto. Aquí estoy cuando me necesites.', seguir: false }
    case 'desactivar':
      vozActiva.value = false
      guardarPreferenciaVoz(false)
      modoLlamada.value = false
      return { respuesta: 'Listo, apagué la activación por voz. Cuando quieras volver a llamarme, la enciendes desde el chat.', seguir: false }
    case 'describir':
      try {
        return { respuesta: describirPantalla(document).hablado, seguir: true }
      } catch (err) {
        console.warn('No se pudo describir la pantalla:', err)
        return { respuesta: 'Qué pena, no pude leer esta pantalla en este momento.', seguir: true }
      }
    case 'repetir':
      return { respuesta: ultimaRespuestaBot() || 'Todavía no te he dicho nada en esta conversación, cuéntame qué necesitas.', seguir: true }
    case 'ayuda':
      return {
        respuesta: 'Claro que sí. Puedo responder preguntas sobre tus tickets, mantenimientos y compras. También puedo describir la pantalla en la que estás, llevarte a otra sección, por ejemplo: llévame a notificaciones, y repetir mi última respuesta. Para callarme, presiona Escape.',
        seguir: true,
      }
    case 'abrir':
      abierto.value = true
      hayMensajeNuevo.value = false
      return { respuesta: 'Listo, aquí tienes el chat.', seguir: true }
    case 'cerrar':
      abierto.value = false
      return { respuesta: 'Listo, cerré el chat.', seguir: false }
    case 'saludo':
      return { respuesta: `¡Hola${nombreUsuario.value ? ' ' + nombreUsuario.value : ''}! ¿Qué más? ¿En qué te puedo ayudar?`, seguir: true }
    case 'navegar': {
      // 1) Como lo haría una persona: la opción del menú lateral de su rol.
      let opcion = null
      try { opcion = buscarOpcionMenu(document, comando) } catch {}
      if (opcion) {
        opcion.elemento.click()
        return { respuesta: `Listo, ya te abrí ${opcion.etiqueta}.`, seguir: true }
      }
      // 2) Una ruta conocida del sistema.
      const ruta = comando.destino ? rutaDestino(comando.destino) : null
      const nombre = NOMBRES_DESTINO[comando.destino] || comando.texto
      if (ruta && ruta === route.path) return { respuesta: `Ya estás en ${nombre}, ¿qué más necesitas?`, seguir: true }
      if (ruta) {
        router.push(ruta).catch(() => {})
        return { respuesta: `Dale, te llevo a ${nombre}.`, seguir: true }
      }
      // 3) Sección conocida que este rol no tiene: decirlo y ofrecer las opciones reales.
      if (comando.destino) {
        let opciones = []
        try { opciones = opcionesMenu(document) } catch {}
        return {
          respuesta: `Qué pena, no encontré ${nombre} en tu menú.` + (opciones.length ? ` Te puedo abrir: ${opciones.join(', ')}.` : ''),
          seguir: true,
        }
      }
      // 4) No es una sección: se deja que responda la IA.
      return null
    }
    default:
      return { respuesta: 'Qué pena, no te entendí. ¿Me lo repites, por favor?', seguir: true }
  }
}

function registrarIntercambio(pregunta, respuesta) {
  mensajes.value.push({ rol: 'usuario', texto: pregunta, hora: horaActual() })
  mensajes.value.push({ rol: 'bot', texto: respuesta, hora: horaActual() })
  if (!abierto.value) hayMensajeNuevo.value = true
  scrollAbajo()
}

function cancelarConversacion() {
  ++turnoVoz
  if (controlConsulta) { controlConsulta.porUsuario = true; controlConsulta.abort() }
  modoLlamada.value = false
  detenerHabla()
  volverAReposo()
}

/* ---------------- Activación por voz (interruptor) ---------------- */
function toggleVozActiva() {
  if (!puedeUsarMicrofono()) return
  if (dictando.value) detenerDictado()

  vozActiva.value = !vozActiva.value
  guardarPreferenciaVoz(vozActiva.value)

  if (vozActiva.value) {
    avisoVoz.value = ''
    sonarTono()
    precargarFrasesFrecuentes()
    // Este clic también "desbloquea" la voz del navegador para el resto de la sesión.
    if (modoLlamada.value) return
    limpiarTimers()
    detenerReconocimiento()
    const turno = ++turnoVoz
    estadoVoz.value = 'hablando'
    hablar(`¡Listo! Cuando me necesites, solo di: oye ${NOMBRE_ASISTENTE}.`).then(ok => {
      if (ok && turno === turnoVoz) volverAReposo()
    })
  } else {
    cancelarConversacion()
  }
}

/* ---------------- Dictado manual (botón micrófono) ---------------- */
function toggleGrabacionManual() {
  if (!puedeUsarMicrofono()) return
  if (dictando.value) { detenerDictado(); return }

  if (estadoVoz.value !== 'espera' && estadoVoz.value !== 'inactivo') cancelarConversacion()
  limpiarTimers()
  detenerReconocimiento()
  textoBaseDictado = mensajeActual.value.trim()
  dictando.value = true
  arrancarReconocimiento()
  tSilencio = setTimeout(detenerDictado, 8000) // nadie habló
}

function manejarDictado(finalTxt, interino) {
  if (finalTxt) textoBaseDictado = `${textoBaseDictado} ${finalTxt}`.trim()
  mensajeActual.value = `${textoBaseDictado} ${interino}`.trim()
  ajustarAltura()
  clearTimeout(tSilencio)
  tSilencio = setTimeout(detenerDictado, 2500)
}

function detenerDictado() {
  clearTimeout(tSilencio)
  if (!dictando.value) return
  dictando.value = false
  detenerReconocimiento()
  programarReinicio(300) // si la activación por voz está encendida, vuelve a esperar "Tati"
  nextTick(() => inputRef.value?.focus())
}

/* ---------------- Modo llamada (conversación continua) ---------------- */
function toggleModoLlamada() {
  if (!puedeUsarMicrofono()) return
  if (modoLlamada.value) { cancelarConversacion(); return }
  if (dictando.value) detenerDictado()
  ++turnoVoz
  detenerHabla()
  modoLlamada.value = true
  sonarTono()
  pasarAEscuchar(0)
}

/* ---------------- Síntesis de voz (TTS) — voz colombiana de Tati ----------------
   1. Voz principal: "Salomé" (es-CO) generada por el servidor (/api/asistente/voz/),
      igual en cualquier navegador. Se lee frase por frase y la siguiente frase se
      pide mientras suena la actual, así no hay silencios ni cortes.
   2. Respaldo: si el servidor o internet fallan, la voz del navegador más parecida
      (es-CO, latina, femenina). Tras un fallo se usa el respaldo durante 1 minuto
      para no hacer esperar al usuario en cada frase.
------------------------------------------------------------------------------- */
let idHabla = 0
let vocesDisponibles = []
let audioActual = null
let vozServidorFallaHasta = 0
const cacheAudio = new Map() // frase → Promise<blobURL | null>
const MAX_CACHE_AUDIO = 40

function cargarVoces() {
  if (soportaSintesis) vocesDisponibles = window.speechSynthesis.getVoices()
}

function pedirAudio(frase) {
  if (Date.now() < vozServidorFallaHasta || typeof Audio === 'undefined') return Promise.resolve(null)
  if (cacheAudio.has(frase)) return cacheAudio.get(frase)

  const promesa = (async () => {
    const control = new AbortController()
    const limite = setTimeout(() => control.abort(), 9000)
    try {
      const res = await fetch('/api/asistente/voz/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Token ${token.value}` },
        body: JSON.stringify({ texto: frase }),
        signal: control.signal,
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      if (!blob.size) throw new Error('audio vacío')
      return URL.createObjectURL(blob)
    } catch (err) {
      console.warn('Voz de Tati no disponible, se usa la del navegador:', err?.message || err)
      vozServidorFallaHasta = Date.now() + 60000
      cacheAudio.delete(frase)
      return null
    } finally {
      clearTimeout(limite)
    }
  })()

  cacheAudio.set(frase, promesa)
  if (cacheAudio.size > MAX_CACHE_AUDIO) {
    const [clave, vieja] = cacheAudio.entries().next().value
    cacheAudio.delete(clave)
    vieja.then(url => url && URL.revokeObjectURL(url))
  }
  return promesa
}

/** Pide por adelantado frases frecuentes (saludo) para que suenen al instante. */
function precargarVoz(texto) {
  frasesParaVoz(texto).forEach(pedirAudio)
}

function frasesSaludo() {
  return 'Ordene, mi señor. ¿En qué puedo ayudarle?'
}

/** Reproduce un MP3. Resuelve 'ok' | 'error' | 'bloqueado' | 'cancelado'. */
function reproducirAudio(url, mio) {
  return new Promise(resolve => {
    const audio = new Audio(url)
    audioActual = audio
    let listo = false
    let guardia = null
    const fin = (r) => {
      if (listo) return
      listo = true
      clearTimeout(guardia)
      if (audioActual === audio) audioActual = null
      resolve(r)
    }
    audio.onended = () => fin('ok')
    audio.onerror = () => fin('error')
    audio.onpause = () => { if (mio !== idHabla) fin('cancelado') }
    audio.onloadedmetadata = () => {
      if (Number.isFinite(audio.duration)) {
        clearTimeout(guardia)
        guardia = setTimeout(() => fin('ok'), (audio.duration + 3) * 1000)
      }
    }
    guardia = setTimeout(() => fin('ok'), 30000) // red de seguridad
    const p = audio.play()
    if (p?.catch) p.catch(e => fin(e?.name === 'NotAllowedError' ? 'bloqueado' : 'error'))
  })
}

/** Voz del navegador (respaldo). Resuelve 'ok' | 'bloqueado' | 'cancelado'. */
function hablarNavegador(frase, mio) {
  return new Promise(resolve => {
    if (!soportaSintesis) return resolve('ok')
    const synth = window.speechSynthesis
    let listo = false
    let guardia = null
    const fin = (r) => {
      if (listo) return
      listo = true
      clearTimeout(guardia)
      resolve(r)
    }
    const u = new SpeechSynthesisUtterance(frase)
    const voz = elegirVoz(vocesDisponibles.length ? vocesDisponibles : synth.getVoices())
    if (voz) { u.voice = voz; u.lang = voz.lang } else { u.lang = 'es-CO' }
    u.rate = 0.96  // mismo carácter cálido que la voz del servidor
    u.pitch = 0.95
    u.onend = () => fin('ok')
    u.onerror = (e) => {
      if (e.error === 'not-allowed') fin('bloqueado')
      else if (e.error === 'interrupted' || e.error === 'canceled') fin('cancelado')
      else fin('ok')
    }
    // Algunos navegadores no disparan "onend": no dejar la conversación colgada.
    guardia = setTimeout(() => fin(mio === idHabla ? 'ok' : 'cancelado'), Math.max(6000, frase.length * 110))
    setTimeout(() => {
      if (mio !== idHabla) return fin('cancelado')
      synth.resume()
      synth.speak(u)
    }, 60)
  })
}

function detenerSalidaAudio() {
  if (audioActual) { try { audioActual.pause() } catch {} }
  if (soportaSintesis) window.speechSynthesis.cancel()
}

/**
 * Lee un texto en voz alta con la voz de Tati. Siempre resuelve (nunca deja la
 * conversación colgada):
 *   true  → terminó (o el navegador no pudo hablar; se continúa igual)
 *   false → fue interrumpida por otra lectura o por "cancelar".
 */
async function hablar(texto) {
  const mio = ++idHabla
  detenerSalidaAudio()
  textoHablando.value = texto
  const frases = frasesParaVoz(texto, { max: LIMITE_VOZ })
  if (!frases.length) return true
  // Se piden todas las frases en paralelo (máx. ~4): mientras suena la primera,
  // las demás ya se están generando en el servidor.
  frases.forEach(pedirAudio)
  return reproducirFrases(frases, mio)
}

const LIMITE_VOZ = 600
const AVISO_DETALLE_CHAT = 'El resto te lo dejé escrito en el chat.'
const FRASE_ESPERA = 'Regálame un momentico, ya te cuento.'
const FRASE_DIME = '¿Sí, mi señor? Ordene.'

/** Cola asíncrona de frases: se llena mientras llega la respuesta y se lee en orden. */
function crearColaFrases() {
  const items = []
  let esperando = null
  let cerrada = false
  return {
    push(frase) {
      pedirAudio(frase) // la voz se genera mientras suena la frase anterior
      if (esperando) { esperando({ value: frase, done: false }); esperando = null } else items.push(frase)
    },
    cerrar() {
      cerrada = true
      if (esperando) { esperando({ value: undefined, done: true }); esperando = null }
    },
    [Symbol.asyncIterator]() {
      return {
        next: () => items.length
          ? Promise.resolve({ value: items.shift(), done: false })
          : cerrada ? Promise.resolve({ value: undefined, done: true }) : new Promise(r => { esperando = r }),
      }
    },
  }
}

/** Lee en orden las frases (lista o cola). true = terminó; false = interrumpida. */
async function reproducirFrases(fuente, mio) {
  try {
    return await reproducirFrasesSinRegistro(fuente, mio)
  } finally {
    finHablaEn = Date.now()
    ultimoDicho = textoHablando.value
  }
}

async function reproducirFrasesSinRegistro(fuente, mio) {
  for await (const frase of fuente) {
    if (mio !== idHabla) return false
    const url = await pedirAudio(frase)
    if (mio !== idHabla) return false

    let r = url ? await reproducirAudio(url, mio) : 'error'
    if (r === 'error' && mio === idHabla) r = await hablarNavegador(frase, mio)

    if (mio !== idHabla || r === 'cancelado') return false
    if (r === 'bloqueado') {
      avisoVoz.value = `Haz clic una vez en la página para que ${NOMBRE_ASISTENTE} pueda hablar.`
      return true
    }
  }
  return mio === idHabla
}

function detenerHabla() {
  ++idHabla
  detenerSalidaAudio()
  textoHablando.value = ''
}

function precargarFrasesFrecuentes() {
  if (!estaAutenticado.value) return
  precargarVoz(frasesSaludo())
  precargarVoz(FRASE_DIME)
  precargarVoz(FRASE_ESPERA)
  precargarVoz(AVISO_DETALLE_CHAT)
}

/** Botón "Escuchar" de cada respuesta. */
async function leerMensaje(texto) {
  limpiarTimers()
  detenerReconocimiento()
  const turno = ++turnoVoz
  estadoVoz.value = 'hablando'
  const completo = await hablar(texto)
  if (!completo || turno !== turnoVoz) return
  if (modoLlamada.value) pasarAEscuchar(0)
  else volverAReposo()
}

/* ---------------- Tono de activación ---------------- */
let ctxAudio = null
function sonarTono(tipo = 'inicio') {
  try {
    const AC = window.AudioContext || window.webkitAudioContext
    if (!AC) return
    ctxAudio = ctxAudio || new AC()
    if (ctxAudio.state === 'suspended') ctxAudio.resume()
    const t = ctxAudio.currentTime
    const osc = ctxAudio.createOscillator()
    const g = ctxAudio.createGain()
    osc.type = 'sine'
    // inicio: sube (te escucho) · fin: baja (te escuché)
    const [f1, f2, vol] = tipo === 'fin' ? [880, 620, 0.12] : [660, 880, 0.18]
    osc.frequency.setValueAtTime(f1, t)
    osc.frequency.setValueAtTime(f2, t + 0.09)
    g.gain.setValueAtTime(0.0001, t)
    g.gain.exponentialRampToValueAtTime(vol, t + 0.02)
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.24)
    osc.connect(g).connect(ctxAudio.destination)
    osc.start(t)
    osc.stop(t + 0.26)
  } catch {}
}

/* ---------------- Ciclo de vida de la voz ---------------- */
function alCambiarVisibilidad() {
  if (document.visibilityState === 'visible') {
    reclamarPestana()
    programarReinicio(300)
  } else {
    detenerReconocimiento() // pestaña oculta: no se escucha
  }
}

function alEnfocarVentana() {
  if (document.visibilityState === 'visible' && !esPestanaActiva()) {
    reclamarPestana()
    programarReinicio(300)
  }
}

function alPresionarTecla(e) {
  if (e.key === 'Escape' && ['escuchando', 'pensando', 'hablando'].includes(estadoVoz.value)) {
    cancelarConversacion()
  }
}

async function verificarPermisoMicrofono() {
  try {
    const p = await navigator.permissions?.query({ name: 'microphone' })
    if (p?.state === 'denied' && vozActiva.value) {
      apagarVozPorError(`El micrófono está bloqueado para esta página. Permítelo desde el candado de la barra de direcciones para hablar con ${NOMBRE_ASISTENTE}.`)
    }
  } catch {}
}

onMounted(() => {
  if (soportaSintesis) {
    cargarVoces()
    window.speechSynthesis.addEventListener?.('voiceschanged', cargarVoces)
  }
  document.addEventListener('visibilitychange', alCambiarVisibilidad)
  window.addEventListener('keydown', alPresionarTecla)
  window.addEventListener('focus', alEnfocarVentana)
  window.addEventListener('storage', alCambiarPestanaActiva)
  window.addEventListener('beforeunload', soltarPestana)
  // Esta pestaña pasa a ser la que escucha (la anterior se detiene) y arranca el micrófono.
  reclamarPestana()
  programarReinicio(500)
  if (vozActiva.value) verificarPermisoMicrofono()
})

onUnmounted(() => {
  if (soportaSintesis) window.speechSynthesis.removeEventListener?.('voiceschanged', cargarVoces)
  document.removeEventListener('visibilitychange', alCambiarVisibilidad)
  window.removeEventListener('keydown', alPresionarTecla)
  window.removeEventListener('focus', alEnfocarVentana)
  window.removeEventListener('storage', alCambiarPestanaActiva)
  window.removeEventListener('beforeunload', soltarPestana)
  soltarPestana()
  ++turnoVoz
  limpiarTimers()
  clearTimeout(tReinicio)
  detenerHabla()
  detenerReconocimiento()
  try { ctxAudio?.close() } catch {}
  for (const p of cacheAudio.values()) p.then(url => url && URL.revokeObjectURL(url))
  cacheAudio.clear()
})

// Mientras habla o piensa, el micrófono se reanuda para poder interrumpirla.
watch(estadoVoz, (estado) => {
  if ((estado === 'hablando' || estado === 'pensando') && !rec) programarReinicio(450)
})

// Iniciar / detener la escucha según la sesión (login / logout).
watch(estaAutenticado, (autenticado) => {
  if (autenticado) {
    if (estadoVoz.value === 'inactivo') estadoVoz.value = estadoReposo()
    programarReinicio(500)
    if (vozActiva.value) setTimeout(precargarFrasesFrecuentes, 1500)
  } else {
    ++turnoVoz
    modoLlamada.value = false
    dictando.value = false
    limpiarTimers()
    detenerHabla()
    detenerReconocimiento()
    estadoVoz.value = 'inactivo'
  }
}, { immediate: true })

/* ============================================================
   ACCIONES
============================================================ */
function toggleChat() {
  abierto.value = !abierto.value
  if (abierto.value) {
    hayMensajeNuevo.value = false
    nextTick(() => inputRef.value?.focus())
  } else {
    if (dictando.value) detenerDictado()
    if (modoLlamada.value) cancelarConversacion()
  }
}

function limpiarChat() {
  mensajes.value = []
  errorConexion.value = false
  if (['escuchando', 'pensando', 'hablando'].includes(estadoVoz.value)) cancelarConversacion()
}

function usarSugerencia(texto) {
  mensajeActual.value = texto
  enviarMensaje()
}

async function enviarMensaje() {
  const texto = mensajeActual.value.trim()
  if (!texto || cargando.value) return
  if (dictando.value) detenerDictado()

  mensajeActual.value = ''
  textoBaseDictado = ''
  if (inputRef.value) inputRef.value.style.height = 'auto'

  // En modo llamada, la respuesta a lo escrito también se lee en voz alta.
  if (modoLlamada.value) {
    procesarConsulta(texto)
    return
  }
  // Órdenes escritas ("describe esta pantalla", "llévame a compras"…) se resuelven al instante.
  const comando = detectarComando(texto)
  if (comando && ['describir', 'navegar', 'repetir', 'ayuda'].includes(comando.tipo)) {
    const local = ejecutarComando(comando)
    if (local) {
      registrarIntercambio(texto, local.respuesta)
      return
    }
  }
  await consultarServidor(texto)
}

/** Resumen de lo que el usuario ve (se envía como contexto a la IA). */
function resumenPantallaActual(pregunta) {
  if (!refiereAPantalla(pregunta)) return '' // menos texto = la IA responde mucho más rápido
  try { return describirPantalla(document).resumen } catch { return '' }
}

/**
 * Envía la consulta al backend, agrega ambos mensajes al historial y
 * devuelve el texto de la respuesta (nunca lanza error).
 */
let controlConsulta = null

async function consultarServidor(texto, { voz = false, alFrase = null } = {}) {
  mensajes.value.push({ rol: 'usuario', texto, hora: horaActual() })
  await scrollAbajo()

  cargando.value = true
  errorConexion.value = false
  let respuesta
  let mensajeBot = null // se muestra en el chat mientras se va escribiendo

  const control = new AbortController()
  controlConsulta = control
  const limite = setTimeout(() => control.abort(), 90000)
  try {
    const res = await fetch('/api/asistente/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token.value}`,
      },
      body: JSON.stringify({
        mensaje: texto,
        modo: voz ? 'voz' : 'texto',
        pantalla: resumenPantallaActual(texto),
        stream: true,
      }),
      signal: control.signal,
    })
    if (res.status === 401) {
      const e = new Error('sesión expirada')
      e.sesionExpirada = true
      throw e
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const tipo = res.headers?.get?.('Content-Type') || ''
    if (!tipo.includes('ndjson') || !res.body?.getReader) {
      const data = await res.json()
      respuesta = data.respuesta || 'No obtuve respuesta del servidor.'
    } else {
      // Respuesta por partes: una línea JSON por trozo.
      const lector = res.body.getReader()
      const decodificador = new TextDecoder()
      let pendiente = ''
      let acumulado = ''
      let porFrases = ''
      const procesarLinea = (linea) => {
        if (!linea.trim()) return
        const d = JSON.parse(linea)
        if (d.delta) {
          acumulado += d.delta
          if (!mensajeBot) {
            cargando.value = false
            mensajes.value.push({ rol: 'bot', texto: '', hora: horaActual() })
            mensajeBot = mensajes.value[mensajes.value.length - 1]
          }
          mensajeBot.texto = acumulado
          scrollAbajo()
          if (alFrase) {
            const r = extraerFrases(porFrases + d.delta)
            porFrases = r.resto
            r.frases.forEach(alFrase)
          }
        }
        if (d.fin && d.respuesta) acumulado = d.respuesta
      }
      for (;;) {
        const { value, done } = await lector.read()
        if (done) break
        pendiente += decodificador.decode(value, { stream: true })
        const lineas = pendiente.split('\n')
        pendiente = lineas.pop()
        lineas.forEach(procesarLinea)
      }
      procesarLinea(pendiente)
      if (alFrase && porFrases.trim()) extraerFrases(porFrases, true).frases.forEach(alFrase)
      respuesta = acumulado.trim() || 'No obtuve respuesta del servidor.'
    }
  } catch (err) {
    if (control.porUsuario) {
      respuesta = mensajeBot?.texto || '' // cancelada por el usuario
    } else if (err?.sesionExpirada) {
      respuesta = 'Qué pena, tu sesión expiró. Vuelve a iniciar sesión y seguimos conversando.'
    } else {
      errorConexion.value = true
      respuesta = mensajeBot?.texto
        ? mensajeBot.texto
        : 'Qué pena, en este momento no me puedo conectar con el servidor. Intenta de nuevo en unos minuticos, por favor.'
    }
  } finally {
    clearTimeout(limite)
    cargando.value = false
    if (controlConsulta === control) controlConsulta = null
  }

  if (mensajeBot) mensajeBot.texto = respuesta || mensajeBot.texto
  else if (respuesta) mensajes.value.push({ rol: 'bot', texto: respuesta, hora: horaActual() })
  if (!abierto.value) hayMensajeNuevo.value = true
  await scrollAbajo()
  return respuesta
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

/* ============================================================
   VOZ — "OYE TATI"
============================================================ */
.sia-asistente-raiz {
  display: contents;
}

/* FAB en espera (escucha en segundo plano) */
.sia-fab--espera {
  box-shadow: 0 6px 22px rgba(12, 42, 79, 0.45), 0 0 0 3px rgba(255, 199, 44, 0.35);
}

/* FAB durante la conversación por voz */
.sia-fab--voz {
  animation: sia-anillo 1.4s ease-out infinite;
}

@keyframes sia-anillo {
  0%   { box-shadow: 0 6px 22px rgba(12, 42, 79, 0.45), 0 0 0 0 rgba(255, 199, 44, 0.65); }
  100% { box-shadow: 0 6px 22px rgba(12, 42, 79, 0.45), 0 0 0 16px rgba(255, 199, 44, 0); }
}

.sia-fab__oido {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #FFC72C;
  color: #0C2A4F;
  border: 2px solid #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Burbuja flotante con el chat cerrado */
.sia-burbuja-voz {
  position: fixed;
  right: 28px;
  bottom: 98px;
  z-index: 999998;
  width: min(330px, calc(100vw - 32px));
  background: linear-gradient(135deg, #0C2A4F 0%, #123A6B 100%);
  color: #FFFFFF;
  border: 1px solid rgba(255, 199, 44, 0.45);
  border-radius: 16px;
  padding: 12px 14px;
  box-shadow: 0 12px 32px rgba(12, 42, 79, 0.4);
}

.sia-burbuja-voz__cabecera {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13.5px;
}

.sia-burbuja-voz__cabecera strong {
  flex: 1;
  color: #FFC72C;
  font-weight: 700;
}

.sia-burbuja-voz__cerrar {
  background: rgba(255, 255, 255, 0.12);
  border: none;
  color: #FFFFFF;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.sia-burbuja-voz__cerrar:hover {
  background: rgba(255, 199, 44, 0.3);
}

.sia-burbuja-voz__texto {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.45;
  color: #E8EEF6;
  max-height: 120px;
  overflow-y: auto;
}

/* Ondas animadas */
.sia-burbuja-voz__onda {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  height: 18px;
}

.sia-burbuja-voz__onda i {
  display: block;
  width: 3px;
  height: 6px;
  border-radius: 2px;
  background: #FFC72C;
}

.sia-burbuja-voz--escuchando .sia-burbuja-voz__onda i,
.sia-burbuja-voz--hablando .sia-burbuja-voz__onda i {
  animation: sia-onda 0.9s ease-in-out infinite;
}

.sia-burbuja-voz__onda i:nth-child(2) { animation-delay: 0.15s; }
.sia-burbuja-voz__onda i:nth-child(3) { animation-delay: 0.3s; }
.sia-burbuja-voz__onda i:nth-child(4) { animation-delay: 0.45s; }

.sia-burbuja-voz--pensando .sia-burbuja-voz__onda i {
  animation: sia-parpadeo 1.2s ease-in-out infinite;
}

@keyframes sia-onda {
  0%, 100% { height: 5px; }
  50%      { height: 18px; }
}

@keyframes sia-parpadeo {
  0%, 100% { opacity: 0.3; }
  50%      { opacity: 1; }
}

/* Aviso de voz flotante */
.sia-aviso-voz {
  position: fixed;
  right: 28px;
  bottom: 98px;
  z-index: 999997;
  width: min(330px, calc(100vw - 32px));
  background: #FFF3E0;
  color: #8A3A00;
  border: 1px solid #FFB74D;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 12.5px;
  line-height: 1.4;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.sia-aviso-voz span { flex: 1; }

.sia-aviso-voz button,
.sia-error-banner--voz button {
  background: none;
  border: none;
  color: inherit;
  font-size: 16px;
  cursor: pointer;
  line-height: 1;
}

.sia-error-banner--voz {
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
}

.sia-error-banner--voz span { flex: 1; }

/* Interruptor activo en la cabecera */
.sia-ventana__btn-accion--activo {
  background: #FFC72C;
  border-color: #FFC72C;
  color: #0C2A4F;
}

.sia-ventana__btn-accion--activo:hover {
  background: #FFD760;
  color: #0C2A4F;
}

.sia-bienvenida__link {
  background: none;
  border: none;
  padding: 0;
  color: #123A6B;
  font: inherit;
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
}

.sia-voz-activo-banner__texto {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sia-voz-activo-banner__btn {
  background: #0C2A4F;
  color: #FFC72C;
  border: none;
  border-radius: 8px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.sia-fade-enter-active,
.sia-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.sia-fade-enter-from,
.sia-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 480px) {
  .sia-burbuja-voz,
  .sia-aviso-voz {
    right: 16px;
    bottom: 90px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sia-fab--voz,
  .sia-burbuja-voz__onda i {
    animation: none !important;
  }
}
</style>
