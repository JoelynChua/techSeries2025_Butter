<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import ArcadeHeader from '../components/ArcadeHeader.vue'
import FriendFilter from '../components/FriendFilter.vue'
import FriendTile from '../components/FriendTile.vue'
import AddFriendModal from '../components/AddFriendsModal.vue'

import Blank from '@/assets/mascot/Blank.png'
import Concerned from '@/assets/mascot/Concerned.png'
import GoodJob from '@/assets/mascot/GoodJob.png'
import Happy from '@/assets/mascot/Happy.png'
import Love from '@/assets/mascot/Love.png'
import Pout from '@/assets/mascot/Pout.png'
import Proud from '@/assets/mascot/Proud.png'
import Support from '@/assets/mascot/Support.png'

const router = useRouter()
const mascot = { Blank, Concerned, GoodJob, Happy, Love, Pout, Proud, Support }

// const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'
const OWNER_UID =
  (sessionStorage.getItem('ownerUid') || sessionStorage.getItem('userId')) ||
  (import.meta.env.VITE_OWNER_UID || '')

const friends = ref([])
const loading = ref(false)
const friendsError = ref('')
const query = ref('')
const tab = ref('all')

const showForm = ref(false)
const formMode = ref('add')
const selectedFriend = ref(null)

const toasts = ref([])
function pushToast({ type = 'info', title = '', message = '', timeout = 3500 } = {}) {
  const id = Math.random().toString(36).slice(2)
  toasts.value.push({ id, type, title, message })
  if (timeout > 0) setTimeout(() => dismissToast(id), timeout)
}
function dismissToast(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}
function toastIcon(type) {
  if (type === 'success') return '🌿'
  if (type === 'error') return '💥'
  if (type === 'warning') return '⚠️'
  return '🔔'
}

function normalizeEmotion(e) {
  const m = Number.isFinite(e?.mood) ? e.mood : 20
  const en = Number.isFinite(e?.energy) ? e.energy : 60
  const sl = Number.isFinite(e?.sleep) ? e.sleep : 60
  return { mood: clamp(m), energy: clamp(en), sleep: clamp(sl) }
}
function clamp(x) { return Math.max(0, Math.min(100, Number(x) || 0)) }
function mascotByEmotion(e) {
  const { mood, energy, sleep } = normalizeEmotion(e)
  const avg = (mood + energy + sleep) / 3
  if (sleep < 35 && avg < 60) return mascot.Pout
  if (avg < 35) return mascot.Concerned
  if (avg < 45) return mascot.Support
  if (avg >= 90) return mood >= 92 ? mascot.Love : mascot.Proud
  if (avg >= 75) return (mood >= 80 && energy >= 75) ? mascot.Proud : mascot.Happy
  if (avg >= 58) return mascot.GoodJob
  return mascot.Blank
}

function friendRowsToUi(rows) {
  return rows.map(r => {
    const id = r.id ?? r.friendId ?? r.userId ?? Math.random().toString(36).slice(2)
    const emotions = r.emotions ?? { mood: 70, energy: 65, sleep: 60 }
    return {
      id,
      username: r.username ?? '',
      relationship: r.relationship ?? '',
      tags: Array.isArray(r.tags) ? r.tags : [],
      emergencycontact: !!(r.emergencycontact ?? r.emergencyContact),
      email: r.email || '',
      phone: r.phone || r.mobile || '',
      name: r.username ?? '',
      handle: r.handle ?? '',
      status: r.status ?? 'active',
      emotions,
      avatar: r.avatar || mascotByEmotion(emotions),
      emergencyContact: !!(r.emergencycontact ?? r.emergencyContact),
      friendofuid: r.friendofuid ?? r.ownerUid ?? r.ownerId ?? OWNER_UID
    }
  })
}

