<template>
  <main class="home">
    <div class="onboard-card">
      <div class="avatar-wrapper">
        <!-- Mascot -->
        <div class="avatar-container">
          <img :src="mascot" alt="Eco Reality mascot" class="avatar" />
          <!-- Speech bubble -->
          <div class="speech-bubble">
            {{ bubbleText }}
          </div>
        </div>
      </div>

      <p class="intro">
        Hi there! I’m Veggie, and I’m going to guide you through your first steps in Eco Reality.
        You seem to be totally ready to bring more health and thoughtfulness to your life, so
        let’s get it started!
      </p>

      <div class="dots" aria-label="Onboarding progress">
        <span class="dot active" aria-current="step"></span>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import mascot from "../assets/mascot/Blank.png"

// ---- API baseURL (configurable via Vite env or fallback) ----
const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

// Extract a title-cased image name from the file path
const imageName = computed(() => {
  const path = String(mascot || '')
  const filename = (path.split('/').pop() || '').split('?')[0]
  const base = (filename.split('.').shift() || '')
    .replace(/[-_]+/g, ' ')
    .trim()
    .toLowerCase()

  if (!base) return ''
  return base.charAt(0).toUpperCase() + base.slice(1)
})

const bubbleText = ref("👋 Hi, I’m Veggie!") // fallback text

async function fetchMascotWords() {
  try {
    const resp = await axios.get(`${baseURL}/mascotWords`, {
      params: { feeling: imageName.value }
    })
    const data = resp?.data ?? {}
    // Flask returns {feeling, encourageWords: [...]}
    if (Array.isArray(data.encourageWords) && data.encourageWords.length > 0) {
      bubbleText.value = data.encourageWords[0]
    }
  } catch (err) {
    console.error("Failed to fetch mascot words:", err)
  }
}

onMounted(fetchMascotWords)
</script>

<style scoped>
/* Page background */
.home {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(
    120% 120% at 50% 0%,
    #b8d7ff 0%,
    #a8c5ff 20%,
    #b7b2ff 45%,
    #caa8ff 70%,
    #c3a0ff 100%
  );
  padding: 24px;
  box-sizing: border-box;
}

/* Card container */
.onboard-card {
  width: 100%;
  max-width: 360px;
  text-align: center;
  color: #ffffff;
}

/* Wrap mascot + bubble */
.avatar-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

/* Image without circle */
.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 160px;
  height: auto;
  display: block;
}

/* Speech bubble top-left */
.speech-bubble {
  position: absolute;
  top: -20px;
  left: -60px;
  max-width: 140px;
  background: #fff;
  color: #333;
  padding: 8px 12px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Tail pointing right */
.speech-bubble::after {
  content: "";
  position: absolute;
  right: -8px;
  top: 20px;
  border-width: 8px;
  border-style: solid;
  border-color: transparent transparent transparent #fff;
}

/* Intro text */
.intro {
  font-size: 14px;
  line-height: 1.6;
  margin: 14px auto 22px;
  max-width: 290px;
  color: rgba(255, 255, 255, 0.95);
}

/* Pager dots */
.dots {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
}

.dot.active {
  background: #ffffff;
  transform: scale(1.05);
}

/* Larger screens */
@media (min-width: 420px) {
  .avatar {
    width: 180px;
  }
  .intro {
    font-size: 15px;
    max-width: 320px;
  }
}
</style>
