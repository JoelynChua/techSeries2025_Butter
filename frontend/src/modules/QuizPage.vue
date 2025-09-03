<template>
    <div class="quiz-background fixed inset-0 flex items-center justify-center z-50 p-4">
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-to-b from-sky-200 to-sky-300"></div>

    <!-- Dotted overlay -->
    <div
      class="pointer-events-none absolute inset-0 opacity-20"
      style="
        background-image:
          radial-gradient(white 18%, transparent 19%),
          radial-gradient(white 18%, transparent 19%);
        background-position: 0 0, 16px 16px;
        background-size: 32px 32px;
      "
    ></div>

    <div
      class="relative w-full max-w-xl overflow-hidden rounded-[28px] p-6 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100 text-xl"
    >
      <h2 class="text-3xl font-bold text-slate-800 mb-6 text-center">
        Daily Quiz
      </h2>

      <div class="h-[450px] flex flex-col justify-between">
        <div
          v-if="isLoading"
          class="flex items-center justify-center h-full pt-16"
        >
          <p class="text-2xl text-slate-600">Loading Quiz...</p>
        </div>

        <div v-if="!isLoading && currentQuestion && !showResults" class="flex-1 flex flex-col justify-center">
          <p class="block font-semibold text-slate-700 mb-14 text-2xl">
            {{ currentQuestionIndex + 1 }}. {{ currentQuestion.question_text }}
          </p>

          <div v-if="currentQuestion.type === 'range'">
            <div class="slider-wrapper relative mb-6">
              <div
                class="slider-value-tooltip"
                :style="{
                  left: sliderTooltip(
                    answers[currentQuestion.field_name],
                    currentQuestion.config.min,
                    currentQuestion.config.max,
                    $refs.slider
                  ),
                }"
              >
                {{ answers[currentQuestion.field_name] }}
              </div>
              <input
                ref="slider"
                type="range"
                :min="currentQuestion.config.min"
                :max="currentQuestion.config.max"
                :step="currentQuestion.config.step"
                v-model.number="answers[currentQuestion.field_name]"
                class="w-full h-6 rounded-lg accent-sky-500"
              />
            </div>
            <div class="flex justify-between text-lg text-slate-500 mt-2">
              <span>{{ currentQuestion.config.min }}</span>
              <span>{{ currentQuestion.config.max }}</span>
            </div>
            <p class="text-2xl font-bold mt-4 text-center">
              {{ answers[currentQuestion.field_name] }} hours
            </p>
          </div>

          <div
            v-if="currentQuestion.type === 'options'"
            class="flex flex-col gap-4"
          >
            <button
              v-for="option in currentQuestion.options"
              :key="option"
              :class="[
                'option-btn',
                { selected: answers[currentQuestion.field_name] === option },
              ]"
              @click="answers[currentQuestion.field_name] = option"
            >
              {{ option }}
            </button>
          </div>
        </div>

        <div v-if="showResults" class="text-center">
          <h3 class="text-3xl font-bold text-slate-800 mb-6">
            Your Mood Summary
          </h3>
          <p
            v-if="answers.sleephours !== undefined"
            class="text-xl text-slate-700 mb-2"
          >
            Sleep Hours: {{ answers.sleephours }} hrs
          </p>
          <p v-if="answers.sleepquality" class="text-xl text-slate-700 mb-2">
            Sleep Quality: {{ answers.sleepquality }}
          </p>
          <p
            v-if="answers.exercisehours !== undefined"
            class="text-xl text-slate-700 mb-2"
          >
            Exercise: {{ answers.exercisehours }} hrs
          </p>
          <p
            v-if="answers.workhours !== undefined"
            class="text-xl text-slate-700 mb-2"
          >
            Work Hours: {{ answers.workhours }} hrs
          </p>
          <p v-if="answers.mood" class="text-xl text-slate-700 mb-2">
            Mood: {{ answers.mood }}
          </p>
          <p v-if="answers.connectwithfamily" class="text-xl text-slate-700">
            Connected with family/friends: {{ answers.connectwithfamily }}
          </p>
        </div>
      </div>

      <div class="flex justify-end gap-4 mt-10">
        <button
          v-if="currentQuestionIndex > 0 && !showResults"
          @click="prevQuestion"
          class="px-6 py-3 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-sm text-lg"
        >
          Back
        </button>
        <button
          v-if="!showResults && !isLoading"
          @click="nextQuestion"
          :disabled="!isAnswered"
          class="px-6 py-3 rounded-xl text-white font-semibold shadow-md transition hover:shadow-lg active:translate-y-[1px] bg-[linear-gradient(180deg,#5EC4FF_0%,#3DA8FF_100%)] text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
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
      const currentAnswer = this.answers[this.currentQuestion.field_name];
      return currentAnswer !== null && currentAnswer !== "";
    },
  },
  methods: {
    async fetchQuizConfig() {
      this.isLoading = true;
      try {
        const questionsRes = await axios.get(`${baseURL}/quizqn?id=1`);
        if (!questionsRes.data || !questionsRes.data.row) {
          throw new Error("Quiz questions could not be loaded from the API.");
        }
        const questionTexts = questionsRes.data.row;

        const fieldOrder = [
          "sleephours",
          "sleepquality",
          "exercisehours",
          "workhours",
          "mood",
          "connectwithfamily",
        ];

        let initialQuestions = fieldOrder.map((field) => ({
          field_name: field,
          question_text: questionTexts[field],
          type: null,
        }));

        const configPromises = initialQuestions.map((q) => {
          if (
            ["sleephours", "workhours", "exercisehours"].includes(q.field_name)
          ) {
            return axios.get(
              `${baseURL}/rangeConfig?field_name=${q.field_name}`
            );
          }
          if (
            ["sleepquality", "mood", "connectwithfamily"].includes(q.field_name)
          ) {
            return axios.get(
              `${baseURL}/labelOptions?field_name=${q.field_name}`
            );
          }
          return Promise.resolve(null);
        });

        const configResults = await Promise.all(configPromises);

        const finalQuizStructure = initialQuestions.map((q, index) => {
          const result = configResults[index];
          if (!result || !result.data.rows) return q;

          const configData = result.data.rows;

          if (q.field_name.includes("hours")) {
            q.type = "range";
            q.config = {
              min: configData[0].min_value,
              max: configData[0].max_value,
              step: configData[0].step_value,
            };
          } else {
            q.type = "options";
            q.options = configData[0].labelvalue;
          }
          return q;
        });

        this.quiz = finalQuizStructure.filter((q) => q.type);

        this.quiz.forEach((q) => {
          if (q.type === "range") {
            this.answers[q.field_name] = q.config.min;
          } else {
            this.answers[q.field_name] = "";
          }
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
    async submitQuiz() {
      const payload = {
        userId: 1, // to be replaced with actual user ID
        sleepHours: this.answers.sleephours,
        sleepQuality: this.answers.sleepquality,
        exerciseHours: this.answers.exercisehours,
        workingHrs: this.answers.workhours,
        mood: this.answers.mood,
        connectwithfamily: this.answers.connectwithfamily,
        created_timestamp: new Date().toISOString(),
      };
      try {
        await axios.post(`${baseURL}/moodMetric`, payload);
        this.showResults = true;
      } catch (error) {
        console.error("Failed to submit quiz:", error);
        alert("There was an error submitting your quiz. Please try again.");
      }
    },
    sliderTooltip(value, min, max, sliderRef) {
      if (!sliderRef || value === undefined) return "0px";
      const percent = (Number(value) - min) / (max - min);
      const thumbWidth = 38;
      const sliderWidth = sliderRef.offsetWidth;
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
  padding: 12px 48px; /* larger width */
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

/* * Slider spacing */
.slider-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 1rem;
}

.slider-value-tooltip {
  position: absolute;
  top: -2.5rem; /* slightly closer to the slider */
  transform: translateX(-50%);
  background: #3da8ff;
  color: white;
  font-size: 0.9rem;
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 0.5rem;
}
</style>
