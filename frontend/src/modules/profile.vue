<template>
    <div class="min-h-screen relative overflow-x-hidden">
        <!-- Gradient underlay -->
        <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>

        <!-- Dotted overlay -->
        <div class="pointer-events-none absolute inset-0 opacity-20"
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
                    <BarMeter v-for="m in meterList" :key="m.key" :label="m.label" :value="m.value"
                        :left-label="m.leftLabel" :right-label="m.rightLabel" :color="m.color"
                        :aria-label="`${m.label} ${Math.round(m.value)} percent`" />
                </div>
            </section>

            <p v-else class="loading">Loading profile...</p>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import BarMeter from '../components/BarMeter.vue'

const router = useRouter()

// Hardcoded userId
const userId = sessionStorage.getItem("userId");

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

const username = ref('')
const metrics = ref({ sleepHours: 0, sleepQuality: 0, energy: 0, stress: 0, mood: 0 })
const loaded = ref(false)

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
        { key: 'sleepHours', label: 'Sleep Hours', value: hoursPct, leftLabel: '0h', rightLabel: '10h', color: 'var(--c-sleep)' },
        { key: 'sleepQuality', label: 'Sleep Quality', value: clamp(metrics.value.sleepQuality), leftLabel: 'Poor', rightLabel: 'Great', color: 'var(--c-quality)' },
        { key: 'energy', label: 'Energy', value: clamp(metrics.value.energy), leftLabel: 'Low', rightLabel: 'High', color: 'var(--c-energy)' },
        { key: 'stress', label: 'Stress', value: clamp(metrics.value.stress), leftLabel: 'Calm', rightLabel: 'Tense', color: 'var(--c-stress)' },
        { key: 'mood', label: 'Mood', value: clamp(metrics.value.mood), leftLabel: 'Down', rightLabel: 'Upbeat', color: 'var(--c-mood)' },
    ]
})

onMounted(async () => {
    try {
        // Get username
        const resUser = await axios.get(`${baseURL}/userProfile`, { params: { userId } })
        username.value = resUser.data.row.username || 'User'

        // Get all metrics from /moodMetric
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

        metrics.value.sleepHours = avg(rows.map(r => r.sleepHours || r.hours))
        metrics.value.sleepQuality = avg(rows.map(r => r.sleepQuality || r.quality))
        metrics.value.energy = avg(rows.map(r => r.energy || r.energyScore || r.score_energy))
        metrics.value.stress = avg(rows.map(r => r.stress || r.stressScore || r.score_stress))
        metrics.value.mood = avg(rows.map(r => r.mood || r.moodScore || r.score_mood || r.score))

        loaded.value = true
    } catch (err) {
        console.error('Failed to fetch profile/metrics', err)
    }
})

function handleSignout() {
    sessionStorage.removeItem("userId")
    router.push("/login") // adjust route if your login page differs
}
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
    background: #f87171; /* red-ish pink */
    color: white;
    padding: 0.45rem 1rem;
    border-radius: 9999px; /* fully rounded pill */
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
    transition: background 0.2s, transform 0.15s;
    z-index: 20; /* ensure it's on top, but not covering avatar */
}

.signout-btn:hover {
    background: #ef4444;
    transform: translateY(-1px);
}


.signout-btn:hover {
    background: #ef4444;
}

.profile {
    display: grid;
    gap: 1.25rem;
    padding: 1.25rem;
    background: transparent;
}

.profile__header {
    display: grid;
    grid-template-columns: 56px 1fr;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1rem; 
}

.avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #22c55e);
    color: white;
}

.identity .username {
    margin: 0 0 2px;
    font-size: 1.25rem;
    font-weight: 600;
}

.identity .subtitle {
    margin: 0;
    font-size: 0.9rem;
    color: gray;
}

.cards {
    display: grid;
    gap: 14px;
}

.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh; /* centers it vertically inside screen */
    font-size: 1rem;
    font-weight: 500;
    color: #374151; /* nice gray tone */
    text-align: center;
}

</style>
