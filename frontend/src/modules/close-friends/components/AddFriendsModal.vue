<template>
  
  <div
    class="absolute inset-0 z-[60] flex items-center justify-center bg-sky-900/40 backdrop-blur-sm"
    @click.self="$emit('close')"
    role="dialog"
    aria-modal="true"
  >
    <div
      class="relative w-[92vw] max-w-md overflow-hidden rounded-[28px] p-6 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100 pointer-events-auto"
    >
      <div aria-hidden="true" class="pointer-events-none absolute inset-0 opacity-20 mix-blend-soft-light"
           style="background-image:radial-gradient(white 16%,transparent 17%),radial-gradient(white 16%,transparent 17%);background-position:0 0,14px 14px;background-size:28px 28px;"></div>

      <div class="relative flex justify-between items-center mb-5">
        <h2 class="text-lg font-bold text-slate-800">{{ mode === 'edit' ? 'Edit Friend' : 'Add Friend' }}</h2>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 transition" aria-label="Close">✕</button>
      </div>

      <form @submit.prevent="onSubmit" class="relative space-y-4" novalidate>
        <!-- Username autocomplete -->
        <div class="relative">
          <label class="block text-sm font-semibold text-slate-700 mb-1">Username</label>
          <div class="relative">
            <input
              v-model.trim="search"
              type="text"
              :placeholder="loadingUsers ? 'Loading users…' : 'Type a username…'"
              :disabled="loadingUsers || saving"
              @focus="openList()"
              @blur="deferCloseList"
              @keydown.down.prevent="move(1)"
              @keydown.up.prevent="move(-1)"
              @keydown.enter.prevent="chooseHighlighted()"
              @keydown.esc.prevent="closeList()"
              class="w-full rounded-xl border border-sky-200 px-3 py-2 pr-9 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none bg-white/90"
              autocomplete="off"
              aria-autocomplete="list"
              :aria-expanded="listOpen ? 'true' : 'false'"
              aria-controls="user-autocomplete-list"
            />
            <span v-if="loadingUsers" class="absolute right-3 top-2.5 text-slate-400 animate-pulse">…</span>

            <ul
              v-show="listOpen && filtered.length"
              id="user-autocomplete-list"
              class="absolute z-30 mt-1 max-h-60 w-full overflow-auto rounded-xl border border-sky-200 bg-white shadow-lg"
              @mousedown.prevent
              role="listbox"
            >
              <li
                v-for="(u, i) in filtered"
                :key="u.id"
                @click="addedEmailSet.has(u._emailLc) ? null : selectUser(u)"
                :class="[
                  'px-3 py-2 cursor-pointer text-sm flex items-center justify-between',
                  i === highlighted ? 'bg-sky-100' : 'hover:bg-sky-50',
                  addedEmailSet.has(u._emailLc) ? 'opacity-60 cursor-not-allowed' : ''
                ]"
                role="option"
                :aria-selected="i === highlighted"
              >
                <span class="truncate">@{{ u.username }}</span>
                <span
                  v-if="addedEmailSet.has(u._emailLc) && SHOW_ADDED_IN_LIST"
                  class="ml-3 text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 ring-1 ring-slate-200"
                >Added</span>
              </li>
            </ul>

            <div v-show="listOpen && !filtered.length && !loadingUsers"
                 class="absolute z-30 mt-1 w-full rounded-xl border border-sky-200 bg-white shadow-lg px-3 py-2 text-sm text-slate-500">
              No users found.
            </div>
          </div>
          <p v-if="usersError" class="mt-1 text-xs text-rose-600">{{ usersError }}</p>
          <p v-if="form.username" class="mt-1 text-xs text-slate-500">
            Selected: <span class="font-medium">@{{ form.username }}</span>
          </p>
        </div>

        <!-- Relationship -->
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Relationship</label>
          <select
            v-model="selectedRelationship"
            :disabled="saving"
            class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none bg-white/90"
          >
            <option value="" disabled>Select a relationship…</option>
            <option v-for="opt in REL_OPTIONS" :key="opt" :value="opt">{{ opt }}</option>
            <option value="Other…">Other…</option>
          </select>

          <div v-if="selectedRelationship === 'Other…'" class="mt-2">
            <input
              v-model.trim="customRelationship"
              :disabled="saving"
              type="text"
              placeholder="Type a custom relationship (e.g., Project Advisor)"
              class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
            />
            <p class="mt-1 text-xs text-slate-500">
              Saving as: <span class="font-medium">{{ form.relationship || '—' }}</span>
            </p>
          </div>
        </div>

        <!-- Tags -->
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Tags</label>
          <input
            v-model="tagsInput"
            :disabled="saving"
            type="text"
            placeholder="Comma-separated (e.g., Family, Buddy)"
            @keydown.enter.prevent="addTags"
            class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
          />
          <div class="mt-2 flex flex-wrap gap-2">
            <span
              v-for="(tag, idx) in form.tags"
              :key="idx"
              class="text-xs bg-sky-100 text-sky-800 px-2 py-1 rounded-full flex items-center gap-1 ring-1 ring-sky-200"
            >
              #{{ tag }}
              <button type="button" :disabled="saving" @click="removeTag(idx)" class="text-slate-400 hover:text-rose-500" aria-label="Remove tag">✕</button>
            </span>
          </div>
        </div>

        <!-- Emergency contact -->
        <div class="flex items-center gap-2">
          <input v-model="form.emergencycontact" :disabled="saving" type="checkbox" id="emergency" class="w-4 h-4 text-rose-500 rounded focus:ring-rose-400" />
          <label for="emergency" class="text-sm text-slate-700">Mark as Emergency Contact</label>
        </div>

        <!-- Inline notifications -->
        <div class="space-y-2">
          <p v-if="formError" class="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">{{ formError }}</p>
          <p v-if="serverError" class="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">{{ serverError }}</p>
          <p v-if="successMsg" class="text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">{{ successMsg }}</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-2">
          <button type="button" :disabled="saving" @click="$emit('close')" class="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-sm">
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!form.friendofuid || saving"
            class="px-4 py-2 rounded-xl text-white font-semibold shadow-md transition hover:shadow-lg active:translate-y-[1px]
                   bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)]
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!saving">{{ mode === 'edit' ? 'Save Changes' : 'Add Friend' }}</span>
            <span v-else>Saving…</span>
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
  alreadyAddedEmails: { type: Array, default: () => [] },
  onSave: { type: Function, default: null }
})

