<template>
  <div class="min-h-screen relative overflow-x-hidden">
    <!-- Gradient underlay -->
    <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>

    <!-- Dotted overlay -->
    <div
      class="pointer-events-none absolute inset-0 opacity-20"
      style="background-image:radial-gradient(white 18%, transparent 19%),radial-gradient(white 18%, transparent 19%);background-position:0 0,16px 16px;background-size:32px 32px;">
    </div>

    <!-- Phone-sized content area -->
    <div class="relative mx-auto max-w-sm px-3 py-6">
      <!-- Signout button -->
      <button class="signout-btn" @click="handleSignout">Sign Out</button>

      <section class="profile" v-if="loaded">
        <!-- Header -->
        <header class="profile__header">
          <div class="avatar" aria-hidden="true">{{ initials }}</div>
          <div class="identity">
            <h1 class="username">{{ username }}</h1>
            <p class="subtitle">Personal wellness snapshot</p>
          </div>
        </header>

        <!-- Metrics -->
        <div class="cards">
          <BarMeter
            v-for="m in meterList"
            :key="m.key"
            :label="m.label"
            :value="m.value"
            :left-label="m.leftLabel"
            :right-label="m.rightLabel"
            :color="m.color"
            :aria-label="`${m.label} ${Math.round(m.value)} percent`"
          />
        </div>

        <div class="weekly-card">
          <div class="weekly-card__head">
            <div>
              <h2 class="weekly-title">This week</h2>
              <p class="weekly-sub">
                <span v-if="dailyQuizAt">Last check-in: {{ formatLocalDT(dailyQuizAt) }}</span>
                <span v-else>No check-ins yet</span>
              </p>
            </div>
            <div class="weekly-stats">
              <div class="weekly-stat">
                <div class="stat-label">Avg</div>
                <div class="stat-value">{{ avgScore != null ? avgScore.toFixed(1) : "—" }}</div>
              </div>
              <div class="weekly-stat">
                <div class="stat-label">Min</div>
                <div class="stat-value">{{ minScore != null ? minScore.toFixed(1) : "—" }}</div>
              </div>
              <div class="weekly-stat">
                <div class="stat-label">Max</div>
                <div class="stat-value">{{ maxScore != null ? maxScore.toFixed(1) : "—" }}</div>
              </div>
            </div>
          </div>

          <!-- Bars -->
          <div class="bars-wrap" v-if="weekBars.length">
            <div
              v-for="b in weekBars"
              :key="b.key"
              class="bar-item"
              :title="`${b.label}: ${b.value != null ? b.value.toFixed(1) : '—'}`"
            >
<div class="bar">
  <div
    class="bar-fill"
    :style="{ height: b.heightPct }"
  ></div>
</div>

              <div class="bar-label">{{ b.label }}</div>
            </div>
          </div>
          <p v-else class="no-data">No entries in the current week yet.</p>

          <!-- Latest band -->
          <div v-if="latestBand?.label" class="band-chip">
            Latest band: <strong>{{ latestBand.label }}</strong>
          </div>
        </div>
      </section>

      <p v-else class="loading">Loading profile...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import BarMeter from '../components/BarMeter.vue'

const router = useRouter()

const userId = sessionStorage.getItem("userId")
const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

// UI state
const username = ref('')
const metrics = ref({ sleepHours: 0, sleepQuality: 0, energy: 0, stress: 0, mood: 0 })
const loaded = ref(false)

const weeklyRows = ref([])       // moodMetric rows for the SGT week (with scoreBand attached)
const avgScore   = ref(null)
const minScore   = ref(null)
const maxScore   = ref(null)
const dailyQuizAt = ref(null)    // from users.daily_quiz_at

const initials = computed(() =>
  username.value
    .split(/[\s_]+/)
    .map((s) => s[0]?.toUpperCase())
    .slice(0, 2)
    .join('') || 'U'
)

const clamp = (n, min = 0, max = 100) => Math.min(max, Math.max(min, Number(n) || 0))
const avg = (arr) => (Array.isArray(arr) && arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0)

