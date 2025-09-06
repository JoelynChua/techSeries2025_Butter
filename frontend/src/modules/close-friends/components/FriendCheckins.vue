<template>
  <div class="mt-4 w-full rounded-2xl border border-sky-100 bg-white/90 p-3">
    <div class="flex items-end justify-between mb-2">
      <div>
        <div class="font-semibold text-slate-800">This week</div>
        <div class="text-xs text-slate-500">
          <span v-if="dailyQuizAt">Last check-in: {{ formatLocalDT(dailyQuizAt) }}</span>
          <span v-else>No check-ins yet</span>
        </div>
      </div>
      <div class="flex gap-3 text-right">
        <div class="text-xs"><div class="text-slate-500">Avg</div><div class="font-bold">{{ fmt(avgScore) }}</div></div>
        <div class="text-xs"><div class="text-slate-500">Min</div><div class="font-bold">{{ fmt(minScore) }}</div></div>
        <div class="text-xs"><div class="text-slate-500">Max</div><div class="font-bold">{{ fmt(maxScore) }}</div></div>
      </div>
    </div>

    <div v-if="loading" class="text-center text-slate-500 py-8">Loading…</div>
    <div v-else-if="error" class="text-center text-rose-600 py-4 text-sm">{{ error }}</div>
    <div v-else>
      <div v-if="bars.length" class="bars-wrap">
        <div v-for="b in bars" :key="b.key" class="bar-item" :title="`${b.label}: ${b.value != null ? b.value.toFixed(1) : '—'}`">
          <div class="bar"><div class="bar-fill" :style="{ height: b.heightPct }"></div></div>
          <div class="bar-label">{{ b.label }}</div>
        </div>
      </div>
      <p v-else class="text-center text-slate-500 text-sm py-6">No entries in the current week yet.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'

const props = defineProps({
  friend: { type: Object, required: true },
  apiBase: { type: String, required: true }
})

const loading = ref(false)
const error = ref('')
const dailyQuizAt = ref(null)
const avgScore = ref(null)
const minScore = ref(null)
const maxScore = ref(null)
const rows = ref([])

function fmt(v){ return v==null ? '—' : Number(v).toFixed(1) }

function formatLocalDT(iso){
  try{
    return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Singapore' }).format(new Date(iso))
  }catch{ return new Date(iso).toLocaleString() }
}

function labelFor(d){
  return new Intl.DateTimeFormat('en-US', { weekday: 'short', timeZone: 'Asia/Singapore' }).format(d)
}

const bars = computed(()=>{
  const sorted = [...rows.value].sort((a,b)=>{
    const ta = new Date(a.created_timestamp || a.created_at || a.inserted_at).getTime()
    const tb = new Date(b.created_timestamp || b.created_at || b.inserted_at).getTime()
    return ta - tb
  })
  return sorted.map((r,i)=>{
    const d = new Date(r.created_timestamp || r.created_at || r.inserted_at)
    const raw = r.finalMoodScores != null ? Number(r.finalMoodScores) : null // 0–10
    const val = raw==null ? null : Math.max(0, Math.min(10, raw))
    return { key: (r.id??i)+'-'+d.toISOString(), label: labelFor(d), value: val, heightPct: val==null?'0%':`${(val/10)*100}%` }
  })
})

async function getUsersIndex(){
  try{
    const r = await fetch(`${props.apiBase}/users`, { headers:{Accept:'application/json'} })
    if (!r.ok) throw new Error()
    const p = await r.json()
    const arr = Array.isArray(p?.rows) ? p.rows : (Array.isArray(p) ? p : [])
    const m = new Map()
    for (const u of arr){
      const email = (u?.email||'').toLowerCase()
      const id = u?.userId ?? u?.id
      if (email && id!=null) m.set(email, Number(id))
    }
    return m
  }catch{ return new Map() }
}

async function fetchData(){
  loading.value = true
  error.value = ''
  rows.value = []
  try{
    // resolve userId from friend
    let uid = props.friend.userId
    if (!uid && props.friend.email){
      const idx = await getUsersIndex()
      uid = idx.get((props.friend.email||'').toLowerCase())
    }
    if (!uid) throw new Error('No userId for this friend.')

    // weekly endpoint (like profile page)
    const rWeek = await fetch(`${props.apiBase}/userWeeklyQuizResult?userId=${encodeURIComponent(uid)}`, { headers:{Accept:'application/json'} })
    if (rWeek.ok){
      const d = await rWeek.json()
      dailyQuizAt.value = d?.daily_quiz_at || null
      rows.value = Array.isArray(d?.rows) ? d.rows : []
      avgScore.value = d?.avgScore ?? null
      minScore.value = d?.minScore ?? null
      maxScore.value = d?.maxScore ?? null
      return
    }

    // fallback: if weekly missing, still show something from moodMetric
    const rAll = await fetch(`${props.apiBase}/moodMetric?userId=${encodeURIComponent(uid)}`, { headers:{Accept:'application/json'} })
    if (!rAll.ok) throw new Error('Failed loading mood metrics')
    let arr = await rAll.json()
    if (Array.isArray(arr)) { /* ok */ }
    else if (Array.isArray(arr?.rows)) arr = arr.rows
    else if (Array.isArray(arr?.data)) arr = arr.data
    else arr = []

    // synthesize weekly-like bars from latest 7 entries
    const latest = [...arr].sort((a,b)=>new Date(b.created_at||b.inserted_at||b.ts) - new Date(a.created_at||a.inserted_at||a.ts)).slice(0,7).reverse()
    rows.value = latest.map((r,i)=>({
      id: r.id ?? i,
      created_timestamp: r.created_at || r.inserted_at || r.ts || new Date().toISOString(),
      finalMoodScores: Number(r.mood ?? r.moodScore ?? r.score_mood ?? r.score ?? 0)
    }))
    const vals = rows.value.map(x => x.finalMoodScores).filter(x => Number.isFinite(x))
    if (vals.length){
      const avg = vals.reduce((a,b)=>a+b,0)/vals.length
      avgScore.value = avg
      minScore.value = Math.min(...vals)
      maxScore.value = Math.max(...vals)
    }
  }catch(e){
    error.value = e.message || 'Failed to load data'
  }finally{
    loading.value = false
  }
}
onMounted(fetchData)
watchEffect(()=>{ /* refetch if friend changes */ props.friend && fetchData() })
</script>

<style scoped>
.bars-wrap { display:grid; grid-template-columns: repeat(7,1fr); align-items:end; gap:8px; height:120px; padding:6px 2px 4px; border-radius:12px; background:linear-gradient(180deg,#f8fbff,#eef7ff); border:1px solid rgba(59,130,246,0.12); }
.bar-item { display:grid; grid-template-rows:1fr auto; align-items:end; gap:6px; height:100%; }
.bar { position:relative; width:100%; height:100%; border-radius:10px; background:linear-gradient(180deg,#e2e8f0 0%, #f1f5f9 100%); overflow:hidden; }
.bar-fill { position:absolute; left:0; right:0; bottom:0; background:linear-gradient(180deg,#5EC4FF 0%, #3DA8FF 100%); border-top-left-radius:10px; border-top-right-radius:10px; transition:height 240ms ease; }
.bar-label { text-align:center; font-size:0.7rem; color:#64748b; }
</style>
