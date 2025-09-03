<template>
  <div class="fixed inset-0 bg-sky-900/40 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="relative w-full max-w-md overflow-hidden rounded-[28px] p-6 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100">
      <div aria-hidden="true" class="pointer-events-none absolute inset-0 opacity-20 mix-blend-soft-light"
           style="background-image:radial-gradient(white 16%,transparent 17%),radial-gradient(white 16%,transparent 17%);background-position:0 0,14px 14px;background-size:28px 28px;"></div>

      <div class="relative flex justify-between items-center mb-5">
        <h2 class="text-lg font-bold text-slate-800">{{ mode === 'edit' ? 'Edit Friend' : 'Add Friend' }}</h2>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 transition">✕</button>
      </div>

      <form @submit.prevent="onSubmit" class="relative space-y-4">
        <!-- Username autocomplete -->
        <div class="relative">
          <label class="block text-sm font-semibold text-slate-700 mb-1">Username</label>
          <div class="relative">
            <input
              v-model.trim="search"
              type="text"
              :placeholder="loadingUsers ? 'Loading users…' : 'Type a username…'"
              :disabled="loadingUsers"
              @focus="openList()"
              @blur="deferCloseList"
              @keydown.down.prevent="move(1)"
              @keydown.up.prevent="move(-1)"
              @keydown.enter.prevent="chooseHighlighted()"
              @keydown.esc.prevent="closeList()"
              class="w-full rounded-xl border border-sky-200 px-3 py-2 pr-9 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none bg-white/90"
            />
            <span v-if="loadingUsers" class="absolute right-3 top-2.5 text-slate-400 animate-pulse">…</span>

     <ul
  v-show="listOpen && filtered.length"
  class="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-xl border border-sky-200 bg-white shadow-lg"
  @mousedown.prevent
>
  <li
    v-for="(u, i) in filtered"
    :key="u.id"
    @click="addedSet.has(u.id) ? null : selectUser(u)"
    :class="[
      'px-3 py-2 cursor-pointer text-sm flex items-center justify-between',
      i === highlighted ? 'bg-sky-100' : 'hover:bg-sky-50',
      addedSet.has(u.id) ? 'opacity-60 cursor-not-allowed' : ''
    ]"
  >
    <span class="truncate">@{{ u.username }}</span>

    <!-- Only show the “Added” badge when we are not hiding added users -->
    <span
      v-if="addedSet.has(u.id) && SHOW_ADDED_IN_LIST"
      class="ml-3 text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 ring-1 ring-slate-200"
    >
      Added
    </span>
  </li>
</ul>


            <div v-show="listOpen && !filtered.length && !loadingUsers"
                 class="absolute z-20 mt-1 w-full rounded-xl border border-sky-200 bg-white shadow-lg px-3 py-2 text-sm text-slate-500">
              No users found.
            </div>
          </div>
<p v-if="usersError" class="mt-1 text-xs text-rose-600">{{ usersError }}</p>
<p v-if="form.username" class="mt-1 text-xs text-slate-500">
  Selected: <span class="font-medium">@{{ form.username }}</span>
</p>
<!-- Removed the email display lines on purpose -->

          <p v-if="form.email" class="mt-1 text-xs text-slate-500">
            Email: <span class="font-medium">{{ form.email }}</span>
          </p>
          <p v-else-if="form.username" class="mt-1 text-xs text-rose-600">
            This user has no email on file — cannot add friend (server requires email).
          </p>
        </div>

        <div>
  <label class="block text-sm font-semibold text-slate-700 mb-1">Relationship</label>

  <!-- Native select with presets -->
  <select
    v-model="selectedRelationship"
    class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none bg-white/90"
  >
    <option value="" disabled>Select a relationship…</option>
    <option v-for="opt in REL_OPTIONS" :key="opt" :value="opt">{{ opt }}</option>
    <option value="Other…">Other…</option>
  </select>

  <!-- Show when 'Other…' is chosen -->
  <div v-if="selectedRelationship === 'Other…'" class="mt-2">
    <input
      v-model.trim="customRelationship"
      type="text"
      placeholder="Type a custom relationship (e.g., Project Advisor)"
      class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
    />
    <p class="mt-1 text-xs text-slate-500">
      Saving as: <span class="font-medium">{{ form.relationship || '—' }}</span>
    </p>
  </div>
</div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Tags</label>
          <input v-model="tagsInput" type="text" placeholder="Comma-separated (e.g., Family, Buddy)"
                 @keydown.enter.prevent="addTags"
                 class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none" />
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="(tag, idx) in form.tags" :key="idx"
                  class="text-xs bg-sky-100 text-sky-800 px-2 py-1 rounded-full flex items-center gap-1 ring-1 ring-sky-200">
              #{{ tag }}
              <button type="button" @click="removeTag(idx)" class="text-slate-400 hover:text-rose-500">✕</button>
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <input v-model="form.emergencycontact" type="checkbox" id="emergency" class="w-4 h-4 text-rose-500 rounded focus:ring-rose-400" />
          <label for="emergency" class="text-sm text-slate-700">Mark as Emergency Contact</label>
        </div>

        <div class="flex justify-end gap-2 pt-4">
          <button type="button" @click="$emit('close')" class="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-sm">
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!form.friendofuid || !form.email"
            class="px-4 py-2 rounded-xl text-white font-semibold shadow-md transition hover:shadow-lg active:translate-y-[1px]
                   bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)]
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ mode === 'edit' ? 'Save Changes' : 'Add Friend' }}
          </button>
        </div>
      </form>

      <div class="pointer-events-none absolute -right-8 -bottom-8 h-24 w-24 rounded-full bg-sky-200 -z-10"></div>
      <div class="pointer-events-none absolute right-6 -bottom-2 h-8 w-8 rounded-full bg-sky-300 -z-10"></div>
    </div>
  </div>