const meterList = computed(() => {
  const hoursPct = clamp((metrics.value.sleepHours / 10) * 100)
  return [
    { key: 'sleepHours',   label: 'Sleep Hours',   value: hoursPct,                          leftLabel: '0h',   rightLabel: '10h',   color: 'var(--c-sleep)'   },
    { key: 'sleepQuality', label: 'Sleep Quality', value: clamp(metrics.value.sleepQuality), leftLabel: 'Poor', rightLabel: 'Great', color: 'var(--c-quality)' },
    { key: 'energy',       label: 'Energy',        value: clamp(metrics.value.energy),       leftLabel: 'Low',  rightLabel: 'High',  color: 'var(--c-energy)'  },
    { key: 'stress',       label: 'Stress',        value: clamp(metrics.value.stress),       leftLabel: 'Calm', rightLabel: 'Tense', color: 'var(--c-stress)'  },
    { key: 'mood',         label: 'Mood',          value: clamp(metrics.value.mood),         leftLabel: 'Down', rightLabel: 'Upbeat',color: 'var(--c-mood)'    },
  ]
})

const weekBars = computed(() => {
  // Sort ascending by created_timestamp for left->right timeline
  const rows = [...weeklyRows.value].sort((a, b) => {
    const ta = new Date(a.created_timestamp || a.created_at || a.inserted_at).getTime()
    const tb = new Date(b.created_timestamp || b.created_at || b.inserted_at).getTime()
    return ta - tb
  })

  return rows.map((r, i) => {
    const d = new Date(r.created_timestamp || r.created_at || r.inserted_at)
    const label = new Intl.DateTimeFormat('en-US', { weekday: 'short', timeZone: 'Asia/Singapore' }).format(d)

    // mood score is 0–10; clamp just in case backend ever sends outside range
    const raw = r.finalMoodScores != null ? Number(r.finalMoodScores) : null
    const val = raw == null ? null : Math.max(0, Math.min(10, raw))

    return {
      key: (r.id ?? i) + '-' + (r.created_timestamp || r.created_at || r.inserted_at),
      label,
      value: val,                                  // 0–10
      heightPct: val == null ? '0%' : `${(val / 10) * 100}%`, // for the bar
    }
  })
})


const latestBand = computed(() => {
  if (!weeklyRows.value.length) return null
  // latest = greatest created_timestamp
  const latest = [...weeklyRows.value].sort((a, b) => {
    const ta = new Date(a.created_timestamp || a.created_at || a.inserted_at).getTime()
    const tb = new Date(b.created_timestamp || b.created_at || b.inserted_at).getTime()
    return tb - ta
  })[0]
  return latest?.scoreBand || null
})

onMounted(async () => {
  try {
    // 1) User profile
    const resUser = await axios.get(`${baseURL}/userProfile`, { params: { userId } })
    // Your /userProfile earlier returned the whole user object; adjust field if needed:
    const userRow = resUser?.data?.row || resUser?.data || {}
    username.value = userRow.username || 'User'

    const resWeek = await axios.get(`${baseURL}/userWeeklyQuizResult`, { params: { userId } })
    dailyQuizAt.value = resWeek?.data?.daily_quiz_at || null
    weeklyRows.value  = Array.isArray(resWeek?.data?.rows) ? resWeek.data.rows : []
    avgScore.value    = resWeek?.data?.avgScore ?? null
    minScore.value    = resWeek?.data?.minScore ?? null
    maxScore.value    = resWeek?.data?.maxScore ?? null

    // 3) All-time metrics (same as before)
    const resMetrics = await axios.get(`${baseURL}/moodMetric`, { params: { userId } })
    let rows = resMetrics?.data
    if (Array.isArray(rows)) {
      // ok
    } else if (Array.isArray(rows?.rows)) {
      rows = rows.rows
    } else if (Array.isArray(rows?.data)) {
      rows = rows.data
    } else if (rows && typeof rows === 'object') {
      rows = [rows]
    } else {
      rows = []
    }

    metrics.value.sleepHours   = avg(rows.map(r => r.sleepHours ?? r.hours))
    metrics.value.sleepQuality = avg(rows.map(r => r.sleepQuality ?? r.quality))
    metrics.value.energy       = avg(rows.map(r => r.energy ?? r.energyScore ?? r.score_energy))
    metrics.value.stress       = avg(rows.map(r => r.stress ?? r.stressScore ?? r.score_stress))
    metrics.value.mood         = avg(rows.map(r => r.mood ?? r.moodScore ?? r.score_mood ?? r.score))

    loaded.value = true
  } catch (err) {
    console.error('Failed to fetch profile/metrics', err)
    loaded.value = true
  }
})

