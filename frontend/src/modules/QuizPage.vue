<template>
  <div class="quiz-background flex py-10 justify-center p-4">
    <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>

    <div class="pointer-events-none absolute inset-0 opacity-20" style="
        background-image: radial-gradient(white 18%, transparent 19%),
          radial-gradient(white 18%, transparent 19%);
        background-position: 0 0, 16px 16px;
        background-size: 32px 32px;
      "></div>

    <div
      class="relative h-[550px] w-full max-w-xl overflow-hidden rounded-[28px] p-6 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100 text-xl">
      <h2 class="text-2xl font-bold text-slate-800 mb-2 text-center">
        Daily Quiz
      </h2>

      <div class="h-[250px] flex flex-col justify-between">
        <div v-if="isLoading" class="flex items-center justify-center h-full pt-16">
          <p class="text-xl text-slate-600">Loading Quiz...</p>
        </div>

        <div v-if="!isLoading && currentQuestion && !showResults" class="flex-1 flex flex-col justify-center">
          <p class="block font-semibold text-slate-700 mb-14 text-xl">
            {{ currentQuestionIndex + 1 }}. {{ currentQuestion.prompt }}
          </p>

          <!-- Range (number/scale) -->
          <div v-if="currentQuestion.type === 'range'">
            <div class="slider-wrapper relative mb-6">
              <div class="slider-value-tooltip" :style="{
                left: sliderTooltip(
                  answers[currentQuestion.field_name],
                  currentQuestion.config.min,
                  currentQuestion.config.max,
                  $refs.slider
                ),
                transform: answers[currentQuestion.field_name] === currentQuestion.config.min
                  ? 'translateX(0)'
                  : answers[currentQuestion.field_name] === currentQuestion.config.max
                    ? 'translateX(-100%)'
                    : 'translateX(-50%)'

              }">
                {{ answers[currentQuestion.field_name] }} <span v-if="currentQuestion.unit">{{ currentQuestion.unit
                }}</span>
              </div>
              <input ref="slider" type="range" :min="currentQuestion.config.min" :max="currentQuestion.config.max"
                :step="currentQuestion.config.step" v-model.number="answers[currentQuestion.field_name]"
                class="w-full h-6 rounded-lg accent-sky-500" />
            </div>
            <div class="flex justify-between text-lg text-slate-500 mt-2">
              <span>{{ currentQuestion.config.min }}</span>
              <span>{{ currentQuestion.config.max }}</span>
            </div>
            <p class="text-xl font-bold mt-4 text-center">
              {{ answers[currentQuestion.field_name] }} <span v-if="currentQuestion.unit">{{ currentQuestion.unit
              }}</span>
            </p>
          </div>

          <!-- Options (boolean) -->
          <div v-if="currentQuestion.type === 'options'" class="flex flex-col gap-2">
            <button v-for="option in currentQuestion.options" :key="option.value ?? option"
              :class="['option-btn', { selected: answers[currentQuestion.field_name] === (option.value ?? option) }]"
              @click="answers[currentQuestion.field_name] = (option.value ?? option)">
              {{ option.label ?? option }}
            </button>
          </div>

          <!-- Text -->
          <div v-if="currentQuestion.type === 'text'">
            <textarea class="w-full rounded-xl border border-slate-200 p-3 text-lg" rows="4"
              v-model="answers[currentQuestion.field_name]"
              :placeholder="currentQuestion.placeholder || 'Type here...'"></textarea>
          </div>
        </div>

        <!-- Results -->
        <div v-if="showResults" class="text-center">
          <h3 class="text-2xl font-bold text-slate-800 mb-2">Today's Score</h3>
<p class="text-3xl font-extrabold text-slate-900">{{ Number(finalScore).toFixed(1) }}</p>
<p v-if="scoreBand?.label" class="text-3xl font-extrabold text-slate-900">
  {{ scoreBand.label }}
</p>
          <p class="mt-1 text-slate-600 text-lg">out of 10</p>

          <!-- Band details -->
<div v-if="scoreBand" class="mt-6 text-left mx-auto max-w-md rounded-xl p-4 border text-sm">
  <div class="flex items-center justify-between mb-1">
    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-white">
      {{ scoreBand.label }}
    </span>
    <span class="text-xs">
      {{ Number(scoreBand.min_score).toFixed(1) }}–{{ Number(scoreBand.max_score).toFixed(1) }}
    </span>
  </div>

  <p class="text-slate-800 mb-2">
    {{ scoreBand.message }}
  </p>

  <ul class="list-disc pl-5 space-y-1 text-slate-700 text-xs">
    <li v-for="tip in bandTips" :key="tip">{{ tip }}</li>
  </ul>

  <p v-if="scoreBand.crisis_note" class="mt-3 text-xs font-medium">
    {{ scoreBand.crisis_note }}
  </p>
