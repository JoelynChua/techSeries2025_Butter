<template>
  <main class="home relative overflow-x-hidden">
    <!-- Background image -->
    <div class="absolute inset-0 bg-cover bg-center home-bg"></div>

    <!-- Foreground content -->
    <div class="relative z-10 onboard-card">
      <div class="avatar-wrapper">
        <!-- Mascot (clickable) -->
        <div class="avatar-container" @click="randomiseFeeling">
          <img :src="mascotPath" :alt="currentFeeling" class="avatar" />
          <!-- Speech bubble -->
          <div class="speech-bubble">
            {{ bubbleText }}
          </div>
        </div>
      </div>

      <p class="intro">
        Hi there! I’m Jewey, your bestie and most understanding animal friend.
        You seem to be totally ready to bring more health and thoughtfulness to your life, so
        let’s get it started!
      </p>


    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

const currentFeeling = ref('Blank')
const bubbleText = ref('...')

onMounted(() => {
  fetchEncouragement('Blank')
})

const mascotPath = computed(() => {
  try {
    return new URL(`../assets/mascot/${currentFeeling.value}.png`, import.meta.url).href
  } catch (e) {
    return new URL(`../assets/mascot/Blank.png`, import.meta.url).href
  }
})

async function fetchEncouragement(feeling) {
  try {
    const resp = await axios.get(`${baseURL}/mascotWords`, { params: { feeling } })
    const data = resp?.data ?? {}
    if (Array.isArray(data.encourageWords) && data.encourageWords.length > 0) {
      bubbleText.value = data.encourageWords[0]
    } else {
      bubbleText.value = "👋 Hi, I’m Veggie!"
    }
    currentFeeling.value = feeling
  } catch (err) {
    console.error('Failed to fetch encouragement:', err)
    bubbleText.value = "👋 Hi, I’m Veggie!"
    currentFeeling.value = 'Blank'
  }
}

async function randomiseFeeling() {
  try {
    const resp = await axios.get(`${baseURL}/encouragementAll`)
    const rows = resp?.data?.rows || []
    if (!rows.length) return

    const randomRow = rows[Math.floor(Math.random() * rows.length)]
    const feeling = randomRow.feeling || 'Blank'
    const words = randomRow.encourageWords || 'Stay positive!'

    if (feeling === 'Blank') {
      await fetchEncouragement('Blank')
    } else {
      currentFeeling.value = feeling
      bubbleText.value = words
    }
  } catch (err) {
    console.error('Failed to fetch encouragements:', err)
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: grid;
  justify-items: center;  /* keep it centered horizontally */
  align-items: start;     /* push to top instead of center */
  padding: 90px 24px;     /* less top padding */
  box-sizing: border-box;
}

/* New background image */
.home-bg {
  background-image: url("../assets/homePageBG.png");
}

.onboard-card {
  width: 100%;
  max-width: 360px;
  text-align: center;
  color: #ffffff;
}

.avatar-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.avatar {
  width: 220px;
  height: auto;
  display: block;
}

/* Bounce continuously on hover */
.avatar-container:hover .avatar {
  animation: bounce 0.8s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  30% { transform: translateY(-15px); }
  60% { transform: translateY(-8px); }
}

.speech-bubble {
  position: absolute;
  top: -5px;
  left: -30px;
  max-width: 160px;
  background: #fff;
  color: #333;
  padding: 8px 12px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.speech-bubble::after {
  content: "";
  position: absolute;
  right: -6px;
  top: 12px;
  border-width: 6px;
  border-style: solid;
  border-color: transparent transparent transparent #fff;
}

.intro {
  font-size: 14px;
  line-height: 1.6;
  margin: 14px auto 22px;
  max-width: 290px;
  color: rgba(255, 255, 255, 0.95);
}

@media (min-width: 420px) {
  .avatar {
    width: 260px;
  }
  .intro {
    font-size: 15px;
    max-width: 320px;
  }
}
</style>
