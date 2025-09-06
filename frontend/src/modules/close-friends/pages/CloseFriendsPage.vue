<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import ArcadeHeader from '../components/ArcadeHeader.vue'
import FriendFilter from '../components/FriendFilter.vue'
import FriendTile from '../components/FriendTile.vue'
import AddFriendModal from '../components/AddFriendsModal.vue'
import FriendCheckins from '../components/FriendCheckins.vue'

import Blank from '@/assets/mascot/Blank.png'
import Concerned from '@/assets/mascot/Concerned.png'
import GoodJob from '@/assets/mascot/GoodJob.png'
import Happy from '@/assets/mascot/Happy.png'
import Love from '@/assets/mascot/Love.png'
import Pout from '@/assets/mascot/Pout.png'
import Proud from '@/assets/mascot/Proud.png'
import Support from '@/assets/mascot/Support.png'

const router = useRouter()
const API_BASE = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || 'http://localhost:5000').replace(/\/+$/, '')
const OWNER_UID = (sessionStorage.getItem('ownerUid') || sessionStorage.getItem('userId') || '').trim()
const LOW_THRESHOLD = Number(import.meta.env.VITE_LOW_EMO_THRESHOLD ?? 45) // highlight cutoff

/* ---------- state ---------- */
const friends = ref([])
const loading = ref(false)
const friendsError = ref('')
const query = ref('')
const tab = ref('all')

const sortBy = ref('default')
const SORT_OPTIONS = [
  { value: 'default',   label: 'Default' },
  { value: 'lowFirst',  label: 'Lowest emotion' },
  { value: 'highFirst', label: 'Highest emotion' },
  { value: 'nameAZ',    label: 'Name A → Z' },
  { value: 'nameZA',    label: 'Name Z → A' },
]

const showForm = ref(false)
const formMode = ref('add')
const selectedFriend = ref(null)

/* expanded rows: manual toggle only (no auto-expand) */
const expandedIds = ref(new Set())
function setExpanded(id, on) { const s = new Set(expandedIds.value); on ? s.add(id) : s.delete(id); expandedIds.value = s }
function toggleExpanded(friend) { setExpanded(friend.id, !expandedIds.value.has(friend.id)) }
function onMore(friend) { toggleExpanded(friend) }

/* toasts */
const toasts = ref([])
function pushToast({ type='info', title='', message='', timeout=3500 }={}) {
  const id = Math.random().toString(36).slice(2)
  toasts.value.push({ id, type, title, message })
  if (timeout>0) setTimeout(()=>dismissToast(id), timeout)
}
function dismissToast(id){ toasts.value = toasts.value.filter(t=>t.id!==id) }
function toastIcon(t){ return t==='success'?'🌿':t==='error'?'💥':t==='warning'?'⚠️':'🔔' }

/* mascot helpers */
const mascot = { Blank, Concerned, GoodJob, Happy, Love, Pout, Proud, Support }
function clamp(x){ return Math.max(0, Math.min(100, Number(x)||0)) }
function normalizeEmotion(e){ return { mood:clamp(e?.mood), energy:clamp(e?.energy), sleep:clamp(e?.sleep) } }
function mascotByEmotion(e){
  const { mood, energy, sleep } = normalizeEmotion(e||{})
  const avg = (mood+energy+sleep)/3
  if (sleep<35 && avg<60) return mascot.Pout
  if (avg<35) return mascot.Concerned
  if (avg<45) return mascot.Support
  if (avg>=90) return mood>=92 ? mascot.Love : mascot.Proud
  if (avg>=75) return (mood>=80 && energy>=75) ? mascot.Proud : mascot.Happy
  if (avg>=58) return mascot.GoodJob
  return mascot.Blank
}

/* tags parsing */
function parseTags(raw){
  if (Array.isArray(raw)) return raw
  if (raw==null) return []
  if (typeof raw==='string'){
    const s = raw.trim()
    if (s.startsWith('[') && s.endsWith(']')) { try { const a=JSON.parse(s); return Array.isArray(a)?a:[] } catch{} }
    return s.split(',').map(t=>t.trim()).filter(Boolean)
  }
  if (typeof raw==='object' && Array.isArray(raw.tags)) return raw.tags
  return []
}