</template>


<script setup>
import { reactive, ref, watch, computed, onMounted } from 'vue'

const props = defineProps({
  mode: { type: String, default: 'add' },
  friend: { type: Object, default: null },
  // ⬇️ pass the IDs of users already added to your friend list
  alreadyAddedIds: { type: Array, default: () => [] }
})

const emit = defineEmits(['save','close'])

const form = reactive({
  friendofuid: '',
  username: '',
  relationship: '',
  tags: [],
  emergencycontact: false,
  email: '',
  phone: ''
})

const SHOW_ADDED_IN_LIST = false // set true if you prefer showing “Added” (disabled) rows

const tagsInput = ref('')

const userProfiles = ref([])   // [{id, username, email, phone}]
const loadingUsers = ref(false)
const usersError = ref('')

const search = ref('')
const listOpen = ref(false)
const highlighted = ref(-1)
let blurTimer = null

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/,'')
const USERS_URL = `${API_BASE}/users`

function normalizeUsers(data) {
  const rows = Array.isArray(data?.rows) ? data.rows : (Array.isArray(data) ? data : [])
  return rows.map(r => {
    const id = r?.userId ?? r?.id ?? null
    const username = String(r?.username ?? r?.name ?? '')
    const email = r?.email ?? ''
    const phone = r?.mobile ?? r?.phone ?? ''
    return id == null || !username ? null : { id: String(id), username, email, phone }
  }).filter(Boolean)
}

async function fetchProfiles () {
  loadingUsers.value = true
  usersError.value = ''
  try {
    const res = await fetch(USERS_URL, { headers: { Accept: 'application/json' } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    userProfiles.value = normalizeUsers(data)
  } catch (e) {
    usersError.value = `Failed to load users. ${e.message}`
    userProfiles.value = []
  } finally {
    loadingUsers.value = false
  }
}
onMounted(fetchProfiles)

// Fast lookup for “already added”
const addedSet = computed(() => new Set((props.alreadyAddedIds || []).map(String)))

const baseFiltered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const base = userProfiles.value
  if (!q) return base.slice(0, 50)
  return base.filter(u =>
    u.username.toLowerCase().includes(q) ||
    (u.email && u.email.toLowerCase().includes(q)) ||
    (u.phone && u.phone.toLowerCase().includes(q))
  ).slice(0, 50)
})

// Final filtered list: hide already-added unless SHOW_ADDED_IN_LIST = true
const filtered = computed(() => {
  if (SHOW_ADDED_IN_LIST) return baseFiltered.value
  return baseFiltered.value.filter(u => !addedSet.value.has(u.id))
})

function openList() { listOpen.value = true }
function closeList() { listOpen.value = false; highlighted.value = -1 }
function deferCloseList() {
  blurTimer && clearTimeout(blurTimer)
  blurTimer = setTimeout(() => { closeList() }, 120)
}
function move(dir) {
  if (!listOpen.value) listOpen.value = true
  const n = filtered.value.length
  if (!n) return
  highlighted.value = (highlighted.value + dir + n) % n
}
function chooseHighlighted() {
  if (highlighted.value < 0 || highlighted.value >= filtered.value.length) return
  const u = filtered.value[highlighted.value]
  if (addedSet.value.has(u.id)) return // safety if SHOW_ADDED_IN_LIST = true
  selectUser(u)
}
function selectUser(u) {
  if (addedSet.value.has(u.id)) return // disable selection for added users
  form.friendofuid = u.id
  form.username    = u.username
  form.email       = u.email || ''   // still captured for backend; just not displayed
  form.phone       = u.phone || ''
  search.value     = u.username
  closeList()
}

// (…keep your relationship dropdown/watchers/edit-mode prefill etc. unchanged)

function addTags() {
  if (!tagsInput.value.trim()) return
  form.tags.push(...tagsInput.value.split(',').map(t => t.trim()).filter(Boolean))
  tagsInput.value = ''
}
function removeTag(i) { form.tags.splice(i, 1) }

function onSubmit() {
  if (!form.friendofuid) { alert('Please select a user from the list.'); return }
  if (!form.email) { alert('Selected user has no email; server requires email.'); return }
  emit('save', { ...form })
}

// Preset options shown in the dropdown
const REL_OPTIONS = [
  'Friend',
  'Best Friend',
  'Classmate',
  'Sibling',
  'Parent',
  'Partner',]

const selectedRelationship = ref('')    // what’s selected in the <select>
const customRelationship   = ref('')    // free-text when 'Other…' is chosen

// Keep form.relationship in sync with the UI
watch(selectedRelationship, (val) => {
  if (val === 'Other…') {
    form.relationship = customRelationship.value.trim()
  } else {
    form.relationship = val
  }
})
watch(customRelationship, (val) => {
  if (selectedRelationship.value === 'Other…') {
    form.relationship = val.trim()
  }
})

// Prefill edit mode sensibly
watch(() => props.friend, (val) => {
  if (val && props.mode === 'edit') {
    Object.assign(form, {
      friendofuid: String(val.friendofuid ?? ''),
      username: val.username || '',
      relationship: val.relationship || '',
      tags: Array.isArray(val.tags) ? val.tags : [],
      emergencycontact: !!val.emergencycontact,
      email: val.email || '',
      phone: val.phone || ''
    })
    // If existing relationship matches a preset, select it; else use Other…
    const match = REL_OPTIONS.includes(form.relationship) ? form.relationship : 'Other…'
    selectedRelationship.value = match
    if (match === 'Other…') customRelationship.value = form.relationship
    search.value = form.username
  }
}, { immediate: true })
</script>