const emit = defineEmits(['saved','close'])

const form = reactive({
  friendofuid: '',
  username: '',
  relationship: '',
  tags: [],
  emergencycontact: false,
  email: '',
  phone: ''
})

const SHOW_ADDED_IN_LIST = false
const tagsInput = ref('')

const userProfiles = ref([])
const loadingUsers = ref(false)
const usersError = ref('')

const search = ref('')
const listOpen = ref(false)
const highlighted = ref(-1)
let blurTimer = null

const formError   = ref('')
const serverError = ref('')
const successMsg  = ref('')
const saving      = ref(false)

// const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:5000").replace(/\/+$/,'')
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'
const USERS_URL = `${API_BASE}/users`

/** current session self */
const SELF_UID = String(
  sessionStorage.getItem('ownerUid') ||
  sessionStorage.getItem('userId')   ||
  localStorage.getItem('ownerUid')   ||
  localStorage.getItem('userId')     ||
  import.meta.env.VITE_OWNER_UID     || ''
).trim()
const SELF_EMAIL = String(
  sessionStorage.getItem('email') ||
  localStorage.getItem('email')   || ''
).toLowerCase()

function normalizeUsers(data) {
  const rows = Array.isArray(data?.rows) ? data.rows : (Array.isArray(data) ? data : [])
  return rows.map(r => {
    const id = r?.userId ?? r?.id ?? null
    const username = String(r?.username ?? r?.name ?? '')
    const email = r?.email ?? ''
    const phone = r?.mobile ?? r?.phone ?? ''
    const _emailLc = (email || '').toLowerCase()
    return id == null || !username ? null : { id: String(id), username, email, phone, _emailLc }
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

const addedEmailSet = computed(() => new Set((props.alreadyAddedEmails || []).map(e => String(e).toLowerCase())))

/** exclude current session user here */
const baseFiltered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const withoutSelf = userProfiles.value.filter(u => {
    const notSelfId    = !SELF_UID   || String(u.id) !== String(SELF_UID)
    const notSelfEmail = !SELF_EMAIL || u._emailLc !== SELF_EMAIL
    return notSelfId && notSelfEmail
  })
  if (!q) return withoutSelf.slice(0, 50)
  return withoutSelf.filter(u => u.username.toLowerCase().includes(q)).slice(0, 50)
})

const filtered = computed(() =>
  SHOW_ADDED_IN_LIST
    ? baseFiltered.value
    : baseFiltered.value.filter(u => !addedEmailSet.value.has(u._emailLc))
)

function openList() { listOpen.value = true }
function closeList() { listOpen.value = false; highlighted.value = -1 }
function deferCloseList() { blurTimer && clearTimeout(blurTimer); blurTimer = setTimeout(() => { closeList() }, 120) }
function move(dir) { if (!listOpen.value) listOpen.value = true; const n = filtered.value.length; if (!n) return; highlighted.value = (highlighted.value + dir + n) % n }
function chooseHighlighted() { if (highlighted.value < 0 || highlighted.value >= filtered.value.length) return; const u = filtered.value[highlighted.value]; if (addedEmailSet.value.has(u._emailLc)) return; selectUser(u) }

/** block selecting self */
function selectUser(u) {
  if ((SELF_UID && String(u.id) === String(SELF_UID)) ||
      (SELF_EMAIL && u._emailLc === SELF_EMAIL)) {
    usersError.value = 'You can’t add yourself as a friend.'
    return
  }
  if (addedEmailSet.value.has(u._emailLc)) return

  const ownerId =
    (sessionStorage.getItem('ownerUid') || sessionStorage.getItem('userId')) ??
    (localStorage.getItem('ownerUid')   || localStorage.getItem('userId')) ??
    import.meta.env.VITE_OWNER_UID ?? 0

  form.friendofuid = Number(ownerId)
  form.username    = u.username
  form.email       = u.email || ''
  form.phone       = u.phone || ''
  search.value     = u.username
  closeList()
  if (formError.value) formError.value = ''
}

function addTags() {
  if (!tagsInput.value.trim()) return
  form.tags.push(...tagsInput.value.split(',').map(t => t.trim()).filter(Boolean))
  tagsInput.value = ''
}
function removeTag(i) { form.tags.splice(i, 1) }

async function onSubmit() {
  formError.value = ''
  serverError.value = ''
  successMsg.value = ''

  if (!form.friendofuid) { formError.value = 'Please select a user from the list.'; return }
  if (!form.email) { formError.value = 'Selected user has no email; cannot add friend.'; return }

  const payload = { ...form }

  try {
    saving.value = true
    if (typeof props.onSave === 'function') {
      await props.onSave(payload)
    } else {
      throw new Error('onSave handler not provided')
    }
    successMsg.value = props.mode === 'edit' ? 'Friend updated successfully.' : 'Friend added successfully.'
    setTimeout(() => { emit('saved') }, 600)
  } catch (e) {
    serverError.value = e?.message ? `Failed to save: ${e.message}` : 'Failed to save. Please try again.'
  } finally {
    saving.value = false
  }
}

const REL_OPTIONS = ['Friend','Best Friend','Classmate','Sibling','Parent','Partner']
const selectedRelationship = ref('')
const customRelationship   = ref('')

watch(selectedRelationship, (val) => { form.relationship = val === 'Other…' ? customRelationship.value.trim() : val })
watch(customRelationship, (val) => { if (selectedRelationship.value === 'Other…') form.relationship = val.trim() })

watch(() => props.friend, (val) => {
  if (val && props.mode === 'edit') {
    Object.assign(form, {
      friendofuid: Number(val.friendofuid ?? (sessionStorage.getItem('ownerUid') || sessionStorage.getItem('userId') || localStorage.getItem('ownerUid') || localStorage.getItem('userId') || import.meta.env.VITE_OWNER_UID || 0)),
      username: val.username || '',
      relationship: val.relationship || '',
      tags: Array.isArray(val.tags) ? val.tags : [],
      emergencycontact: !!val.emergencycontact,
      email: val.email || '',
      phone: val.phone || ''
    })
    const match = REL_OPTIONS.includes(form.relationship) ? form.relationship : 'Other…'
    selectedRelationship.value = match
    if (match === 'Other…') customRelationship.value = form.relationship
    search.value = form.username
  }
}, { immediate: true })
</script>
