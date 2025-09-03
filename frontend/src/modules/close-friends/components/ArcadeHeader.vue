<template>
  <header class="sticky top-0 z-30 relative isolate">
   
    <div
      class="arcade-bg relative grid grid-cols-[auto_1fr_auto] items-center gap-2
             rounded-b-[18px] bg-sky-500 px-3 py-2 md:px-5 md:py-3
             shadow-[0_10px_26px_-12px_rgba(2,132,199,0.7)] ring-2 ring-white
             pt-[env(safe-area-inset-top)]"
    >
      <!-- <div class="flex items-center gap-2">
        <div
          class="grid h-11 w-11 place-items-center rounded-full border-4 border-white
                 bg-gradient-to-b from-sky-200 to-sky-400 text-sky-900 font-extrabold
                 shadow-[inset_0_4px_10px_rgba(255,255,255,0.6),0_6px_12px_-4px_rgba(0,0,0,0.25)]"
          aria-label="Level"
        >
          {{ level }}
        </div>
      </div> -->

     
      <h1
        class="justify-self-center text-center leading-tight font-extrabold text-white tracking-wide text-stroke
               text-[clamp(18px,6vw,32px)] max-w-[70vw] md:max-w-none"
      >
        {{ title }}
      </h1>

   
      <div class="flex items-center gap-2 md:gap-3">
  
        <!-- <button
          class="flex items-center gap-2 rounded-full bg-white/95 px-3 py-1.5
                 ring-2 ring-white shadow-[0_6px_14px_-6px_rgba(2,132,199,0.6)]
                 hover:scale-105 transition cursor-pointer focus:outline-none focus-visible:ring-4 focus-visible:ring-white/70"
          @click="$emit('gem')"
          title="Gems"
        >
          <span
            class="grid h-6 w-6 place-items-center rounded-full bg-fuchsia-400 text-white font-bold
                   ring-2 ring-white shadow"
            aria-hidden="true"
          >◆</span>
          <span class="min-w-[2ch] text-sky-900 font-extrabold">{{ gems }}</span>
        </button> -->

      
        <!-- <button
          class="flex items-center gap-2 rounded-full bg-white/95 px-3 py-1.5
                 ring-2 ring-white shadow-[0_6px_14px_-6px_rgba(2,132,199,0.6)]
                 hover:scale-105 transition cursor-pointer focus:outline-none focus-visible:ring-4 focus-visible:ring-white/70"
          @click="$emit('coin')"
          title="Coins"
        >
          <span
            class="grid h-6 w-6 place-items-center rounded-full bg-amber-400 text-white font-extrabold
                   ring-2 ring-white shadow"
            aria-hidden="true"
          >⭕</span>
          <span class="min-w-[2ch] text-sky-900 font-extrabold">{{ coins.toLocaleString() }}</span>
        </button> -->

<!--    
        <button
          class="grid h-9 w-9 place-items-center rounded-full bg-emerald-400 text-white text-xl font-extrabold
                 ring-2 ring-white shadow hover:scale-105 transition focus:outline-none focus-visible:ring-4 focus-visible:ring-white/70"
          @click="$emit('add')"
          title="Add Friend"
          aria-label="Add Friend"
        >+</button> -->
      </div>
    </div>


    <svg
      v-if="edge !== 'none'"
      class="pointer-events-none absolute -bottom-2 left-0 w-full"
      height="14" viewBox="0 0 120 14" preserveAspectRatio="none"
      aria-hidden="true"
    >
    
      <path v-if="edge === 'wave'"
            d="M0,14 C10,4 20,4 30,14 S50,24 60,14 80,4 90,14 110,24 120,14"
            fill="white" />
     
      <path v-else
            d="M0,14 Q6,0 12,14 T36,14 T60,14 T84,14 T108,14 T132,14"
            fill="white" />
    </svg>
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Close Friends' },
  level: { type: [Number, String], default: 1 },
  gems:  { type: [Number, String], default: 0 },
  coins: { type: Number, default: 0 },
  edge:   { type: String, default: 'wave' },
})
defineEmits(['add', 'gem', 'coin'])
</script>

<style scoped>

.text-stroke {
  text-shadow:
    0 2px 0 rgba(0,0,0,0.25),
    0 0 2px rgba(0,0,0,0.15),
    0 0 6px rgba(0,0,0,0.08);
}

.arcade-bg::before{
  content:"";
  position:absolute; inset:0;
  background-image:
    radial-gradient(rgba(255,255,255,.35) 18%, transparent 19%),
    radial-gradient(rgba(255,255,255,.25) 18%, transparent 19%);
  background-size:22px 22px,22px 22px;
  background-position:0 0,11px 11px;
  opacity:.35; pointer-events:none;
}
</style>