function handleSignout() {
  sessionStorage.removeItem("userId")
  router.push("/login")
}

// Util: format datetime in Asia/Singapore
function formatLocalDT(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "Asia/Singapore",
    }).format(new Date(iso))
  } catch {
    return new Date(iso).toLocaleString()
  }
}
watch(weekBars, v => console.log('weekBars ->', v), { immediate: true })

</script>

<style scoped>
:root,
:host {
  --c-sleep: linear-gradient(90deg, #8ec5ff, #3a7bd5);
  --c-quality: linear-gradient(90deg, #c084fc, #7c3aed);
  --c-energy: linear-gradient(90deg, #34d399, #10b981);
  --c-stress: linear-gradient(90deg, #fb7185, #ef4444);
  --c-mood: linear-gradient(90deg, #fbbf24, #f59e0b);
  --radius: 24px;
  --knob: 18px;
}

.signout-btn {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: #f87171;
  color: white;
  padding: 0.45rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  box-shadow: 0 3px 8px rgba(0,0,0,0.15);
  transition: background 0.2s, transform 0.15s;
  z-index: 20;
}
.signout-btn:hover { background: #ef4444; transform: translateY(-1px); }

.profile { display: grid; gap: 1.25rem; padding: 1.25rem; background: transparent; }
.profile__header {
  display: grid; grid-template-columns: 56px 1fr; align-items: center; gap: 0.75rem; margin-top: 1rem;
}
.avatar { width: 56px; height: 56px; border-radius: 50%; display: grid; place-items: center; font-weight: 700;
  background: linear-gradient(135deg, #6366f1, #22c55e); color: white; }
.identity .username { margin: 0 0 2px; font-size: 1.25rem; font-weight: 600; }
.identity .subtitle { margin: 0; font-size: 0.9rem; color: gray; }
.cards { display: grid; gap: 14px; }

.loading { display: flex; justify-content: center; align-items: center; min-height: 60vh; font-size: 1rem; font-weight: 500; color: #374151; text-align: center; }

.weekly-card {
  margin-top: 10px;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  background: #ffffffcc;
  backdrop-filter: blur(6px);
  padding: 14px;
  box-shadow: 0 10px 24px -18px rgba(24,39,75,0.35);
}
.weekly-card__head {
  display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; margin-bottom: 10px;
}
.weekly-title { margin: 0; font-weight: 700; font-size: 1.05rem; color: #0f172a; }
.weekly-sub { margin: 0; font-size: 0.8rem; color: #475569; }
.weekly-stats { display: flex; gap: 12px; }
.weekly-stat { text-align: right; }
.stat-label { font-size: 0.7rem; color: #64748b; }
.stat-value { font-size: 1.05rem; font-weight: 800; color: #0f172a; }

/* Bars */
.bars-wrap {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  align-items: end;
  gap: 8px;
  height: 120px;
  padding: 6px 2px 4px 2px;
  border-radius: 12px;
  background: linear-gradient(180deg, #f8fbff, #eef7ff);
  border: 1px solid rgba(59,130,246,0.12);
}
.bar-item { display: grid; grid-template-rows: 1fr auto; align-items: end; gap: 6px; height: 100%; }
.bar {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  background: linear-gradient(180deg, #e2e8f0 0%, #f1f5f9 100%);
  overflow: hidden;
}
.bar-fill {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  background: linear-gradient(180deg, #5EC4FF 0%, #3DA8FF 100%);
  border-top-left-radius: 10px; border-top-right-radius: 10px;
  transition: height 240ms ease;
}
.bar-label {
  text-align: center;
  font-size: 0.7rem;
  color: #64748b;
}

/* Band chip */
.band-chip {
  margin-top: 10px;
  font-size: 0.8rem;
  background: #f1f5f9;
  color: #0f172a;
  display: inline-block;
  padding: 6px 10px;
  border-radius: 9999px;
}
</style>
