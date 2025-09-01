<template>
  <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <!-- search: rounded candy input with subtle sky vibe -->
    <div class="flex-1 md:max-w-sm">
      <div
        class="flex items-center gap-2 rounded-2xl border border-sky-200 bg-gradient-to-b from-sky-50 to-white px-3 py-2 shadow-[0_6px_16px_rgba(24,39,75,0.06)] focus-within:ring-2 focus-within:ring-sky-300"
      >
        <span class="text-sky-500 text-sm">🔎</span>
        <input
          v-model="modelQuery"
          type="search"
          placeholder="Search name, @handle, tag…"
          class="w-full bg-transparent outline-none placeholder:text-slate-400 text-slate-700"
        />
      </div>
    </div>

    <!-- tabs: bubbly pastel pills -->
    <div class="flex flex-wrap gap-2">
      <button :class="pill('all')"       @click="emit('update:tab', 'all')"> All</button>
      <button :class="pill('active')"    @click="emit('update:tab', 'active')">🟢 Active</button>
      <button :class="pill('pending')"   @click="emit('update:tab', 'pending')">🕒 Pending</button>
      <button :class="pill('emergency')" @click="emit('update:tab', 'emergency')">🚨 Emergency</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  activeTab: { type: String, default: 'all' },
  query: { type: String, default: '' }
})
const emit = defineEmits(['update:tab','update:query'])

const modelQuery = computed({
  get: () => props.query,
  set: v => emit('update:query', v)
})

function pill(tab) {
  const base =
    'px-3 py-1.5 rounded-full text-sm font-semibold transition ' +
    'ring-1 shadow-sm focus:outline-none focus-visible:ring-2 ' +
    'active:translate-y-[1px]'

  const active =
    'text-white ring-sky-400 shadow-[0_8px_18px_-8px_rgba(24,39,75,0.25)] ' +
    'bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)]'

  const idle =
    'text-sky-900 ring-sky-200 bg-sky-100/70 hover:bg-sky-200'

  // special color for emergency when active
  const activeEmergency =
    'text-white ring-rose-400 ' +
    'bg-[linear-gradient(180deg,#FF8CA8_0%,#FF6B9A_100%)]'

  if (props.activeTab === tab) {
    return tab === 'emergency' ? `${base} ${activeEmergency}` : `${base} ${active}`
  }
  return `${base} ${idle}`
}
</script>
