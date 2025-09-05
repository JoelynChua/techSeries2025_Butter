<template>
  <main class="home relative overflow-x-hidden">
    <!-- Background image -->
    <div class="absolute inset-0 bg-cover bg-center home-bg"></div>

    <!-- Sign Up Card -->
    <div class="relative z-10 onboard-card">
      <div class="avatar-wrapper">
        <div class="avatar-container">
          <img src="../assets/mascot/Blank.png" alt="Jewey Mascot" class="avatar" />
        </div>
      </div>

      <h2 class="signup-title">Join Us 🎉</h2>
      <p class="intro">Create an account to start your journey with Jewey!</p>

      <form @submit.prevent="handleSignUp" class="signup-form">
        <div class="form-group">
          <input
            v-model="name"
            type="text"
            placeholder="Name"
            required
            class="form-input"
          />
        </div>
        <div class="form-group">
          <input
            v-model="email"
            type="email"
            placeholder="Email"
            required
            class="form-input"
          />
          <p v-if="errors.email" class="error">{{ errors.email }}</p>
        </div>
        <div class="form-group">
          <input
            v-model="mobile"
            type="tel"
            placeholder="Mobile Number"
            required
            class="form-input"
          />
          <p v-if="errors.mobile" class="error">{{ errors.mobile }}</p>
        </div>
        <div class="form-group">
          <input
            v-model="password"
            type="password"
            placeholder="Password"
            required
            class="form-input"
          />
          <p v-if="errors.password" class="error">{{ errors.password }}</p>
        </div>

        <button type="submit" class="signup-btn">
          Sign Up
        </button>
      </form>

      <p class="login-text">
        Already have an account?
        <a href="/login" class="login-link">Log in</a>
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const name = ref('')
const email = ref('')
const mobile = ref('')
const password = ref('')
const errors = ref({})

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000'
const router = useRouter()

function validateForm() {
  errors.value = {}

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    errors.value.email = 'Invalid email format'
  }

  // Mobile (must be exactly 8 digits)
  const mobileRegex = /^\d{8}$/
  if (!mobileRegex.test(mobile.value)) {
    errors.value.mobile = 'Mobile number must be 8 digits'
  }

  // Password (at least 8 characters)
  if (password.value.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
  }

  return Object.keys(errors.value).length === 0
}

async function handleSignUp() {
  if (!validateForm()) return // stop if validation fails

  try {
    const signupResp = await axios.post(`${baseURL}/signup`, {
      name: name.value,
      email: email.value,
      mobile: mobile.value,
      password: password.value,
    })
    console.log(signupResp.data)
    if (signupResp.data?.user) {
      alert("🎉 Sign-up successful! Please log in.")
      router.push('/login')
    } else {
      alert("❌ Sign-up failed. Please try again.")
    }
  } catch (err) {
    console.error("Sign-up failed:", err)
    if (err.response?.status === 409) {
      alert("⚠️ This email is already registered. Please log in instead.")
      router.push('/login')
    } else {
      alert("⚠️ Something went wrong. Please try again.")
    }
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

.signup-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.intro {
  font-size: 14px;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.signup-form {
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

.error {
  font-size: 12px;
  color: #ffbaba;
  margin-top: 4px;
  text-align: left;
}

.signup-btn {
  background: #ffffff;
  color: #333;
  font-weight: 600;
  border: none;
  border-radius: 14px;
  padding: 12px;
  cursor: pointer;
  transition: 0.2s;
}

.signup-btn:hover {
  background: #f0f0f0;
}

.login-text {
  margin-top: 16px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.login-link {
  color: #fff;
  font-weight: bold;
  text-decoration: underline;
}
</style>