</div>


        </div>


      </div>

      <div class="flex justify-end gap-4 mt-10">
        <button v-if="currentQuestionIndex > 0 && !showResults" @click="prevQuestion"
          class="px-6 py-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-sm text-lg">
          Back
        </button>
        <button v-if="!showResults && !isLoading" @click="nextQuestion" :disabled="!isAnswered"
          class="px-6 py-3 rounded-xl text-white font-semibold shadow-md transition hover:shadow-lg active:translate-y-[1px] bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)] text-lg disabled:opacity-50 disabled:cursor-not-allowed">
          {{ isLastQuestion ? "Finish" : "Next" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:5000";

export default {
  name: "QuizCard",
  data() {
    return {
      isLoading: true,
      quiz: [],
      currentQuestionIndex: 0,
      showResults: false,
      answers: {},
      finalScore: null,
      scoreBand: null,
    };
  },
  computed: {
    currentQuestion() {
      return this.quiz[this.currentQuestionIndex];
    },
    isLastQuestion() {
      return this.currentQuestionIndex === this.quiz.length - 1;
    },
    isAnswered() {
      if (!this.currentQuestion) return false;
      const q = this.currentQuestion;
      const ans = this.answers[q.field_name];

      if (q.type === "range") {
        return typeof ans === "number" && !Number.isNaN(ans);
      }
      if (q.type === "options") {
        return ans !== null && ans !== undefined && ans !== "";
      }
      if (q.type === "text") {
        return q.required ? !!(ans && ans.toString().trim().length) : true;
      }
      return false;
    },
    bandTips() {
      const t = this.scoreBand?.tips;
      return Array.isArray(t) ? t.slice(0, 5) : [];
    },
  },
  methods: {
    async fetchQuizConfig() {
      this.isLoading = true;
      try {
        const res = await axios.get(`${baseURL}/quizqn?section=daily`);
        if (!res.data || !res.data.rows) {
          throw new Error("Quiz questions could not be loaded from the API.");
        }
        const rows = res.data.rows;

        const mapped = rows
          .map((r) => {
            const inputType = (r.input_type || "").toLowerCase();
            const type =
              inputType === "number" || inputType === "scale"
                ? "range"
                : inputType === "boolean"
                  ? "options"
                  : inputType === "text"
                    ? "text"
                    : null;

            if (!type) return null;

            const q = {
              key: r.key,
              field_name: r.key,
              prompt: r.prompt,
              unit: r.unit || "",
              required: !!r.required,
              type,
              config: undefined,
              options: undefined,
            };

            if (type === "range") {
              const min = Number(r.min_value ?? 0);
              const max = Number(r.max_value ?? 10);
              const step = Number(r.step ?? 1);
              q.config = { min, max, step };
            } else if (type === "options" && inputType === "boolean") {
              q.options = [
                { label: "Yes", value: true },
                { label: "No", value: false },
              ];
            }

            return q;
          })
          .filter(Boolean);

        this.quiz = mapped;

        // Initialize answers
        this.quiz.forEach((q) => {
          if (q.type === "range") this.answers[q.field_name] = q.config.min;
          else if (q.type === "options") this.answers[q.field_name] = null;
          else if (q.type === "text") this.answers[q.field_name] = "";
        });
      } catch (error) {
        console.error("Failed to load quiz configuration:", error);
      } finally {
        this.isLoading = false;
      }
    },

    nextQuestion() {
      if (this.isLastQuestion) {
        this.submitQuiz();
      } else {
        this.currentQuestionIndex++;
      }
    },
    prevQuestion() {
      if (this.currentQuestionIndex > 0) this.currentQuestionIndex--;
    },

    // Map question keys -> /moodMetric payload fields
    buildSubmissionPayload() {
      // backend accepts these keys:
      // userId, sleepHours, exerciseHours, workingHrs, sleepQuality, mood,
      // energy, stress, timeOutsideMin, connectwithfamily, notes, created_timestamp, finalMoodScores
      const keyToPayload = {
        sleep_hours: "sleepHours",
        work_hours: "workingHrs",
        sleep_quality: "sleepQuality",      // 1–10
        mood: "mood",                       // 1–10
        energy: "energy",                   // 1–10
        stress: "stress",                   // 1–10 (higher = more stressed)
        time_outside_min: "timeOutsideMin", // minutes (int)
        connect_with_family: "connectwithfamily",
        notes: "notes",
        // special case: exercise_min (minutes) -> exerciseHours (hours)
        exercise_min: "exerciseHours",
      };

      const payload = {
        userId: 1, // TODO: replace with real user id
        created_timestamp: new Date().toISOString().slice(0, 19).replace("T", " "),
      };

      Object.entries(keyToPayload).forEach(([key, outField]) => {
        if (Object.prototype.hasOwnProperty.call(this.answers, key)) {
          let val = this.answers[key];

          if (key === "exercise_min") {
            // convert minutes -> hours with 2dp
            const hours = Number(val) / 60;
            val = Number.isFinite(hours) ? Number(hours.toFixed(2)) : 0;
          }

          if (key === "time_outside_min") {
            // ensure integer minutes
            val = Number.isFinite(Number(val)) ? Math.round(Number(val)) : 0;
          }

          payload[outField] = val;
        }
      });

      return payload;
    },

    async submitQuiz() {
      try {
        const payload = this.buildSubmissionPayload();
        const resp = await axios.post(`${baseURL}/moodMetric`, payload);
        this.finalScore = resp?.data?.finalScore ?? resp?.data?.row?.finalMoodScores ?? null;
        this.scoreBand = resp?.data?.scoreBand ?? null;   
        this.showResults = true;
        console.log("Quiz submitted successfully:", resp.data);
      } catch (error) {
        console.error("Failed to submit quiz:", error);
        alert("There was an error submitting your quiz. Please try again.");
      }
    },


    sliderTooltip(value, min, max, sliderRef) {
      if (!sliderRef || value === undefined) return "0px";
      const percent = (Number(value) - Number(min)) / (Number(max) - Number(min));
      const thumbWidth = 38;
      const sliderWidth = sliderRef.offsetWidth || 0;
      const left = percent * (sliderWidth - thumbWidth) + thumbWidth / 2;
      return `${left}px`;
    },
  },

  async mounted() {
    await this.fetchQuizConfig();
  },
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

.quiz-background {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  box-sizing: border-box;
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
  padding: 12px 48px;
  border: 1px solid #cce6ff;
  border-radius: 16px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1.1rem;
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
