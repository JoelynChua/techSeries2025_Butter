<script setup>
import { ref, computed, onMounted } from 'vue'
import ArcadeHeader from '../components/ArcadeHeader.vue'
import FriendFilter from '../components/FriendFilter.vue'
import FriendTile from '../components/FriendTile.vue'
import AddFriendModal from '../components/AddFriendsModal.vue'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/,'')
const OWNER_UID =
  (localStorage.getItem('ownerUid') || localStorage.getItem('userId')) ||
  (import.meta.env.VITE_OWNER_UID || '')

const friends = ref([])
const loading = ref(false)
const friendsError = ref('')
const query = ref('')
const tab = ref('all')

const showForm = ref(false)
const formMode = ref('add')
const selectedFriend = ref(null)

function friendRowsToUi(rows) {
  return rows.map(r => ({
    id: r.id ?? r.friendId ?? r.userId ?? Math.random().toString(36).slice(2),
    username: r.username ?? '',
    relationship: r.relationship ?? '',
    tags: Array.isArray(r.tags) ? r.tags : [],
    emergencycontact: !!(r.emergencycontact ?? r.emergencyContact),
    email: r.email || '',
    phone: r.phone || r.mobile || '',
    // fields FriendTile may read
    name: r.username ?? '',
    handle: r.handle ?? '',
    status: r.status ?? 'active',
    emotions: r.emotions ?? { mood: 70, energy: 65, sleep: 60 },
    avatar: r.avatar || 'https://picsum.photos/seed/friend/256/256',
    emergencyContact: !!(r.emergencycontact ?? r.emergencyContact),
  }))
}

function candidateFriendUrls() {
  const urls = [`${API_BASE}/friends`]
  if (OWNER_UID) {
    urls.push(
      `${API_BASE}/friends?userId=${encodeURIComponent(OWNER_UID)}`,
      `${API_BASE}/friends?ownerUid=${encodeURIComponent(OWNER_UID)}`,
      `${API_BASE}/friends?ownerId=${encodeURIComponent(OWNER_UID)}`,
      `${API_BASE}/friends?friendofuid=${encodeURIComponent(OWNER_UID)}`
    )
  }
  return urls
}

async function robustFetchFriends() {
  const urls = candidateFriendUrls()
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

async function fetchFriends () {
  loading.value = true
  friendsError.value = ''
  try {
    friends.value = await robustFetchFriends()
  } catch (e) {
    friends.value = []
    friendsError.value = `Could not load friends (${e.message}). If your API requires a user id, set one in localStorage: ownerUid=123`
    console.error('[friends] load failed:', e, { tried: candidateFriendUrls() })
  } finally {
    loading.value = false
  }
}
onMounted(fetchFriends)

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

function openAddForm () { formMode.value = 'add'; selectedFriend.value = null; showForm.value = true }
function closeForm () { showForm.value = false }

async function saveFriend (payload) {
  try {
    if (!payload.friendofuid) { alert('Pick a user from the list.'); return }
    if (!payload.email) { alert('Selected user has no email (server requires it).'); return }

    const dup = friends.value.find(f => (f.email || '').toLowerCase() === payload.email.toLowerCase())
    if (dup) { alert('This email is already in your friends list.'); return }

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
      try { serverMsg = JSON.stringify(await res.json()) } catch { try { serverMsg = await res.text() } catch {} }
      throw new Error(`HTTP ${res.status}${serverMsg ? ` - ${serverMsg}` : ''}`)
    }

    await fetchFriends()
    showForm.value = false
  } catch (e) {
    alert(`Failed to add friend. ${e.message}`)
    console.error('saveFriend error:', e)
  }
}

function onCloseHeader () {}
</script>

<template>
  <div class="min-h-screen relative overflow-x-hidden">
    <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>
    <div
      class="pointer-events-none absolute inset-0 opacity-20"
      style="
        background-image:
          radial-gradient(white 18%, transparent 19%),
          radial-gradient(white 18%, transparent 19%);
        background-position: 0 0, 16px 16px;
        background-size: 32px 32px;
      "
    ></div>

    <div class="relative mx-auto max-w-5xl px-5 py-6">
      <ArcadeHeader
        title="Close Friends"
        :level="49"
        :gems="0"
        :edge="'none'"
        :coins="18490"
        @close="onCloseHeader"
      />

      <div v-if="friendsError" class="mt-4 rounded-xl bg-rose-50 text-rose-700 ring-1 ring-rose-200 px-4 py-3">
        {{ friendsError }}
      </div>

      <div class="mt-4 flex justify-end">
        <button
          @click="openAddForm"
          class="px-4 py-2 rounded-xl bg-sky-500 text-white hover:bg-sky-600 transition"
        >
          + Add Friend
        </button>
      </div>

      <div class="mt-6 rounded-3xl bg-white/90 ring-1 ring-white shadow-[0_16px_36px_-18px_rgba(2,132,199,0.35)] p-4 backdrop-blur">
        <FriendFilter
          :activeTab="tab"
          :query="query"
          @update:tab="tab = $event"
          @update:query="query = $event"
        />
      </div>

      <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <FriendTile
          v-for="f in filteredFriends"
          :key="f.id"
          :friend="f"
          @remove="() => {}"
          @update="() => {}"
          @approve="() => {}"
          @resend="() => {}"
          @revoke="() => {}"
        />
      </div>

      <div v-if="!loading && filteredFriends.length === 0" class="mt-12 text-center text-sky-900/70 text-lg font-medium">
        (｡•́︿•̀｡) No friends yet — add someone you trust.
      </div>
      <div v-if="loading" class="mt-12 text-center text-sky-900/60 animate-pulse">
        Loading buddies…
      </div>

      <AddFriendModal
        v-if="showForm"
        :mode="formMode"
        :friend="selectedFriend"
        @save="saveFriend"
        @close="closeForm"
      />
    </div>
  </div>
</template>
