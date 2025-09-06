<template>
  <div
    class="relative overflow-hidden rounded-[32px] bg-white p-4 ring-2 ring-white shadow-[0_16px_36px_-12px_rgba(2,132,199,0.4)]"
    :class="{
      'ring-rose-300 shadow-[0_18px_48px_-22px_rgba(225,29,72,0.35)]': anyBelowThreshold
    }"
  >
    <div aria-hidden="true" class="pointer-events-none absolute -right-6 -bottom-6 h-28 w-28 rounded-full bg-sky-200 z-0"></div>
    <div aria-hidden="true" class="pointer-events-none absolute right-6 -bottom-2 h-10 w-10 rounded-full bg-sky-300 z-0"></div>
    <div aria-hidden="true" class="pointer-events-none absolute -right-6 -bottom-6 h-28 w-28 rounded-full bg-sky-200 z-0 hidden sm:block"></div>

    <div class="relative z-10 flex flex-col items-center">
      <div class="relative">
        <img
          :src="avatarSrc"
          alt=""
          class="h-32 w-32 rounded-[28px] object-cover ring-4 ring-white shadow-[0_10px_20px_-10px_rgba(0,0,0,0.45)]"
        />
      </div>

      <div class="mt-4 w-full text-center">
        <div class="truncate text-lg font-extrabold text-sky-900 drop-shadow-[0_1px_0_rgba(255,255,255,0.9)]">
          {{ displayName }}
        </div>
        <div v-if="handle" class="truncate text-sm text-sky-900/70">
          {{ handle }}
        </div>
      </div>

      <!-- badges -->
      <div class="mt-4 flex flex-wrap justify-center gap-2 text-xs">
        <span v-if="friend?.relationship" class="rounded-full bg-sky-100 px-3 py-1 font-semibold text-sky-700">
          {{ friend.relationship }}
        </span>
        <span
          v-if="friend?.emergencycontact || friend?.emergencyContact"
          class="rounded-full bg-rose-100 px-3 py-1 font-semibold text-rose-700"
        >
          Emergency
        </span>
      </div>

      <!-- TAGS -->
      <div v-if="friendTags.length" class="mt-3 flex flex-wrap justify-center gap-2" aria-label="Tags">
        <span
          v-for="(tag, i) in friendTags"
          :key="i"
          class="text-xs bg-sky-100 text-sky-800 px-2 py-1 rounded-full ring-1 ring-sky-200"
        >
          #{{ tag }}
        </span>
      </div>

      <!-- Emotions -->
      <div v-if="hasEmotions" class="mt-5 w-full rounded-2xl bg-sky-50/60 p-3 ring-1 ring-sky-100">
        <!-- Mood -->
        <div class="mb-2">
          <div class="flex items-center justify-between text-[11px] font-semibold text-sky-900/80">
            <span class="inline-flex items-center gap-1">
              😊 Mood
              <span
                v-if="below('mood')"
                class="ml-1 inline-flex items-center gap-1 rounded-full bg-rose-50 px-1.5 py-0.5 text-[10px] font-semibold text-rose-700 ring-1 ring-rose-200"
              >
                <svg viewBox="0 0 24 24" class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 9v4m0 4h.01" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Low
              </span>
            </span>
            <span>{{ pct(friend.emotions?.mood) }}%</span>
          </div>
          <div class="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-sky-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-yellow-300 to-orange-400 transition-[width] duration-500"
              :style="{ width: stat(friend.emotions?.mood) + '%' }"
            />
          </div>
        </div>

        <!-- Energy -->
        <div class="mb-2">
          <div class="flex items-center justify-between text-[11px] font-semibold text-sky-900/80">
            <span class="inline-flex items-center gap-1">
              ⚡ Energy
              <span
                v-if="below('energy')"
                class="ml-1 inline-flex items-center gap-1 rounded-full bg-rose-50 px-1.5 py-0.5 text-[10px] font-semibold text-rose-700 ring-1 ring-rose-200"
              >
                <svg viewBox="0 0 24 24" class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M13 2 3 14h7l-1 8 11-12h-7l1-8z" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Low
              </span>
            </span>
            <span>{{ pct(friend.emotions?.energy) }}%</span>
          </div>
          <div class="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-sky-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-emerald-300 to-emerald-500 transition-[width] duration-500"
              :style="{ width: stat(friend.emotions?.energy) + '%' }"
            />
          </div>
        </div>

        <!-- Sleep -->
        <div>
          <div class="flex items-center justify-between text-[11px] font-semibold text-sky-900/80">
            <span class="inline-flex items-center gap-1">
              😴 Sleep
              <span
                v-if="below('sleep')"
                class="ml-1 inline-flex items-center gap-1 rounded-full bg-rose-50 px-1.5 py-0.5 text-[10px] font-semibold text-rose-700 ring-1 ring-rose-200"
              >
                <svg viewBox="0 0 24 24" class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 12h8M8 16h8M12 20h8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Low
              </span>
            </span>
            <span>{{ pct(friend.emotions?.sleep) }}%</span>
          </div>
          <div class="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-sky-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-sky-300 to-indigo-400 transition-[width] duration-500"
              :style="{ width: stat(friend.emotions?.sleep) + '%' }"
            />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-5 w-full">
        <div v-if="!confirming" class="grid grid-cols-2 gap-2">
          <button
            class="rounded-full bg-slate-100 text-slate-700 text-sm font-semibold py-2 hover:bg-slate-200"
            @click="$emit('more', friend)"
          >
            More
          </button>
          <button
            class="rounded-full bg-rose-100 text-rose-700 text-sm font-semibold py-2 hover:bg-rose-200
                   disabled:opacity-60 disabled:cursor-not-allowed"
            @click="confirming = true"
            :disabled="removing"
          >
            Remove
          </button>
        </div>

        <div v-else class="grid grid-cols-2 gap-2">
          <button
            class="rounded-full bg-rose-600 text-white text-sm font-semibold py-2 hover:bg-rose-700
                   disabled:opacity-60 disabled:cursor-not-allowed"
            @click="confirmRemove"
            :disabled="removing"
          >
            <span v-if="!removing">Delete</span>
            <span v-else class="inline-flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"/>
                <path class="opacity-75" d="M4 12a8 8 0 0 1 8-8v4" stroke="currentColor" stroke-linecap="round"/>
              </svg>
              Deleting…
            </span>
          </button>
          <button
            class="rounded-full bg-slate-100 text-slate-700 text-sm font-semibold py-2 hover:bg-slate-200"
            @click="confirming = false"
          >
            Cancel
          </button>
        </div>
      </div>

      <!-- Slot for expanded content (parent injects the bar graph component) -->
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

