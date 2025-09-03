<template>
  <main class="home">
    <div class="onboard-card">
      <div class="avatar-wrapper">
        <div class="avatar-ring">
          <img :src="mascot" alt="Eco Reality mascot" class="avatar" />
        </div>
        <!-- Speech bubble -->
        <div class="speech-bubble">
          👋 Hi, I’m Veggie!
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
import mascot from "../assets/mascot/Blank.png";
</script>

<style scoped>
/* Page background */
.home {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(120% 120% at 50% 0%,
              #b8d7ff 0%, #a8c5ff 20%, #b7b2ff 45%, #caa8ff 70%, #c3a0ff 100%);
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

/* Wrap avatar + speech bubble side by side */
.avatar-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

/* Circular mascot container */
.avatar-ring {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: #ffffff;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
}

.avatar {
  width: 75%;
  height: auto;
  display: block;
}

/* Speech bubble style */
.speech-bubble {
  max-width: 140px;
  background: #fff;
  color: #333;
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.4;
  position: relative;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* Tail of bubble */
.speech-bubble::after {
  content: "";
  position: absolute;
  left: -8px;
  top: 20px;
  border-width: 8px;
  border-style: solid;
  border-color: transparent #fff transparent transparent;
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
  .avatar-ring {
    width: 200px;
    height: 200px;
  }
  .intro {
    font-size: 15px;
    max-width: 320px;
  }
}
</style>
