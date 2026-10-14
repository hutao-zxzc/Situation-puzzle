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
        <button class="btn btn-primary" @click="$emit('review')">📋 查看复盘</button>
        <button class="btn btn-secondary" @click="$emit('newGame')">再来一局</button>
      </div>
    </div>

    <!-- 问答区域 -->
    <div v-if="game.status === 'playing'" class="qa-section">
      <!-- 新局引导 -->
      <div v-if="isNewGame" class="guide-banner card">
        <p>🎮 游戏开始！输入封闭式问题来推理真相。</p>
        <p>💡 输入 <strong>【提示】</strong> 可获取 AI 模糊线索（限3次，消耗1轮）</p>
        <p>🏁 输入 <strong>【复盘/汤底/结束】</strong> 结束本局并查看完整复盘</p>
        <p class="spoiler-warning">🛡️ 游戏进行中禁止剧透，多局上下文隔离</p>
      </div>

      <!-- 问答历史 -->
      <div class="history card" v-if="game.history?.length > 0">
        <h3 class="history-title">💬 问答记录</h3>
        <div class="history-list">
          <div v-for="(item, idx) in game.history" :key="idx" class="history-item" :class="{ 'hint-item': item.is_hint }">
            <div v-if="item.is_hint" class="hint-bubble">
              <span class="hint-label">💡 提示</span>
              <p class="hint-text">{{ item.answer }}</p>
            </div>
            <template v-else>
              <div class="question">
                <span class="q-mark">Q{{ item.round }}</span>
                <span>{{ item.question }}</span>
              </div>
              <div class="answer">
                <span class="tag" :class="getTagClass(item.type)">{{ item.type }}</span>
                <span class="answer-text">{{ item.answer }}</span>
              </div>
            </template>
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
          <div class="input-hints-bar">
            <span v-if="game.hints_used < game.max_hints" class="hint-available">
              💡 提示剩余 {{ game.max_hints - game.hints_used }} 次
            </span>
            <span v-else class="hint-exhausted">💡 提示次数已用尽</span>
          </div>
          <textarea
            v-if="inputMode === 'ask'"
            v-model="question"
            placeholder="请输入你的问题...（输入【提示】获取线索，【复盘/汤底/结束】结束本局）"
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
            <button class="btn btn-hint" @click="$emit('hint')" :disabled="loading || game.hints_used >= game.max_hints">
              💡 提示
            </button>
            <button class="btn btn-secondary" @click="$emit('review')" :disabled="loading">
              📋 复盘
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

const emit = defineEmits(['ask', 'guess', 'reveal', 'hint', 'review', 'newGame'])

// 监听 game 变化：换局时重置引导横幅
import { watch } from 'vue'
watch(() => props.game?.session_id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    isNewGame.value = true
  }
})

const inputMode = ref('ask')
const question = ref('')
const guess = ref('')
const isNewGame = ref(true)

const canSubmit = computed(() => {
  if (inputMode.value === 'ask') return question.value.trim().length > 0
  return guess.value.trim().length > 0
})

const gameBase = computed(() => {
  return props.game.soup_base || ''
})

function submitAsk() {
  const q = question.value.trim()
  if (!q || props.loading) return

  // 检测关键词：提示
  if (q === '提示' || q === '【提示】') {
    isNewGame.value = false
    emit('hint')
    question.value = ''
    return
  }

  // 检测关键词：复盘/汤底/结束
  if (['复盘', '汤底', '结束', '【复盘】', '【汤底】', '【结束】'].includes(q)) {
    isNewGame.value = false
    emit('review')
    question.value = ''
    return
  }

  // 防剧透检测
  if (props.game.status === 'playing') {
    const spoilerWords = ['汤底', '真相', '答案', '原来', '完整', '解析']
    if (spoilerWords.some(w => q.includes(w)) && !q.includes('?') && !q.includes('？')) {
      alert('🛡️ 游戏进行中禁止剧透！请继续推理，或发送【复盘/汤底/结束】来结束本局。')
      question.value = ''
      return
    }
  }

  isNewGame.value = false
  emit('ask', q)
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

/* 提示按钮 — 和复盘按钮完全一致，用更高优先级覆盖 */
.input-actions .btn-hint {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #e0e6f0 !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 0.75rem 1.5rem !important;
  border-radius: 8px !important;
  font-size: 1rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  font-family: inherit !important;
}

.input-actions .btn-hint:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.input-actions .btn-hint:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
  background: rgba(255, 255, 255, 0.03) !important;
  color: #8b9bb4 !important;
}

/* 提示次数状态栏 */
.input-hints-bar {
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.hint-available {
  color: #8b9bb4;
}

.hint-exhausted {
  color: #ff6b6b;
}

/* 新局引导横幅 */
.guide-banner {
  background: rgba(0, 255, 200, 0.04);
  border: 1px solid rgba(0, 255, 200, 0.1);
  margin-bottom: 1rem;
}

.guide-banner p {
  color: #a0aec0;
  font-size: 0.88rem;
  line-height: 1.7;
  margin-bottom: 0.25rem;
}

.guide-banner p:last-child {
  margin-bottom: 0;
}

.guide-banner .spoiler-warning {
  color: #ffc107;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

/* 提示在历史记录中的样式 */
.hint-item {
  border-left-color: rgba(255, 193, 7, 0.4) !important;
  background: rgba(255, 193, 7, 0.03) !important;
}

.hint-bubble {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.hint-label {
  color: #ffc107;
  font-size: 0.8rem;
  font-weight: 500;
}

.hint-text {
  color: #e0e6f0;
  font-size: 0.9rem;
  line-height: 1.5;
  font-style: italic;
}
</style>
