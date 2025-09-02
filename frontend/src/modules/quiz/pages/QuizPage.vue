<template>
  <div class="fixed inset-0 bg-sky-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div
      class="relative w-full max-w-2xl overflow-hidden rounded-[28px] p-10 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100 text-xl"
    >
      <h2 class="text-3xl font-bold text-slate-800 mb-10 text-center">
        Daily Quiz
      </h2>

      <div class="space-y-12">

        <!-- Question 1 -->
        <div v-if="currentQuestion === 1">
          <p class="block font-semibold text-slate-700 mb-4 text-2xl">1. How many hours did you sleep last night?</p>
          <p v-if="trackerConnected" class="text-lg text-slate-500 mb-4">
            📲 Value imported from health tracker: <strong>{{ sleepHours }} hours</strong>
          </p>
          <div v-else>
            <p class="text-lg text-slate-500 mb-14">No tracker connected. Please input manually.</p>

            <div class="slider-wrapper relative mb-4">
              <div
                class="slider-value-tooltip"
                :style="{ left: sliderTooltip(sleepHours, 0, 12, $refs.sleepSlider) }"
              >
                {{ sleepHours }}
              </div>

              <input
                ref="sleepSlider"
                type="range"
                min="0"
                max="12"
                step="0.5"
                v-model="sleepHours"
                class="w-full h-6 rounded-lg accent-sky-500"
              />
            </div>

            <div class="flex justify-between text-lg text-slate-500 mt-2">
              <span>0</span>
              <span>3</span>
              <span>6</span>
              <span>9</span>
              <span>12</span>
            </div>

            <p class="text-3xl font-bold mt-6 text-center">{{ sleepHours }} hours</p>
          </div>
        </div>

        <!-- Question 2 -->
        <div v-if="currentQuestion === 2">
          <p class="block font-semibold text-slate-700 mb-4 text-2xl">2. How long did you exercise/walk around today?</p>
          <p v-if="trackerConnected" class="text-lg text-slate-500 mb-4">
            📲 Value imported from health tracker: <strong>{{ exerciseHours }} hours</strong>
          </p>
          <div v-else>
            <p class="text-lg text-slate-500 mb-14">No tracker connected. Please input manually.</p>

            <div class="slider-wrapper relative mb-4">
              <div
                class="slider-value-tooltip"
                :style="{ left: sliderTooltip(exerciseHours, 0, 6, $refs.exerciseSlider) }"
              >
                {{ exerciseHours }}
              </div>

              <input
                ref="exerciseSlider"
                type="range"
                min="0"
                max="6"
                step="0.5"
                v-model="exerciseHours"
                class="w-full h-6 rounded-lg accent-sky-500"
              />
            </div>

            <div class="flex justify-between text-lg text-slate-500 mt-2">
              <span>0</span>
              <span>1.5</span>
              <span>3</span>
              <span>4.5</span>
              <span>6</span>
            </div>

            <p class="text-3xl font-bold mt-6 text-center">{{ exerciseHours }} hours</p>
          </div>
        </div>

        <!-- Question 3 -->
        <div v-if="currentQuestion === 3">
          <p class="block font-semibold text-slate-700 mb-6 text-2xl">3. How would you describe your overall mood today?</p>
          <div class="flex flex-col gap-4">
            <button
              v-for="(option, index) in moodOptions"
              :key="index"
              :class="['option-btn', { selected: mood === option }]"
              @click="mood = option"
            >
              {{ option }}
            </button>
          </div>
        </div>

        <!-- Question 4 -->
        <div v-if="currentQuestion === 4">
          <p class="block font-semibold text-slate-700 mb-6 text-2xl text-center">
            4. Did you connect with your family/friends today?
          </p>
          <div class="flex justify-center gap-8">
            <button
              :class="['option-btn', { selected: connected === 'Yes' }]"
              @click="connected = 'Yes'"
            >
              Yes
            </button>
            <button
              :class="['option-btn', { selected: connected === 'No' }]"
              @click="connected = 'No'"
            >
              No
            </button>
          </div>
        </div>

        <!-- Results -->
        <div v-if="currentQuestion === 5" class="text-center">
          <h3 class="text-3xl font-bold text-slate-800 mb-6">Your Mood Summary</h3>
          <p class="text-xl text-slate-700 mb-2">Sleep: {{ sleepHours }} hrs</p>
          <p class="text-xl text-slate-700 mb-2">Exercise: {{ exerciseHours }} hrs</p>
          <p class="text-xl text-slate-700 mb-2">Mood: {{ mood }}</p>
          <p class="text-xl text-slate-700">Connected with family/friends: {{ connected }}</p>
        </div>

      </div>

      <div class="flex justify-end gap-4 mt-10">
        <button v-if="currentQuestion > 1 && currentQuestion < 5" @click="prevQuestion"
          class="px-6 py-3 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-sm text-lg">
          Back
        </button>
        <button v-if="currentQuestion < 5" @click="nextQuestion"
          class="px-6 py-3 rounded-xl text-white font-semibold shadow-md transition hover:shadow-lg active:translate-y-[1px] bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)] text-lg">
          {{ currentQuestion === 4 ? 'Finish' : 'Next' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "QuizCard",
  data() {
    return {
      currentQuestion: 1,
      trackerConnected: false,
      sleepHours: 0,
      exerciseHours: 0,
      mood: "",
      connected: "",
      moodOptions: [
        "Very happy / positive",
        "Calm / content",
        "Neutral / okay",
        "Stressed / anxious",
        "Sad / down"
      ]
    };
  },
  methods: {
    nextQuestion() {
      if (this.currentQuestion < 5) this.currentQuestion++;
    },
    prevQuestion() {
      if (this.currentQuestion > 1) this.currentQuestion--;
    },
    sliderTooltip(value, min, max, sliderRef) {
      if (!sliderRef) return "0px";
      const slider = sliderRef;
      const percent = (value - min) / (max - min);
      const thumbWidth = 38; // slider thumb width + border
      const sliderWidth = slider.offsetWidth;
      const left = percent * (sliderWidth - thumbWidth) + thumbWidth / 2;
      return left + "px";
    }
  }
};
</script>

<style scoped>
.slider-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 1rem;
}
.slider-value-tooltip {
  position: absolute;
  top: -2.5rem;
  transform: translateX(-50%);
  background: #3da8ff;
  color: white;
  font-size: 0.9rem;
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 0.5rem;
}

/* Sliders */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 1.8rem;
  border-radius: 0.5rem;
  background: #cce6ff;
  outline: none;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 50%;
  background: #3da8ff;
  cursor: pointer;
  border: 3px solid #5ec4ff;
  margin-top: -0.35rem;
}

/* Option buttons */
.option-btn {
  padding: 18px 64px; /* larger width */
  border: 1px solid #cce6ff;
  border-radius: 16px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1.25rem;
  text-align: center;
}

.option-btn.selected {
  background: #3da8ff;
  color: white;
  font-weight: bold;
}

.option-btn:hover {
  background: #5ec4ff;
  color: white;
}
</style>
