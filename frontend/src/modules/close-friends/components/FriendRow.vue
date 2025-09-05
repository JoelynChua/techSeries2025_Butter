<template>

  <div
    class="relative overflow-hidden rounded-[28px] p-4 ring-1
           shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)]
           ring-sky-100 bg-gradient-to-b from-sky-50 to-sky-100"
  >
  
    <div
      aria-hidden="true"
      class="pointer-events-none absolute inset-0 opacity-25 mix-blend-soft-light"
      style="
        background-image:
          radial-gradient(white 16%, transparent 17%),
          radial-gradient(white 16%, transparent 17%);
        background-position: 0 0, 14px 14px;
        background-size: 28px 28px;
      "
    ></div>

    <div class="relative flex items-start gap-4">
      <!-- avatar: glossy sticker with halo -->
      <div class="relative shrink-0">
        <div
          class="rounded-2xl p-1 bg-white shadow-[0_6px_18px_rgba(8,36,100,0.08)]
                 ring-1 ring-slate-100"
        >
          <div class="relative">
            <!-- halo -->
            <div class="absolute inset-0 -z-10 rounded-xl blur-md
                        bg-[radial-gradient(closest-side,rgba(99,179,237,0.35),transparent)]"></div>
            <img
              :src="friend.avatar"
              alt=""
              class="h-16 w-16 rounded-xl object-cover"
            />
          </div>
        </div>

        <!-- online pulse -->
        <span
          v-if="friend.status==='active'"
          class="absolute -right-1 -top-1 inline-block h-3 w-3 rounded-full bg-emerald-400 ring-2 ring-white"
        >
        </span>
        <span
          v-if="friend.status==='active'"
          class="absolute -right-1.5 -top-1.5 h-5 w-5 rounded-full animate-ping bg-emerald-300/60"
        ></span>

        <!-- tiny pet badge -->
        <span
          class="absolute -bottom-2 left-2 select-none text-base drop-shadow-sm"
          :title="petLabel(friend.avatar)"
        >
          {{ petIcon(friend.avatar) }}
        </span>
      </div>

      <div class="min-w-0 flex-1">
        <!-- top row -->
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <h3 class="truncate text-[17px] font-extrabold text-slate-800 tracking-tight">
              {{ friend.name }}
            </h3>
            <p class="truncate text-xs text-slate-500">
              {{ friend.handle }} · {{ friend.email || friend.phone }}
            </p>
          </div>

          <!-- actions: soft sticky buttons -->
          <div class="shrink-0 flex items-center gap-2">
            <button v-if="friend.status==='active'"
              class="rounded-full bg-rose-200/80 px-3 py-1 text-xs font-semibold text-rose-800
                     shadow-sm hover:bg-rose-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-300"
              @click="$emit('remove', friend.id)">
              Remove
            </button>
            <template v-else>
              <button
                class="rounded-full bg-emerald-200/80 px-3 py-1 text-xs font-semibold text-emerald-900
                       shadow-sm hover:bg-emerald-300 focus-visible:ring-2 focus-visible:ring-emerald-300"
                @click="$emit('approve', friend.id)">
                Approve
              </button>
              <button
                class="rounded-full bg-indigo-200/80 px-3 py-1 text-xs font-semibold text-indigo-900
                       shadow-sm hover:bg-indigo-300 focus-visible:ring-2 focus-visible:ring-indigo-300"
                @click="$emit('resend', friend.id)">
                Resend
              </button>
              <button
                class="rounded-full bg-rose-200/80 px-3 py-1 text-xs font-semibold text-rose-900
                       shadow-sm hover:bg-rose-300 focus-visible:ring-2 focus-visible:ring-rose-300"
                @click="$emit('revoke', friend.id)">
                Revoke
              </button>
            </template>
          </div>
        </div>

        <!-- divider (dotted) -->
        <div class="mt-3 border-t border-dotted border-sky-200/70"></div>

        <!-- chips -->
        <div class="mt-3 flex flex-wrap items-center gap-2 text-[11px]">
          <span
            v-if="friend.status==='pending'"
            class="inline-flex items-center gap-1 rounded-full bg-amber-200/80 px-3 py-1 font-medium text-amber-900 ring-1 ring-amber-300/60">
            🕒 Pending
          </span>
          <span
            v-if="friend.status==='active'"
            class="inline-flex items-center gap-1 rounded-full bg-emerald-200/80 px-3 py-1 font-medium text-emerald-900 ring-1 ring-emerald-300/60">
            ✅ Active
          </span>

          <span class="inline-flex items-center gap-1 rounded-full bg-pink-200/80 px-3 py-1 font-medium text-pink-900 ring-1 ring-pink-300/60">
            🤝 {{ friend.relationship || 'Buddy' }}
          </span>

          <template v-for="t in (friend.tags || [])" :key="t">
            <span class="rounded-full bg-sky-200/80 px-3 py-1 font-medium text-sky-900 ring-1 ring-sky-300/60">
              #{{ t }}
            </span>
          </template>
        </div>

        <!-- bottom row -->
        <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div class="text-xs text-slate-600">
            <span class="mr-1 font-semibold text-slate-800">Alerts:</span>
            <span class="font-medium space-x-1">
              <span v-if="friend.notifyOn?.redFlags">🚨 Red Flags</span>
              <span v-if="friend.notifyOn?.lowMoodStreak">• 😔 Low Mood</span>
              <span v-if="friend.notifyOn?.sleepDrop">• 💤 Sleep Drop</span>
              <span
                v-if="!friend.notifyOn?.redFlags && !friend.notifyOn?.lowMoodStreak && !friend.notifyOn?.sleepDrop"
                class="text-slate-400"
              >None</span>
            </span>
          </div>

          <!-- primary action: sky candy gradient -->
          <button
            class="rounded-[16px] px-4 py-2 text-white font-semibold shadow-md transition
                   hover:shadow-lg active:translate-y-[1px]
                   bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)] focus-visible:ring-2 focus-visible:ring-sky-300"
            @click="$emit('update',{ id: friend.id, patch: { opened: true } })"
          >
            Continue
          </button>
        </div>
      </div>
    </div>

    <!-- bubbly blobs -->
    <div class="pointer-events-none absolute -right-6 -bottom-6 h-24 w-24 rounded-full bg-sky-200"></div>
    <div class="pointer-events-none absolute right-8 -bottom-2 h-10 w-10 rounded-full bg-sky-300"></div>
  </div>
</template>

<script setup>
const props = defineProps({ friend: { type: Object, required: true } })
defineEmits(['remove','approve','resend','revoke','update'])

// infer a cute icon from avatar path/name (works with /avatars/pets/*.png)
function petIcon(src = '') {
  const s = src.toLowerCase()
  if (s.includes('cat')) return '🐱'
  if (s.includes('dog')) return '🐶'
  if (s.includes('bunny') || s.includes('rabbit')) return '🐰'
  if (s.includes('hamster')) return '🐹'
  if (s.includes('bird')) return '🐦'
  return '🌟'
}
function petLabel(src = '') {
  const s = src.toLowerCase()
  if (s.includes('cat')) return 'Cat'
  if (s.includes('dog')) return 'Dog'
  if (s.includes('bunny') || s.includes('rabbit')) return 'Bunny'
  if (s.includes('hamster')) return 'Hamster'
  if (s.includes('bird')) return 'Bird'
  return 'Buddy'
}
</script>
