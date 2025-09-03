<template>
  <div
    class="relative overflow-hidden rounded-[32px] bg-white p-4 ring-2 ring-white shadow-[0_16px_36px_-12px_rgba(2,132,199,0.4)]"
  >
  
    <div aria-hidden="true" class="pointer-events-none absolute -right-6 -bottom-6 h-28 w-28 rounded-full bg-sky-200 z-0"></div>
    <div aria-hidden="true" class="pointer-events-none absolute right-6 -bottom-2 h-10 w-10 rounded-full bg-sky-300 z-0"></div>
    <div aria-hidden="true" class="pointer-events-none absolute -right-6 -bottom-6 h-28 w-28 rounded-full bg-sky-200 z-0 hidden sm:block"></div>

    
    <div class="relative z-10 flex flex-col items-center">
  
      <div class="relative">
        <img
          :src="friend.avatar"
          alt=""
          class="h-32 w-32 rounded-[28px] object-cover ring-4 ring-white shadow-[0_10px_20px_-10px_rgba(0,0,0,0.45)]"
        />
        <span
          v-if="friend.status==='active'"
          class="absolute -right-1 -top-1 h-4 w-4 rounded-full bg-emerald-400 ring-2 ring-white"
        />
      </div>

    
      <div class="mt-4 w-full text-center">
        <div class="truncate text-lg font-extrabold text-sky-900 drop-shadow-[0_1px_0_rgba(255,255,255,0.9)]">
          {{ friend.name }}
        </div>
        <div class="truncate text-sm text-sky-900/70">
          {{ friend.handle }}
        </div>
      </div>

      
      <div class="mt-4 flex flex-wrap justify-center gap-2 text-xs">
        <span v-if="friend.status==='pending'" class="rounded-full bg-amber-100 px-3 py-1 font-semibold text-amber-700">Pending</span>
        <span v-if="friend.status==='active'" class="rounded-full bg-emerald-100 px-3 py-1 font-semibold text-emerald-700">Active</span>
        <span class="rounded-full bg-sky-100 px-3 py-1 font-semibold text-sky-700">
          {{ friend.relationship || 'Buddy' }}
        </span>
      </div>

   
      <div class="mt-5 w-full rounded-2xl bg-sky-50/60 p-3 ring-1 ring-sky-100">
      
        <div class="mb-2">
          <div class="flex items-center justify-between text-[11px] font-semibold text-sky-900/80">
            <span>😊 Mood</span>
            <span>{{ stat(friend.emotions?.mood) }}%</span>
          </div>
          <div class="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-sky-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-yellow-300 to-orange-400 transition-[width] duration-500"
              :style="{ width: stat(friend.emotions?.mood) + '%' }"
            />
          </div>
        </div>

      
        <div class="mb-2">
          <div class="flex items-center justify-between text-[11px] font-semibold text-sky-900/80">
            <span>⚡ Energy</span>
            <span>{{ stat(friend.emotions?.energy) }}%</span>
          </div>
          <div class="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-sky-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-emerald-300 to-emerald-500 transition-[width] duration-500"
              :style="{ width: stat(friend.emotions?.energy) + '%' }"
            />
          </div>
        </div>


        <div>
          <div class="flex items-center justify-between text-[11px] font-semibold text-sky-900/80">
            <span>😴 Sleep</span>
            <span>{{ stat(friend.emotions?.sleep) }}%</span>
          </div>
          <div class="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-sky-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-sky-300 to-indigo-400 transition-[width] duration-500"
              :style="{ width: stat(friend.emotions?.sleep) + '%' }"
            />
          </div>
        </div>
      </div>

  
      <div class="mt-5 grid w-full grid-cols-2 gap-3">
        <button
          v-if="friend.status==='active'"
          class="col-span-2 rounded-full bg-rose-100 text-rose-700 text-sm font-semibold py-2 hover:bg-rose-200"
          @click="$emit('remove', friend.id)"
        >
          Remove
        </button>

        <template v-else>
          <!-- <button
            class="rounded-full bg-emerald-100 text-emerald-700 text-sm font-semibold py-2 hover:bg-emerald-200"
            @click="$emit('approve', friend.id)"
          >
            Approve
          </button> -->
            <!-- <button
              class="rounded-full bg-indigo-100 text-indigo-700 text-sm font-semibold py-2 hover:bg-indigo-200"
              @click="$emit('resend', friend.id)"
            >
              Resend
            </button> -->
          <button
            class="col-span-2 rounded-full bg-rose-100 text-rose-700 text-sm font-semibold py-2 hover:bg-rose-200"
            @click="$emit('revoke', friend.id)"
          >
            Revoke
          </button>
        </template>

        <!-- <button
          class="relative z-10 col-span-2 rounded-full bg-[linear-gradient(180deg,#5DD6FF_0%,#2EB8FF_100%)] text-white text-sm font-semibold py-2 shadow hover:shadow-md"
          @click="$emit('update', { id: friend.id, patch: { opened: true } })"
        >
          Open
        </button> -->
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ friend: { type: Object, required: true } })
defineEmits(['update','remove','approve','resend','revoke'])

function stat(v) {
  const n = Number(v ?? 0)
  return Math.max(0, Math.min(100, isNaN(n) ? 0 : n))
}
</script>