import Blank from '@/assets/mascot/Blank.png'
import Concerned from '@/assets/mascot/Concerned.png'
import GoodJob from '@/assets/mascot/GoodJob.png'
import Happy from '@/assets/mascot/Happy.png'
import Love from '@/assets/mascot/Love.png'
import Pout from '@/assets/mascot/Pout.png'
import Proud from '@/assets/mascot/Proud.png'
import Support from '@/assets/mascot/Support.png'

const MASCOT = { Blank, Concerned, GoodJob, Happy, Love, Pout, Proud, Support }

const props = defineProps({
  friend: { type: Object, required: true },
  /** Optional thresholds; default 40 for all */
  thresholds: {
    type: Object,
    default: () => ({ mood: 40, energy: 40, sleep: 40 })
  }
})
const emit = defineEmits(['remove', 'more'])

/* ---------- helpers ---------- */
function clamp01(x) { return Math.max(0, Math.min(100, Number(x) || 0)) }
function normalized(e) {
  return { mood: clamp01(e?.mood ?? 60), energy: clamp01(e?.energy ?? 60), sleep: clamp01(e?.sleep ?? 60) }
}
function mascotByEmotion(e) {
  const { mood, energy, sleep } = normalized(e)
  const avg = (mood + energy + sleep) / 3
  if (sleep < 35 && avg < 60) return MASCOT.Pout
  if (avg < 35)               return MASCOT.Concerned
  if (avg < 45)               return MASCOT.Support
  if (avg >= 90)              return mood >= 92 ? MASCOT.Love : MASCOT.Proud
  if (avg >= 75)              return (mood >= 80 && energy >= 75) ? MASCOT.Proud : MASCOT.Happy
  if (avg >= 58)              return MASCOT.GoodJob
  return MASCOT.Blank
}
function stat(v) {
  const n = Number(v ?? 0)
  return Math.max(0, Math.min(100, Number.isNaN(n) ? 0 : n))
}
/* 2dp formatter */
function pct(v) { return stat(v).toFixed(2) }

/* below-threshold checks */
function belowKey(key) {
  const t = Number(props.thresholds?.[key] ?? 0)
  return stat(props.friend?.emotions?.[key]) < t
}
const below = (key) => belowKey(key)

/* Robust tag parser */
function parseTags(raw) {
  if (Array.isArray(raw)) return raw
  if (raw == null) return []
  if (typeof raw === 'string') {
    const s = raw.trim()
    if (s.startsWith('[') && s.endsWith(']')) {
      try { const arr = JSON.parse(s); return Array.isArray(arr) ? arr : [] } catch {}
    }
    return s.split(',').map(t => t.trim()).filter(Boolean)
  }
  if (typeof raw === 'object' && Array.isArray(raw.tags)) return raw.tags
  return []
}

/* ---------- computed ---------- */
const displayName = computed(() => props.friend?.username || props.friend?.name || 'Friend')
const handle = computed(() => props.friend?.handle || '')
const hasEmotions = computed(() => !!props.friend?.emotions)
const avatarSrc = computed(() => props.friend?.avatar || mascotByEmotion(props.friend?.emotions) || MASCOT.Blank)
const friendTags = computed(() => parseTags(props.friend?.tags || []))
const anyBelowThreshold = computed(() => ['mood','energy','sleep'].some(below))


const confirming = ref(false)
const removing   = ref(false)

function confirmRemove () {
  if (removing.value) return
  removing.value = true
  emit('remove', props.friend)
  setTimeout(() => { removing.value = false; confirming.value = false }, 600)
}
</script>
