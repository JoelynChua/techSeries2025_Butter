<template>
  <!-- <CloseFriendsPage /> -->
  <div>
    <router-view />
    <BottomNavBar />
  </div>
</template>

<script setup>
// no need to import individual pages here
import BottomNavBar from "./components/navbar.vue";
</script>