/* ---------- fetch base friends ---------- */
function friendRowsToUi(rows){
  return rows.map(r=>{
    const id = r.id ?? r.friendId ?? r.userId ?? Math.random().toString(36).slice(2)
    return {
      id,
      username: r.username ?? '',
      relationship: r.relationship ?? '',
      tags: parseTags(r.tags),
      emergencycontact: !!(r.emergencycontact ?? r.emergencyContact),
      email: r.email || '',
      phone: r.phone || r.mobile || '',
      name: r.username ?? '',
      handle: r.handle ?? '',
      status: r.status ?? 'active',
      emotions: null,                       // filled from DB after
      avatar: r.avatar || mascot.Blank,     // updated after emotions load
      friendofuid: r.friendofuid ?? r.ownerUid ?? r.ownerId ?? OWNER_UID,
      userId: r.userId ?? r.friendUserId ?? null
    }
  })
}

async function fetchFriends(){
  if (!OWNER_UID){
    friendsError.value = "No session user. Run sessionStorage.setItem('ownerUid','123') then refresh."
    friends.value = []
    return
  }
  loading.value = true
  friendsError.value = ''
  try {
    const url = `${API_BASE}/friends?friendofuid=${encodeURIComponent(OWNER_UID)}`
    const res = await fetch(url, { headers:{Accept:'application/json'} })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    const rows = Array.isArray(data?.rows) ? data.rows : (Array.isArray(data) ? data : [])
    friends.value = friendRowsToUi(rows)
    expandedIds.value = new Set() // reset manual expansions
    await enrichFriendsWithEmotionsFromDB()
  } catch(e){
    friends.value = []
    friendsError.value = `Could not load friends (${e.message}).`
    pushToast({ type:'error', title:'Load Failed', message:e.message||'Could not load friends.' })
  } finally {
    loading.value = false
  }
}
onMounted(fetchFriends)


async function fetchUsersIndex(){
  try{
    const res = await fetch(`${API_BASE}/users`, { headers:{Accept:'application/json'} })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const payload = await res.json()
    const rows = Array.isArray(payload?.rows) ? payload.rows : (Array.isArray(payload) ? payload : [])
    const map = new Map()
    for (const r of rows){
      const email = (r?.email || '').toLowerCase()
      const uid = r?.userId ?? r?.id
      if (email && uid!=null) map.set(email, Number(uid))
    }
    return map
  } catch { return new Map() }
}

async function fetchFriendEmotions(userId){
  try{
    const r = await fetch(`${API_BASE}/userWeeklyQuizResult?userId=${encodeURIComponent(userId)}`, { headers:{Accept:'application/json'} })
    if (r.ok){
      const d = await r.json()
      if (typeof d?.avgScore === 'number'){
        const mood = clamp((d.avgScore/10)*100)  
        return { mood, energy: mood, sleep: mood }
      }
    }
  }catch{}

  try{
    const r = await fetch(`${API_BASE}/moodMetric?userId=${encodeURIComponent(userId)}`, { headers:{Accept:'application/json'} })
    if (!r.ok) throw new Error()
    let rows = await r.json()
    if (Array.isArray(rows)) { /* ok */ }
    else if (Array.isArray(rows?.rows)) rows = rows.rows
    else if (Array.isArray(rows?.data)) rows = rows.data
    else rows = []

    const avg = a => a.length ? a.reduce((x,y)=>x+y,0)/a.length : 0
    const mood10   = avg(rows.map(x => Number(x.mood ?? x.moodScore   ?? x.score_mood   ?? x.score ?? 0)))
    const energy10 = avg(rows.map(x => Number(x.energy ?? x.energyScore ?? x.score_energy ?? 0)))
    const sleep10  = avg(rows.map(x => Number(x.sleepQuality ?? x.quality ?? x.score_sleep ?? 0)))

    return {
      mood:   clamp((mood10/10)*100),
      energy: clamp((energy10/10)*100),
      sleep:  clamp((sleep10/10)*100)
    }
  }catch{
    return null
  }
}


function friendAvgEmotion(f){
  const e = f?.emotions || {}
  const mood = Number.isFinite(e.mood) ? e.mood : 0
  const energy = Number.isFinite(e.energy) ? e.energy : 0
  const sleep = Number.isFinite(e.sleep) ? e.sleep : 0
  return (mood + energy + sleep) / 3
}
function isLowFriend(f){ return friendAvgEmotion(f) < LOW_THRESHOLD }


