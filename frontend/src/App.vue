<template>
  <div class="phone-frame">
    <main class="phone-screen">
      <router-view />
    </main>
  <div>
    <router-view />
    <BottomNavBar />
  </div>
</template>

<script setup>
// no need to import individual pages here
import BottomNavBar from "./components/navbar.vue";
</script>

<style>
/* Frame wrapper */
.phone-frame {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f0f0;  /* grey around the phone */
  height: 100vh;
  margin: 0;
}

/* Phone screen itself */
.phone-screen {
  width: 360px;              /* fixed mobile width */
  height: 640px;             /* fixed mobile height */
  border: 12px solid #000;   /* black bezel */
  border-radius: 28px;       /* rounded corners */
  box-shadow: 0 12px 30px rgba(0,0,0,0.25);
  overflow: hidden;          /* clip inner scrolling */
  background: #fff;          /* phone background */
  position: relative;
}
</style>
