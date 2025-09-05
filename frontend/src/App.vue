<template>
  <div class="phone-frame">
    <main class="phone-screen">
      <!-- Speaker / audio toggle -->
      <button
        class="audio-toggle"
        :aria-label="isMuted ? 'Unmute background music' : 'Mute background music'"
        @click="toggleAudio"
      >
        <!-- Unmuted (volume) icon -->
        <svg v-if="!isMuted" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 5L6 9H3v6h3l5 4V5z"/>
          <path d="M15.54 8.46a5 5 0 010 7.07"/>
          <path d="M19.07 4.93a10 10 0 010 14.14"/>
        </svg>
        <!-- Muted icon -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 5L6 9H3v6h3l5 4V5z"/>
          <path d="M23 9l-6 6"/>
          <path d="M17 9l6 6"/>
        </svg>
      </button>

      <!-- Background music -->
      <audio
        ref="audioRef"
        :muted="isMuted"
        loop
        preload="auto"
        playsinline
      >
        <source src="/audio/sunshine-after-rain.mp3" type="audio/mpeg" />
        <!-- Optional fallback (add if you also export OGG)
        <source src="/audio/sunshine-after-rain.ogg" type="audio/ogg" />
        -->
      </audio>

      <div class="phone-content">
        <router-view />
      </div>
      <BottomNavBar class="bottom-nav" />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import BottomNavBar from "./components/navbar.vue";

const isMuted = ref(true);
const audioRef = ref(null);

onMounted(() => {
  const el = audioRef.value;
  if (!el) return;

  // Sensible starting volume; adjust to taste
  el.volume = 0.5;

  // Helpful (optional) diagnostics
  el.addEventListener("canplay", () => console.log("[audio] canplay"));
  el.addEventListener("play", () => console.log("[audio] playing; muted =", el.muted));
  el.addEventListener("pause", () => console.log("[audio] paused"));
  el.addEventListener("error", () => console.log("[audio] error", el.error));

  // Kick preload in some browsers
  try { el.load(); } catch {}
});

const toggleAudio = async () => {
  const el = audioRef.value;
  if (!el) return;

  // If muted or paused → unmute & play
  if (isMuted.value || el.paused) {
    el.muted = false;
    try {
      await el.play();      // user click satisfies autoplay policies
      isMuted.value = false;
    } catch (err) {
      console.log("[audio] play() failed:", err?.name || err);
      el.muted = true;
      isMuted.value = true;
    }
    return;
  }

  // Otherwise → mute (keeps buffer so resuming is instant)
  el.muted = true;
  isMuted.value = true;
};
</script>

<style>
/* Frame wrapper */
.phone-frame {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f0f0; /* grey around the phone */
  height: 100vh;
  margin: 0;
}

/* Phone screen */
.phone-screen {
  display: flex;
  flex-direction: column;
  width: 360px;
  height: 640px;
  border: 12px solid #000;   /* black bezel */
  border-radius: 28px;       /* rounded corners */
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  background: #fff;
  position: relative;
  isolation: isolate; 
}

/* Scrollable area above the nav */
.phone-content {
  flex: 1;
  overflow-y: auto;
  /* padding-bottom: 60px; give space above navbar */
  max-height: 540px;
  /* Hide scrollbar but keep scrolling */
  scrollbar-width: none;        /* Firefox */
  -ms-overflow-style: none;     /* IE & Edge */
}
.phone-content::-webkit-scrollbar {
  display: none;                /* Chrome, Safari, Opera */
}

/* Bottom nav fixed inside phone */
.bottom-nav {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
}

/* Audio toggle button (top-right) */
.audio-toggle {
  position: absolute;
  top: 8px;
  right: 8px;
  height: 36px;
  width: 36px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  cursor: pointer;
  z-index: 9999;
  transition: transform 0.15s ease, background 0.2s ease;
}
.audio-toggle:hover { transform: scale(1.05); background: rgba(0,0,0,0.65); }
.audio-toggle:active { transform: scale(0.96); }
</style>
