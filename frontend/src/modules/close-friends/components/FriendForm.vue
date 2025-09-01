<template>
  <div class="fixed inset-0 bg-sky-900/40 backdrop-blur-sm flex items-center justify-center z-50">
    <!-- card -->
    <div
      class="relative w-full max-w-md overflow-hidden rounded-[28px] p-6 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100"
    >
      <!-- egg pattern -->
      <div
        aria-hidden="true"
        class="pointer-events-none absolute inset-0 opacity-20 mix-blend-soft-light"
        style="
          background-image:
            radial-gradient(white 16%, transparent 17%),
            radial-gradient(white 16%, transparent 17%);
          background-position: 0 0, 14px 14px;
          background-size: 28px 28px;
        "
      ></div>

      <!-- header -->
      <div class="relative flex justify-between items-center mb-5">
        <h2 class="text-lg font-bold text-slate-800">
          {{ mode === 'edit' ? 'Edit Friend' : 'Add Friend' }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-slate-400 hover:text-slate-700 transition"
        >
          ✕
        </button>
      </div>

      <!-- form -->
      <form @submit.prevent="onSubmit" class="relative space-y-4">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Name</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Phone</label>
          <input
            v-model="form.phone"
            type="tel"
            class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Relationship</label>
          <input
            v-model="form.relationship"
            type="text"
            class="w-full rounded-xl border border-sky-200 px-3 py-2 shadow-sm focus:ring-2 focus:ring-sky-400 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">Tags</label>
          <input
            v-model="tagsInput"
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
              <button
                type="button"
                @click="removeTag(idx)"
                class="text-slate-400 hover:text-rose-500"
              >
                ✕
              </button>
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="form.emergencyContact"
            type="checkbox"
            id="emergency"
            class="w-4 h-4 text-rose-500 rounded focus:ring-rose-400"
          />
          <label for="emergency" class="text-sm text-slate-700">
            Mark as Emergency Contact
          </label>
        </div>

        <!-- footer -->
        <div class="flex justify-end gap-2 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 rounded-xl text-white font-semibold shadow-md transition hover:shadow-lg active:translate-y-[1px]
                   bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)]"
          >
            {{ mode === 'edit' ? 'Save Changes' : 'Add Friend' }}
          </button>
        </div>
      </form>

      <!-- corner blobs -->
      <div class="pointer-events-none absolute -right-8 -bottom-8 h-24 w-24 rounded-full bg-sky-200"></div>
      <div class="pointer-events-none absolute right-6 -bottom-2 h-8 w-8 rounded-full bg-sky-300"></div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
const props = defineProps({ mode: { type: String, default: 'add' }, friend: { type: Object, default: null } })
const emit = defineEmits(['save','close'])

const form = reactive({ name: '', email: '', phone: '', relationship: '', tags: [], emergencyContact: false })
const tagsInput = ref('')

watch(() => props.friend, (val) => {
  if (val && props.mode === 'edit') {
    Object.assign(form, {
      name: val.name || '', email: val.email || '', phone: val.phone || '',
      relationship: val.relationship || '', tags: val.tags || [], emergencyContact: !!val.emergencyContact
    })
  }
}, { immediate: true })

function addTags() {
  if (!tagsInput.value.trim()) return
  form.tags.push(...tagsInput.value.split(',').map(t => t.trim()))
  tagsInput.value = ''
}
function removeTag(i) { form.tags.splice(i, 1) }
function onSubmit() { emit('save', { ...form }) }
</script>
