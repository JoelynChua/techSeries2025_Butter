<template>
  <main class="home relative overflow-x-hidden">
    <!-- Background image -->
    <div class="absolute inset-0 bg-cover bg-center home-bg"></div>

    <!-- Login Card -->
    <div class="relative z-10 onboard-card">
      <div class="avatar-wrapper">
        <div class="avatar-container">
          <img src="../assets/mascot/Blank.png" alt="Jewey Mascot" class="avatar" />
        </div>
      </div>

      <h2 class="login-title">Welcome Back 👋</h2>
      <p class="intro">Log in to continue your journey with Jewey!</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <input v-model="email" type="email" placeholder="Email" required class="form-input" />
        </div>
        <div class="form-group">
          <input v-model="password" type="password" placeholder="Password" required class="form-input" />
        </div>

        <button type="submit" class="login-btn">
          Login
        </button>
      </form>

      <p class="signup-text">
        Don’t have an account?
        <a href="/signup" class="signup-link">Sign up</a>
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const email = ref('')
const password = ref('')
const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000'
const router = useRouter()

async function handleLogin() {
  try {
    const resp = await axios.post(`${baseURL}/login`, {
      email: email.value,
      password: password.value
    })
    // console.log(resp.data)
    // Check if the response contains a "user" object
    if (resp.data?.user) {
      // Store userId in session storage
      sessionStorage.setItem('userId', resp.data.user.userId)
      alert(`🎉 Login successful! Welcome, ${resp.data.user.email || 'User'}!`)
      // Redirect to the dashboard or home page
      router.push('/homePage') // Use router to navigate
    } else if (resp.data?.error) {
      alert("❌ Invalid email or password")
    }
  } catch (err) {
    // console.error("Login failed:", err)
    alert("❌ Invalid email or password")
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: grid;
  justify-items: center;
  align-items: start;
  padding: 90px 24px;
  box-sizing: border-box;
}

.home-bg {
  background-image: url("../assets/homePageBG.png");
}

.onboard-card {
  width: 100%;
  max-width: 360px;
  text-align: center;
  color: #ffffff;
  background: rgba(0, 0, 0, 0.35);
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.avatar-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.avatar {
  width: 120px;
  height: auto;
}

.login-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.intro {
  font-size: 14px;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  outline: none;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.login-btn {
  background: #ffffff;
  color: #333;
  font-weight: 600;
  border: none;
  border-radius: 14px;
  padding: 12px;
  cursor: pointer;
  transition: 0.2s;
}

.login-btn:hover {
  background: #f0f0f0;
}

.signup-text {
  margin-top: 16px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.signup-link {
  color: #fff;
  font-weight: bold;
  text-decoration: underline;
}
</style>