function candidateFriendUrls() {
  const urls = []
  if (OWNER_UID) {
    urls.push(
      // `${API_BASE}/friends?userId=${encodeURIComponent(OWNER_UID)}`,
      // `${API_BASE}/friends?ownerUid=${encodeURIComponent(OWNER_UID)}`,
      // `${API_BASE}/friends?ownerId=${encodeURIComponent(OWNER_UID)}`,
      `${API_BASE}/friends?friendofuid=${encodeURIComponent(OWNER_UID)}`
    )
  }
  return urls
}

async function robustFetchFriends() {
  const urls = candidateFriendUrls()
  // console.log('Fetching friends from candidate URLs:', urls)
  let lastError = ''
  for (const url of urls) {
    try {
      const res = await fetch(url, { headers: { Accept: 'application/json' } })
      if (!res.ok) { lastError = `HTTP ${res.status}`; continue }
      const data = await res.json()
      const rows = Array.isArray(data?.rows) ? data.rows : (Array.isArray(data) ? data : [])
      return friendRowsToUi(rows)
    } catch (e) {
      lastError = e?.message || 'request failed'
    }
  }
  throw new Error(lastError || 'No candidate URL succeeded')
}

async function fetchFriends() {
  loading.value = true
  friendsError.value = ''
  try {
    friends.value = await robustFetchFriends()
  } catch (e) {
    friends.value = []
    friendsError.value = `Could not load friends (${e.message}). If your API requires a user id, set one in localStorage: ownerUid=123`
    pushToast({
      type: 'error',
      title: 'Load Failed',
      message: 'Could not load friends. If your API needs a user id, set localStorage ownerUid=123'
    })
  } finally {
    loading.value = false
  }
}
onMounted(fetchFriends)

async function deleteFriend(friend) {
  const params = new URLSearchParams()
  params.set('id', String(friend.id))
  if (friend.friendofuid != null && friend.friendofuid !== '') {
    params.set('friendofuid', String(friend.friendofuid))
  }
  const url = `${API_BASE}/friends?${params.toString()}`
  const res = await fetch(url, { method: 'DELETE', headers: { Accept: 'application/json' } })
  if (!res.ok) {
    let msg = ''
    try { msg = JSON.stringify(await res.json()) } catch {
      try { msg = await res.text() } catch { }
    }
    throw new Error(`HTTP ${res.status}${msg ? ` - ${msg}` : ''}`)
  }
  return res.json()
}

async function onRemoveFriend(friend) {
  try {
    await deleteFriend(friend)
    pushToast({ type: 'success', title: 'Removed', message: `Deleted ${friend.username || 'friend'}.` })
    await fetchFriends()
  } catch (e) {
    pushToast({ type: 'error', title: 'Delete failed', message: e.message || 'Could not delete friend.' })
  }
}

const filteredFriends = computed(() => {
  let list = [...friends.value]
  if (tab.value === 'emergency') list = list.filter(f => !!(f.emergencycontact ?? f.emergencyContact))
  if (query.value) {
    const q = query.value.toLowerCase()
    list = list.filter(f =>
      (f.username || f.name || '').toLowerCase().includes(q) ||
      (f.relationship || '').toLowerCase().includes(q) ||
      ((f.tags || []).join(',').toLowerCase().includes(q))
    )
  }
  return list
})

function openAddForm() { formMode.value = 'add'; selectedFriend.value = null; showForm.value = true }
function closeForm() { showForm.value = false }

async function createFriend(payload) {
  if (!payload.friendofuid) throw new Error('Please select a user from the list.')
  if (!payload.email) throw new Error('Selected user has no email (server requires it).')

  const dup = friends.value.find(f => (f.email || '').toLowerCase() === String(payload.email).toLowerCase())
  if (dup) throw new Error('This email is already in your friends list.')

  const body = {
    friendofuid: Number(payload.friendofuid),
    username: payload.username,
    relationship: payload.relationship || '',
    tags: Array.isArray(payload.tags) ? payload.tags : [],
    emergencycontact: !!payload.emergencycontact,
    email: payload.email,
    phone: payload.phone || null
  }

  const res = await fetch(`${API_BASE}/friends`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body)
  })
  if (!res.ok) {
    let serverMsg = ''
    try { serverMsg = JSON.stringify(await res.json()) } catch {
      try { serverMsg = await res.text() } catch { }
    }
    throw new Error(`HTTP ${res.status}${serverMsg ? ` - ${serverMsg}` : ''}`)
  }

  return res.json()
}

