<template>
  <div class="game-play">
    <!-- 汤面卡片 -->
    <div class="soup-surface card">
      <div class="card-header">
        <span class="label">🍜 汤面</span>
        <span class="round-badge">{{ game.round }} / {{ game.max_rounds }} 回合</span>
      </div>
      <p class="surface-text">{{ game.soup_surface }}</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: (game.round / game.max_rounds * 100) + '%' }"></div>
      </div>
    </div>

    <!-- 游戏结束状态 -->
    <div v-if="game.status !== 'playing'" class="game-over card" :class="game.status">
      <div class="game-over-icon">
        {{ game.status === 'won' ? '🎉' : game.status === 'lost' ? '😢' : '📖' }}
      </div>
      <h2>
        {{ game.status === 'won' ? '恭喜你猜中了！' : game.status === 'lost' ? '很遗憾，你没能猜中' : '汤底揭晓' }}
      </h2>
      <p v-if="game.status === 'won'" class="game-over-desc">你真是个推理高手！</p>
      <p v-else-if="game.status === 'lost'" class="game-over-desc">回合用完了，真相是...</p>

      <div class="reveal-section">
        <h3>🍲 汤底</h3>
        <p class="base-text">{{ game.soup_base || gameBase }}</p>
      </div>

      <div class="actions">
        <button class="btn btn-primary" @click="$emit('newGame')">再来一局</button>
      </div>
    </div>

    <!-- 问答区域 -->
    <div v-else class="qa-section">
      <!-- 问答历史 -->
      <div class="history card" v-if="game.history?.length > 0">
        <h3 class="history-title">💬 问答记录</h3>
        <div class="history-list">
          <div v-for="(item, idx) in game.history" :key="idx" class="history-item">
            <div class="question">
              <span class="q-mark">Q{{ item.round }}</span>
              <span>{{ item.question }}</span>
            </div>
            <div class="answer">
              <span class="tag" :class="getTagClass(item.type)">{{ item.type }}</span>
              <span class="answer-text">{{ item.answer }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area card">
        <div class="input-tabs">
          <button
            class="tab-btn"
            :class="{ active: inputMode === 'ask' }"
            @click="inputMode = 'ask'"
          >❓ 提问</button>
          <button
            class="tab-btn"
            :class="{ active: inputMode === 'guess' }"
            @click="inputMode = 'guess'"
          >💡 猜真相</button>
        </div>

        <div class="input-box">
          <textarea
            v-if="inputMode === 'ask'"
            v-model="question"
            placeholder="请输入你的问题...（如：死者是自杀吗？）"
            rows="2"
            @keydown.enter.prevent="submitAsk"
          ></textarea>
          <textarea
            v-else
            v-model="guess"
            placeholder="请输入你对真相的猜测..."
            rows="3"
            @keydown.enter.prevent="submitGuess"
          ></textarea>

          <div class="input-actions">
            <button
              class="btn btn-primary"
              :disabled="loading || !canSubmit"
              @click="inputMode === 'ask' ? submitAsk() : submitGuess()"
            >
              <span v-if="loading" class="spinner-small"></span>
              <span v-else>{{ inputMode === 'ask' ? '提问' : '确认猜测' }}</span>
            </button>
            <button class="btn btn-secondary" @click="$emit('reveal')" :disabled="loading">
              📖 直接揭晓
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  game: { type: Object, required: true },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['ask', 'guess', 'reveal', 'newGame'])

const inputMode = ref('ask')
const question = ref('')
const guess = ref('')

const canSubmit = computed(() => {
  if (inputMode.value === 'ask') return question.value.trim().length > 0
  return guess.value.trim().length > 0
})

const gameBase = computed(() => {
  return props.game.soup_base || ''
})

function submitAsk() {
  if (!question.value.trim() || props.loading) return
  emit('ask', question.value.trim())
  question.value = ''
}

function submitGuess() {
  if (!guess.value.trim() || props.loading) return
  emit('guess', guess.value.trim())
  guess.value = ''
}

function getTagClass(type) {
  const map = {
    '是': 'tag-yes',
    '否': 'tag-no',
    '无关': 'tag-irrelevant',
    '部分相关': 'tag-partial'
  }
  return map[type] || 'tag-irrelevant'
}
</script>

<style scoped>
.game-play {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.label {
  font-size: 0.85rem;
  color: #00ffc8;
  font-weight: 500;
}

.round-badge {
  background: rgba(0, 255, 200, 0.1);
  color: #00ffc8;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.surface-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #e0e6f0;
  margin-bottom: 1rem;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00c9a7, #00ffc8);
  transition: width 0.3s ease;
}

/* 问答历史 */
.history-title {
  font-size: 0.9rem;
  color: #8b9bb4;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border-left: 3px solid rgba(0, 255, 200, 0.2);
}

.question {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #e0e6f0;
  font-size: 0.9rem;
}

.q-mark {
  color: #00ffc8;
  font-weight: 500;
  font-size: 0.8rem;
  min-width: 2rem;
}

.answer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.answer-text {
  color: #8b9bb4;
  font-size: 0.85rem;
}

/* 输入区域 */
.input-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #8b9bb4;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  font-size: 0.9rem;
}

.tab-btn.active {
  background: rgba(0, 255, 200, 0.1);
  border-color: rgba(0, 255, 200, 0.3);
  color: #00ffc8;
}

.tab-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.03);
}

.input-box textarea {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #e0e6f0;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  margin-bottom: 0.75rem;
}

.input-box textarea:focus {
  outline: none;
  border-color: rgba(0, 255, 200, 0.3);
}

.input-box textarea::placeholder {
  color: #4a5568;
}

.input-actions {
  display: flex;
  gap: 0.75rem;
}

/* 游戏结束 */
.game-over {
  text-align: center;
  padding: 2rem;
}

.game-over-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.game-over h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.game-over.won h2 {
  color: #00ffc8;
}

.game-over.lost h2 {
  color: #ff6b6b;
}

.game-over.revealed h2 {
  color: #ffc107;
}

.game-over-desc {
  color: #8b9bb4;
  margin-bottom: 1.5rem;
}

.reveal-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  text-align: left;
}

.reveal-section h3 {
  color: #ffc107;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}

.base-text {
  color: #e0e6f0;
  line-height: 1.8;
  font-size: 1rem;
}

.actions {
  margin-top: 1.5rem;
}

.spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
</style>
