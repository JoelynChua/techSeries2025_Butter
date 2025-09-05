<template>
  <nav
    class="fixed bottom-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-sm shadow-[0_-5px_20px_-5px_rgba(0,0,0,0.05)]"
  >
    <div
      class="mx-auto flex max-w-md justify-around py-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))]"
    >
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="flex flex-col items-center justify-center gap-1 w-20 transition-transform duration-200 ease-in-out hover:scale-105 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded-lg"
        :aria-label="item.label"
        v-slot="{ isActive }"
      >
        <div
          class="relative grid h-10 w-10 place-items-center rounded-full transition-all duration-300"
          :class="isActive ? 'bg-blue-100' : 'bg-transparent'"
        >
          <img
            :src="item.icon"
            class="h-6 w-6 transition-all duration-300"
            :class="{ grayscale: !isActive, 'icon-active-blue': isActive }"
            :style="{ transform: `scale(${item.scale || 1})` }"
            alt=""
          />
        </div>

        <span
          class="text-xs font-semibold transition-colors duration-300"
          :class="isActive ? 'text-blue-600' : 'text-gray-400'"
        >
          {{ item.label }}
        </span>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref } from "vue";

const getIconUrl = (name) => {
  return new URL(`../assets/navbar/${name}.png`, import.meta.url).href;
};

const navItems = ref([
  {
    name: "Home",
    label: "Home",
    path: "/homePage",
    icon: getIconUrl("home"),
    scale: 1.5,
  },
  { name: "Quiz", label: "Quiz", path: "/quiz", icon: getIconUrl("quiz") },
  {
    name: "Friends",
    label: "Friends",
    path: "/close-friends",
    icon: getIconUrl("friends"),
  },
  {
    name: "Profile",
    label: "Profile",
    path: "/profile",
    icon: getIconUrl("profile"),
  },
]);
</script>

<style scoped>
.grayscale {
  filter: grayscale(100%);
}

.icon-active-blue {
  filter: invert(38%) sepia(98%) saturate(1583%) hue-rotate(198deg)
    brightness(97%) contrast(98%);
}
</style>
