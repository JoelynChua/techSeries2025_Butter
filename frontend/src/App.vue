<template>
  <div class="phone-frame">
    <main class="phone-screen">
      <div class="phone-content">
        <router-view />
      </div>
      <BottomNavBar class="bottom-nav" />
    </main>
  </div>
</template>

<script setup>
import BottomNavBar from "./components/navbar.vue";
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
}

/* Scrollable area above the nav */
.phone-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 60px; /* give space above navbar */
}

/* Bottom nav fixed inside phone */
.bottom-nav {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
}
</style>
