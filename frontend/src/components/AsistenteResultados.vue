<template>
  <!-- MODIFICACION2: datos proporcionados explícitamente, sin campos ni estados inventados. -->
  <section class="sia-resultados" aria-label="Resultados estructurados">
    <article v-for="(resultado, indice) in resultados" :key="indice" class="sia-resultado">
      <header>
        <strong>{{ resultado.tipo }}<template v-if="resultado.id"> · {{ resultado.id }}</template></strong>
        <span v-if="resultado.estado" class="sia-resultado__estado" :class="`sia-resultado__estado--${resultado.tono}`">{{ resultado.estado }}</span>
      </header>
      <p v-if="resultado.descripcion">{{ resultado.descripcion }}</p>
      <dl v-if="resultado.responsable || resultado.fecha">
        <template v-if="resultado.responsable"><dt>Responsable</dt><dd>{{ resultado.responsable }}</dd></template>
        <template v-if="resultado.fecha"><dt>Fecha</dt><dd>{{ resultado.fecha }}</dd></template>
      </dl>
    </article>
  </section>
</template>

<script setup>
// MODIFICACION2: la presentación recibe únicamente registros normalizados.
defineProps({ resultados: { type: Array, required: true } })
</script>

<style scoped>
/* MODIFICACION2: tarjetas legibles con estados identificados por texto además de color. */
.sia-resultados { display: grid; gap: 10px; margin-block: 12px; min-width: 0; }
.sia-resultado { padding: 12px; border: 1px solid #c4d4e5; border-radius: 12px; background: #f4f8fc; color: #0c2a4f; overflow-wrap: anywhere; }
header { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; justify-content: space-between; }
strong { font-size: 13px; }
p { margin: 10px 0 0; white-space: pre-wrap; line-height: 1.6; }
dl { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 5px 10px; margin: 10px 0 0; font-size: 12px; }
dt { font-weight: 600; } dd { margin: 0; white-space: pre-wrap; }
.sia-resultado__estado { font-size: 12px; font-weight: 700; border-radius: 20px; padding: 4px 9px; background: #e7edf4; color: #33465c; }
.sia-resultado__estado--pendiente { color: #704800; background: #fff0be; }
.sia-resultado__estado--proceso { color: #124878; background: #deedff; }
.sia-resultado__estado--resuelto { color: #145632; background: #dcf3e5; }
</style>
