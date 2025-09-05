<!-- src/components/notificationAlert.vue -->
<script setup>
import { ref, watch, onBeforeUnmount, toRaw } from 'vue'

/**
 * Props:
 * - items: external list (optional). If provided, the component keeps it in sync (v-model style via update:items).
 * - max: max visible toasts
 * - position: 'top' | 'bottom'
 * - pauseOnHover: pause the auto-dismiss timer while hovering a toast
 */
const props = defineProps({
  items: { type: Array, default: () => [] },
  max: { type: Number, default: 4 },
  position: { type: String, default: 'top' }, // 'top' or 'bottom'
  pauseOnHover: { type: Boolean, default: true },
})

const emit = defineEmits(['update:items', 'dismiss', 'click'])

/** Make a plain array of plain objects (no proxies). */
function cloneList(list) {
  const arr = Array.isArray(list) ? list : []
  return arr.map(item => ({ ...toRaw(item) }))
}

const toasts = ref(cloneList(props.items))
const timers = new Map()

watch(
  () => props.items,
  (val) => {
    toasts.value = cloneList(val)
    rebuildAllTimers()
  },
  { deep: true }
)

function uid() {
  return Math.random().toString(36).slice(2)
}

function toastIcon(type) {
  if (type === 'success') return '🌿'
  if (type === 'error') return '💥'
  if (type === 'warning') return '⚠️'
  return '🔔'
}

function add({ type = 'info', title = '', message = '', timeout = 3500, id, data } = {}) {
  const t = { id: id || uid(), type, title, message, timeout, data }
  toasts.value.push(t)
  if (toasts.value.length > props.max) {
    const removed = toasts.value.splice(0, toasts.value.length - props.max)
    removed.forEach(r => clearTimer(r.id))
  }
  syncUp()
  startTimerFor(t)
  return t.id
}

function dismiss(id) {
  clearTimer(id)
  toasts.value = toasts.value.filter(t => t.id !== id)
  syncUp()
  emit('dismiss', id)
}

function clearAll() {
  for (const id of timers.keys()) clearTimer(id)
  toasts.value = []
  syncUp()
}

function startTimerFor(t) {
  clearTimer(t.id)
  if (!t.timeout || t.timeout <= 0) return
  const startedAt = Date.now()
  const handle = setTimeout(() => dismiss(t.id), t.timeout)
  timers.set(t.id, { handle, remaining: t.timeout, startedAt })
}

function clearTimer(id) {
  const timer = timers.get(id)
  if (!timer) return
  clearTimeout(timer.handle)
  timers.delete(id)
}

function pauseTimer(id) {
  if (!props.pauseOnHover) return
  const timer = timers.get(id)
  if (!timer) return
  clearTimeout(timer.handle)
  const elapsed = Date.now() - timer.startedAt
  timer.remaining = Math.max(0, timer.remaining - elapsed)
  timers.set(id, timer)
}

function resumeTimer(id) {
  if (!props.pauseOnHover) return
  const timer = timers.get(id)
  if (!timer || timer.remaining <= 0) return dismiss(id)
  const newHandle = setTimeout(() => dismiss(id), timer.remaining)
  timers.set(id, { handle: newHandle, remaining: timer.remaining, startedAt: Date.now() })
}

function rebuildAllTimers() {
  for (const id of timers.keys()) clearTimer(id)
  for (const t of toasts.value) startTimerFor(t)
}

function syncUp() {
  // Emit plain copies so parent v-model isn't handed proxies
  emit('update:items', cloneList(toasts.value))
}

defineExpose({ add, dismiss, clearAll })
onBeforeUnmount(clearAll)
</script>

<template>
  <div
    class="absolute inset-x-0 z-40 flex justify-center px-3"
    :class="position === 'top' ? 'top-3' : 'bottom-3'"
    aria-live="polite"
    aria-atomic="true"
  >
    <TransitionGroup
      tag="div"
      class="w-full flex flex-col items-center space-y-2"
      enter-active-class="transition duration-200"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-for="t in toasts"
        :key="t.id"
        class="w-full max-w-xs rounded-xl px-3 py-2.5 ring-1 shadow-lg backdrop-blur bg-white/95 flex items-start gap-2 cursor-pointer"
        :class="[
          t.type === 'success' && 'ring-emerald-200 text-emerald-900',
          t.type === 'error'   && 'ring-rose-200 text-rose-900',
          t.type === 'warning' && 'ring-amber-200 text-amber-900',
          (!['success','error','warning'].includes(t.type)) && 'ring-sky-200 text-sky-900'
        ]"
        @click.stop="emit('click', t)"
        @mouseenter="pauseTimer(t.id)"
        @mouseleave="resumeTimer(t.id)"
      >
        <div class="text-lg leading-none pt-0.5 select-none">
          {{ toastIcon(t.type) }}
        </div>
        <div class="min-w-0">
          <div v-if="t.title" class="text-sm font-bold leading-tight">
            {{ t.title }}
          </div>
          <div class="text-xs leading-snug opacity-90 break-words">
            {{ t.message }}
          </div>
        </div>
        <button
          class="ml-auto text-xs opacity-60 hover:opacity-100 px-2"
          @click.stop="dismiss(t.id)"
          aria-label="Dismiss"
          type="button"
        >
          ✕
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
