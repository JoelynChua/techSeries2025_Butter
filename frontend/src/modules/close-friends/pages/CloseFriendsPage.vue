<script setup>
import { ref, computed, onMounted } from 'vue'
import ArcadeHeader from '../components/ArcadeHeader.vue'
import FriendFilter from '../components/FriendFilter.vue'
import FriendForm from '../components/FriendForm.vue'
import FriendTile from '../components/FriendTile.vue'
import * as api from '../__mocks__/friends.mock.js'

const friends = ref([])
const loading = ref(false)
const query = ref('')
const tab = ref('all')

const showForm = ref(false)
const formMode = ref('add')
const selectedFriend = ref(null)

async function fetchFriends () {
  loading.value = true
  friends.value = await api.listFriends(query.value)
  loading.value = false
}
onMounted(fetchFriends)

const filteredFriends = computed(() => {
  let list = [...friends.value]
  if (tab.value === 'active') list = list.filter(f => f.status === 'active')
  if (tab.value === 'pending') list = list.filter(f => f.status === 'pending')
  if (tab.value === 'emergency') list = list.filter(f => f.emergencyContact)
  if (query.value) {
    const q = query.value.toLowerCase()
    list = list.filter(f =>
      f.name.toLowerCase().includes(q) ||
      (f.handle || '').toLowerCase().includes(q) ||
      (f.relationship || '').toLowerCase().includes(q) ||
      ((f.tags || []).join(',').toLowerCase().includes(q))
    )
  }
  return list
})

function openAddForm () { formMode.value = 'add'; selectedFriend.value = null; showForm.value = true }
function closeForm () { showForm.value = false }

async function saveFriend (payload) {
  if (formMode.value === 'add') await api.createFriend(payload)
  else if (formMode.value === 'edit' && selectedFriend.value) await api.updateFriend(selectedFriend.value.id, payload)
  showForm.value = false
  await fetchFriends()
}

async function removeFriend (id) { await api.deleteFriend(id); await fetchFriends() }
async function updateFriend ({ id, patch }) { await api.updateFriend(id, patch); await fetchFriends() }
async function approveFriend (id) { await api.approveInvite(id); await fetchFriends() }
async function resendInvite (id) { await api.resendInvite(id) }
async function revokeInvite (id) { await api.revokeInvite(id); await fetchFriends() }

function onCloseHeader () {
  
}
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
        :edge="none"
        :coins="18490"
        @close="onCloseHeader"
      />

    
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
          @remove="removeFriend"
          @update="updateFriend"
          @approve="approveFriend"
          @resend="resendInvite"
          @revoke="revokeInvite"
        />
      </div>

   
      <div v-if="!loading && filteredFriends.length === 0"
           class="mt-12 text-center text-sky-900/70 text-lg font-medium">
        (｡•́︿•̀｡) No friends yet — add someone you trust.
      </div>
      <div v-if="loading" class="mt-12 text-center text-sky-900/60 animate-pulse">
        Loading buddies…
      </div>

   
      <FriendForm
        v-if="showForm"
        :mode="formMode"
        :friend="selectedFriend"
        @save="saveFriend"
        @close="closeForm"
      />
    </div>
  </div>
</template>
