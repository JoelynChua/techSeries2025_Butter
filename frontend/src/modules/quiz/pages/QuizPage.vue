<template>
  <div
    class="fixed inset-0 bg-sky-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
  >
    <div
      class="relative w-full max-w-2xl overflow-hidden rounded-[28px] p-10 ring-1 ring-sky-100 shadow-[0_18px_48px_-22px_rgba(24,39,75,0.35)] bg-gradient-to-b from-sky-50 to-sky-100 text-xl"
    >
      <h2 class="text-3xl font-bold text-slate-800 mb-10 text-center">
        Daily Quiz
      </h2>

      <div class="space-y-12 min-h-[350px]">
        <div v-if="isLoading" class="text-center pt-16">
          <p class="text-2xl text-slate-600">Loading Quiz...</p>
        </div>

        <div v-if="!isLoading && currentQuestion && !showResults">
          <p class="block font-semibold text-slate-700 mb-6 text-2xl">
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
            <p class="text-3xl font-bold mt-6 text-center">
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

        <div v-if="showResults" class="text-center pt-16">
          <h3 class="text-3xl font-bold text-slate-800 mb-6">
            Quiz Submitted! ✅
          </h3>
          <p class="text-xl text-slate-600">
            Thank you for completing your daily check-in.
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
      // Check that the answer is not null or an empty string
      return currentAnswer !== null && currentAnswer !== "";
    },
  },
  async mounted() {
    await this.fetchQuizConfig();
  },
  methods: {
    methods: {
      async fetchQuizConfig() {
        this.isLoading = true;
        try {
          const [questionsRes, rangesRes, labelsRes] = await Promise.all([
            axios.get("/api/questions"),
            axios.get("/api/range_config"),
            axios.get("/api/label_options"), // Fetches from your new label_options table
          ]);

          const questionsData = (questionsRes.data.rows ||
            questionsRes.data)[0];
          const rangesData = rangesRes.data.rows || rangesRes.data;
          const labelsData = labelsRes.data.rows || labelsRes.data;

          if (!Array.isArray(rangesData) || !Array.isArray(labelsData)) {
            throw new Error("API data is not in the expected array format.");
          }

          const rangesMap = rangesData.reduce((acc, item) => {
            acc[item.field_name] = item;
            return acc;
          }, {});

          // --- THIS IS THE SIMPLIFIED PART ---
          // We no longer need to loop and group the labels.
          // We just map the field_name to its already-existing array of options.
          const labelsMap = labelsData.reduce((acc, item) => {
            acc[item.field_name] = item.labelvalue; // 'labelvalue' is now already an array
            return acc;
          }, {});

          const fieldOrder = [
            "sleephours",
            "sleepquality",
            "exercisehours",
            "workhours",
            "mood",
            "connectwithfamily",
          ];

          const finalQuizStructure = fieldOrder.map((field) => {
            const questionObj = {
              field_name: field,
              question_text: questionsData[field],
            };

            if (field in rangesMap) {
              questionObj.type = "range";
              questionObj.config = {
                min: rangesMap[field].min_value,
                max: rangesMap[field].max_value,
                step: rangesMap[field].step_value,
              };
            } else if (field in labelsMap) {
              questionObj.type = "options";
              // The options are now directly available from the map
              questionObj.options = labelsMap[field];
            }
            return questionObj;
          });

          this.quiz = finalQuizStructure;

          this.quiz.forEach((q) => {
            if (q.type === "range") {
              this.$set(this.answers, q.field_name, q.config.min);
            } else {
              this.$set(this.answers, q.field_name, "");
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
        if (this.currentQuestionIndex > 0) {
          this.currentQuestionIndex--;
        }
      },
      async submitQuiz() {
        // Create the payload for your POST request, matching backend field names
        const payload = {
          userId: 1, // Replace with actual logged-in user ID
          sleepHours: this.answers.sleephours,
          sleepQuality: this.answers.sleepquality,
          exerciseHours: this.answers.exercisehours,
          workingHrs: this.answers.workhours,
          mood: this.answers.mood,
        };

        try {
          await axios.post("/moodMetric", payload);
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
  pointer-events: none;
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
  padding: 18px 64px;
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