async function handleSaved() {
  await fetchFriends()
  showForm.value = false
  try { router.replace({ name: 'CloseFriends' }) } catch { }
}

function onCloseHeader() { }
</script>

<template>
  <div class="min-h-screen relative overflow-x-hidden">
    <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>
    <div class="pointer-events-none absolute inset-0 opacity-20"
      style="background-image:radial-gradient(white 18%, transparent 19%),radial-gradient(white 18%, transparent 19%);background-position:0 0,16px 16px;background-size:32px 32px;">
    </div>

    <div class="relative mx-auto max-w-sm px-3 py-6">
      <!-- Toasts inside phone screen -->
      <div class="absolute top-3 inset-x-0 z-40 flex justify-center px-3">
        <TransitionGroup tag="div" class="w-full flex flex-col items-center space-y-2"
          enter-active-class="transition duration-200" enter-from-class="opacity-0 translate-y-1"
          enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-200"
          leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 translate-y-1">
          <div v-for="t in toasts" :key="t.id"
            class="w-full max-w-xs rounded-xl px-3 py-2.5 ring-1 shadow-lg backdrop-blur bg-white/95 flex items-start gap-2"
            :class="[
              t.type === 'success' && 'ring-emerald-200 text-emerald-900',
              t.type === 'error' && 'ring-rose-200 text-rose-900',
              t.type === 'warning' && 'ring-amber-200 text-amber-900',
              t.type === 'info' && 'ring-sky-200 text-sky-900'
            ]">
            <div class="text-lg leading-none pt-0.5">{{ toastIcon(t.type) }}</div>
            <div class="min-w-0">
              <div v-if="t.title" class="text-sm font-bold leading-tight">{{ t.title }}</div>
              <div class="text-xs leading-snug opacity-90">
                {{ t.message }}
              </div>
            </div>
            <button class="ml-auto text-xs opacity-60 hover:opacity-100 px-2" @click="dismissToast(t.id)"
              aria-label="Dismiss">✕</button>
          </div>
        </TransitionGroup>
      </div>

      <ArcadeHeader title="Close Friends" :level="49" :gems="0" :edge="'none'" :coins="18490" @close="onCloseHeader" />

      <div v-if="friendsError" class="mt-4 rounded-xl bg-rose-50 text-rose-700 ring-1 ring-rose-200 px-4 py-3">
        {{ friendsError }}
      </div>

      <div class="mt-4 flex justify-end">
        <button @click="openAddForm" class="px-4 py-2 rounded-xl bg-sky-500 text-white hover:bg-sky-600 transition">
          + Add Friend
        </button>
      </div>

      <div class="mt-6 rounded-3xl bg-white/90 ring-1 ring-white shadow p-4 backdrop-blur">
        <FriendFilter :activeTab="tab" :query="query" @update:tab="tab = $event" @update:query="query = $event" />
      </div>

      <div class="mt-8 grid grid-cols-1 gap-6">
        <FriendTile v-for="f in filteredFriends" :key="f.id" :friend="f" @remove="onRemoveFriend" />
      </div>

      <div v-if="!loading && filteredFriends.length === 0"
        class="mt-12 text-center text-sky-900/70 text-lg font-medium">
        (｡•́︿•̀｡) No friends yet — add someone you trust.
      </div>
      <div v-if="loading" class="mt-12 text-center text-sky-900/60 animate-pulse">
        Loading buddies…
      </div>

      <AddFriendModal v-if="showForm" :mode="formMode" :friend="selectedFriend"
        :alreadyAddedEmails="friends.map(f => (f.email || '').toLowerCase()).filter(Boolean)" :onSave="createFriend"
        @saved="handleSaved" @close="closeForm" />
    </div>
  </div>
</template>