async function enrichFriendsWithEmotionsFromDB(){
  if (!friends.value.length) return
  const index = await fetchUsersIndex()

  const pool = 4
  let i = 0
  async function worker(){
    while (i < friends.value.length){
      const idx = i++
      const f = friends.value[idx]
      if (f.emotions && Number.isFinite(f.emotions.mood)) continue
      const uid = f.userId || index.get((f.email||'').toLowerCase())
      if (!uid) continue

      const emo = await fetchFriendEmotions(uid)
      if (emo){
        const avatar = f.avatar && f.avatar!==mascot.Blank ? f.avatar : mascotByEmotion(emo)
        friends.value[idx] = { ...friends.value[idx], emotions: emo, avatar }
      }
    }
  }
  await Promise.all(Array.from({length:pool}, ()=>worker()))
}


const baseFiltered = computed(()=>{
  let list = [...friends.value]
  if (tab.value === 'emergency') list = list.filter(f => !!(f.emergencycontact ?? f.emergencyContact))
  if (query.value){
    const q = query.value.toLowerCase()
    list = list.filter(f =>
      (f.username||f.name||'').toLowerCase().includes(q) ||
      (f.relationship||'').toLowerCase().includes(q) ||
      (Array.isArray(f.tags)?f.tags.join(','):String(f.tags||'')).toLowerCase().includes(q)
    )
  }
  return list
})

const filteredFriends = computed(()=>{
  const list = [...baseFiltered.value]
  switch (sortBy.value) {
    case 'lowFirst':
      list.sort((a,b) => (isLowFriend(b) - isLowFriend(a)) || friendAvgEmotion(a) - friendAvgEmotion(b))
      break
    case 'highFirst':
      list.sort((a,b) => (friendAvgEmotion(b) - friendAvgEmotion(a)))
      break
    case 'nameAZ':
      list.sort((a,b) => (a.username||'').localeCompare(b.username||''))
      break
    case 'nameZA':
      list.sort((a,b) => (b.username||'').localeCompare(a.username||''))
      break
    default:

      break
  }
  return list
})


async function deleteFriend(friend){
  const params = new URLSearchParams({ id:String(friend.id), friendofuid: OWNER_UID })
  const url = `${API_BASE}/friends?${params.toString()}`
  const res = await fetch(url, { method:'DELETE', headers:{Accept:'application/json'} })
  if (!res.ok){
    let msg=''; try{ msg=JSON.stringify(await res.json()) }catch{ try{ msg=await res.text() }catch{} }
    throw new Error(`HTTP ${res.status}${msg?` - ${msg}`:''}`)
  }
  return res.json()
}
async function onRemoveFriend(friend){
  try{
    await deleteFriend(friend)
    pushToast({ type:'success', title:'Removed', message:`Deleted ${friend.username||'friend'}.` })
    await fetchFriends()
  }catch(e){
    pushToast({ type:'error', title:'Delete failed', message:e.message||'Could not delete friend.' })
  }
}
function openAddForm(){ formMode.value='add'; selectedFriend.value=null; showForm.value=true }
function closeForm(){ showForm.value=false }
async function createFriend(payload){
  if (!OWNER_UID) throw new Error('No session user. Please log in.')
  if (!payload.email) throw new Error('Selected user has no email (server requires it).')
  const dup = friends.value.find(f => (f.email||'').toLowerCase() === String(payload.email).toLowerCase())
  if (dup) throw new Error('This email is already in your friends list.')
  const body = {
    friendofuid:Number(OWNER_UID),
    username:payload.username,
    relationship:payload.relationship||'',
    tags:Array.isArray(payload.tags)?payload.tags:[],
    emergencycontact:!!payload.emergencycontact,
    email:payload.email,
    phone:payload.phone||null
  }
  const res = await fetch(`${API_BASE}/friends`, { method:'POST', headers:{'Content-Type':'application/json',Accept:'application/json'}, body:JSON.stringify(body) })
  if (!res.ok){
    let serverMsg=''; try{ serverMsg=JSON.stringify(await res.json()) }catch{ try{ serverMsg=await res.text() }catch{} }
    throw new Error(`HTTP ${res.status}${serverMsg?` - ${serverMsg}`:''}`)
  }
  return res.json()
}
async function handleSaved(){ await fetchFriends(); showForm.value=false; try{ router.replace({ name:'CloseFriends' }) }catch{} }
function onCloseHeader(){}
</script>

