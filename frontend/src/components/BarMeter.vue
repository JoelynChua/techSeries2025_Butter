<template>
  <article class="meter">
    <header class="meter__head">
      <h3 class="meter__title">
        <span class="pct">{{ Math.round(pct) }}%</span>
        {{ label }}
      </h3>
    </header>

    <div
      class="meter__bar"
      role="meter"
      :aria-valuemin="0"
      :aria-valuemax="100"
      :aria-valuenow="pct"
      tabindex="0"
    >
      <div class="meter__fill" :style="{ width: pct + '%', background: color }"></div>
      <div class="meter__knob" :style="{ left: knobLeft, borderColor: color }"></div>
    </div>

    <div class="meter__ends">
      <span class="left">{{ leftLabel }}</span>
      <span class="right">{{ rightLabel }}</span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, required: true }, // 0–100
  leftLabel: { type: String, default: '' },
  rightLabel: { type: String, default: '' },
  color: { type: String, default: 'var(--c-energy)' },
})

const pct = computed(() => Math.min(100, Math.max(0, Number(props.value) || 0)))
const knobLeft = computed(() => `calc(${pct.value}% - var(--knob) / 2)`)
</script>

<style scoped>
.meter {
  padding: 14px 16px 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 1px 0 rgba(0,0,0,.04), 0 10px 24px -18px rgba(0,0,0,.3);
}

.meter__head {
  margin-bottom: 10px;
}

.meter__title {
  margin: 0;
  font-weight: 600;
  font-size: 0.98rem;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.meter__title .pct {
  font-weight: 800;
  color: gray;
}

.meter__bar {
  position: relative;
  height: 12px;
  border-radius: 999px;
  background: #e5e7eb; /* neutral gray background */
  overflow: hidden;
}

.meter__fill {
  position: absolute;
  inset: 0 auto 0 0;
  border-radius: inherit;
}

.meter__knob {
  position: absolute;
  top: 50%;
  width: var(--knob);
  height: var(--knob);
  transform: translateY(-50%);
  border-radius: 999px;
  background: white;
  border: 3px solid #ccc;
}

.meter__ends {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 0.85rem;
  color: gray;
}
</style>