<template>
  <div class="min-h-screen relative overflow-x-hidden">
    <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>
    <div class="pointer-events-none absolute inset-0 opacity-20"
      style="background-image:radial-gradient(white 18%, transparent 19%),radial-gradient(white 18%, transparent 19%);background-position:0 0,16px 16px;background-size:32px 32px;">
    </div>

    <div class="relative mx-auto max-w-sm px-3 py-6">
      <!-- toasts -->
      <div class="absolute top-3 inset-x-0 z-40 flex justify-center px-3">
        <TransitionGroup tag="div" class="w-full flex flex-col items-center space-y-2"
          enter-active-class="transition duration-200" enter-from-class="opacity-0 translate-y-1"
          enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-200"
          leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 translate-y-1">
          <div v-for="t in toasts" :key="t.id"
            class="w-full max-w-xs rounded-xl px-3 py-2.5 ring-1 shadow-lg backdrop-blur bg-white/95 flex items-start gap-2"
            :class="[
              t.type==='success'&&'ring-emerald-200 text-emerald-900',
              t.type==='error'&&'ring-rose-200 text-rose-900',
              t.type==='warning'&&'ring-amber-200 text-amber-900',
              t.type==='info'&&'ring-sky-200 text-sky-900'
            ]">
            <div class="text-lg leading-none pt-0.5">{{ toastIcon(t.type) }}</div>
            <div class="min-w-0">
              <div v-if="t.title" class="text-sm font-bold leading-tight">{{ t.title }}</div>
              <div class="text-xs leading-snug opacity-90">{{ t.message }}</div>
            </div>
            <button class="ml-auto text-xs opacity-60 hover:opacity-100 px-2" @click="dismissToast(t.id)">✕</button>
          </div>
        </TransitionGroup>
      </div>

      <ArcadeHeader title="Close Friends" :level="49" :gems="0" :edge="'none'" :coins="18490" @close="onCloseHeader" />

      <div v-if="friendsError" class="mt-4 rounded-xl bg-rose-50 text-rose-700 ring-1 ring-rose-200 px-4 py-3">
        {{ friendsError }}
      </div>

      <div class="mt-4 flex items-center justify-between gap-3">
        <button @click="openAddForm" class="px-4 py-2 rounded-xl bg-sky-500 text-white hover:bg-sky-600 transition">
          + Add Friend
        </button>

       
        <label class="flex items-center gap-2 text-sm text-slate-700">
          <span class="font-semibold">Sort:</span>
          <select
            v-model="sortBy"
            class="rounded-lg border border-sky-200 bg-white/90 px-2 py-1 text-sm shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
          >
            <option v-for="opt in SORT_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </label>
      </div>

      <div class="mt-6 rounded-3xl bg-white/90 ring-1 ring-white shadow p-4 backdrop-blur">
        <FriendFilter :activeTab="tab" :query="query" @update:tab="tab = $event" @update:query="query = $event" />
      </div>

    
      <div class="mt-8 grid grid-cols-1 gap-6">
        <div
          v-for="f in filteredFriends"
          :key="f.id"
          :class="[
            'rounded-[40px] p-1 transition',
            isLowFriend(f)
              ? 'ring-4 ring-rose-400 shadow-[0_22px_60px_-20px_rgba(244,63,94,0.55)] bg-[linear-gradient(135deg,rgba(254,226,226,0.55),rgba(255,255,255,0.45))]'
              : 'ring-1 ring-white/70'
          ]"
        >
          <!-- subtle corner glow accent for low entries -->
          <div
            v-if="isLowFriend(f)"
            aria-hidden="true"
            class="pointer-events-none absolute -ml-4 mt-4 h-16 w-16 rounded-full bg-rose-300/50 blur-xl opacity-60"
          />
          <FriendTile :friend="f" @remove="onRemoveFriend" @more="onMore">
            <FriendCheckins
              v-if="expandedIds.has(f.id)"
              :friend="f"
              :api-base="API_BASE"
            />
          </FriendTile>
        </div>
      </div>

      <div v-if="!loading && filteredFriends.length===0" class="mt-12 text-center text-sky-900/70 text-lg font-medium">
        (｡•́︿•̀｡) No friends yet — add someone you trust.
      </div>
      <div v-if="loading" class="mt-12 text-center text-sky-900/60 animate-pulse">Loading buddies…</div>

      <AddFriendModal
        v-if="showForm"
        :mode="formMode"
        :friend="selectedFriend"
        :alreadyAddedEmails="friends.map(f => (f.email || '').toLowerCase()).filter(Boolean)"
        :onSave="createFriend"
        @saved="handleSaved"
        @close="closeForm"
      />
    </div>
  </div>
</template>
