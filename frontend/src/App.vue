<template>
  <div class="app">
    <header class="app-header">
      <h1 class="title">
        <span class="icon">🐢</span>
        AI 海龟汤
      </h1>
      <p class="subtitle">AI 驱动的推理解谜游戏</p>
      <button class="settings-btn" @click="showSettings = true" title="设置">
        ⚙️
      </button>
    </header>

    <main class="app-main">
      <ModeSelect v-if="currentView === 'mode'" @select="onModeSelect" />
      <PuzzleList
        v-else-if="currentView === 'puzzles'"
        :puzzles="puzzles"
        :loading="loading"
        @select="onPuzzleSelect"
        @back="currentView = 'mode'"
        @generate="onGeneratePuzzle"
      />
      <GamePlay
        v-else-if="currentView === 'game'"
        :game="gameState"
        :loading="loading"
        @ask="onAsk"
        @guess="onGuess"
        @reveal="onReveal"
        @newGame="currentView = 'mode'"
      />
    </main>

    <footer class="app-footer">
      <p>AI 海龟汤 · 推理与挑战</p>
    </footer>

    <SettingsModal
      v-model:show="showSettings"
      :config="llmConfig"
      @save="onSaveSettings"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ModeSelect from './components/ModeSelect.vue'
import PuzzleList from './components/PuzzleList.vue'
import GamePlay from './components/GamePlay.vue'
import SettingsModal from './components/SettingsModal.vue'

const API_BASE = '/api'

const currentView = ref('mode')
const puzzles = ref([])
const gameState = ref(null)
const loading = ref(false)
const showSettings = ref(false)

const llmConfig = ref({
  api_key: '',
  base_url: 'https://api.moonshot.cn/v1',
  model: 'kimi-latest'
})

const LLM_CONFIG_KEY = 'turtle_soup_llm_config'

onMounted(() => {
  const saved = localStorage.getItem(LLM_CONFIG_KEY)
  if (saved) {
    try {
      llmConfig.value = JSON.parse(saved)
    } catch (e) {
      // ignore
    }
  }
})

function onSaveSettings(config) {
  llmConfig.value = config
  localStorage.setItem(LLM_CONFIG_KEY, JSON.stringify(config))
}

function getLLMBody() {
  return { llm_config: llmConfig.value }
}

function checkSettings() {
  if (!llmConfig.value.api_key) {
    showSettings.value = true
    return false
  }
  return true
}

async function safeJson(res) {
  const text = await res.text()
  if (!text) throw new Error('服务器返回空响应，后端可能未启动')
  try {
    return JSON.parse(text)
  } catch (e) {
    throw new Error(`服务器返回非 JSON: ${text.slice(0, 80)}`)
  }
}

async function fetchPuzzles() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/puzzles`)
    puzzles.value = await safeJson(res)
  } catch (e) {
    alert('获取题库失败：' + e.message)
  } finally {
    loading.value = false
  }
}

async function onModeSelect(mode) {
  if (mode === 'preset') {
    await fetchPuzzles()
    currentView.value = 'puzzles'
  } else {
    if (!checkSettings()) return
    await startGame('ai')
  }
}

async function onPuzzleSelect(puzzleId) {
  if (!checkSettings()) return
  await startGame('preset', puzzleId)
}

async function onGeneratePuzzle() {
  if (!checkSettings()) return
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/puzzle/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(getLLMBody())
    })
    if (!res.ok) {
      const err = await safeJson(res)
      throw new Error(err.detail || '生成失败')
    }
    const puzzle = await safeJson(res)
    await startGame('ai', puzzle.id)
  } catch (e) {
    alert('生成题目失败：' + e.message)
  } finally {
    loading.value = false
  }
}

async function startGame(mode, puzzleId = null) {
  loading.value = true
  try {
    const body = { mode, ...getLLMBody() }
    if (puzzleId) body.puzzle_id = puzzleId
    const res = await fetch(`${API_BASE}/game/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!res.ok) {
      const err = await safeJson(res)
      throw new Error(err.detail || '启动游戏失败')
    }
    gameState.value = await safeJson(res)
    currentView.value = 'game'
  } catch (e) {
    alert('启动游戏失败：' + e.message)
  } finally {
    loading.value = false
  }
}

async function onAsk(question) {
  if (!checkSettings()) return
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/game/${gameState.value.session_id}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, ...getLLMBody() })
    })
    if (!res.ok) {
      const err = await safeJson(res)
      throw new Error(err.detail || '提问失败')
    }
    const result = await safeJson(res)
    gameState.value = { ...gameState.value, ...result }
  } catch (e) {
    alert('提问失败：' + e.message)
  } finally {
    loading.value = false
  }
}

async function onGuess(guess) {
  if (!checkSettings()) return
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/game/${gameState.value.session_id}/guess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ guess, ...getLLMBody() })
    })
    if (!res.ok) {
      const err = await safeJson(res)
      throw new Error(err.detail || '猜测失败')
    }
    const result = await safeJson(res)
    gameState.value = { ...gameState.value, ...result }
  } catch (e) {
    alert('猜测失败：' + e.message)
  } finally {
    loading.value = false
  }
}

async function onReveal() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/game/${gameState.value.session_id}/reveal`, {
      method: 'POST'
    })
    if (!res.ok) {
      const err = await safeJson(res)
      throw new Error(err.detail || '揭晓失败')
    }
    const result = await safeJson(res)
    gameState.value = { ...gameState.value, ...result }
  } catch (e) {
    alert('揭晓失败：' + e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #0a0e1a;
  color: #e0e6f0;
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  text-align: center;
  padding: 2rem 1rem 1rem;
  background: linear-gradient(180deg, #0f1729 0%, #0a0e1a 100%);
  border-bottom: 1px solid rgba(0, 255, 200, 0.1);
  position: relative;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #00ffc8;
  text-shadow: 0 0 20px rgba(0, 255, 200, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.icon {
  font-size: 2.2rem;
}

.subtitle {
  margin-top: 0.5rem;
  color: #8b9bb4;
  font-size: 0.9rem;
  letter-spacing: 2px;
}

.settings-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: rgba(0, 255, 200, 0.1);
  border-color: rgba(0, 255, 200, 0.3);
}

.app-main {
  flex: 1;
  padding: 1rem;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  text-align: center;
  padding: 1rem;
  color: #4a5568;
  font-size: 0.8rem;
  border-top: 1px solid rgba(0, 255, 200, 0.05);
}

/* 通用按钮样式 */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #00c9a7 0%, #00a884 100%);
  color: #0a0e1a;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 201, 167, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #e0e6f0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  color: white;
}

.btn-danger:hover {
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* 卡片样式 */
.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 255, 200, 0.08);
  border-radius: 12px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
}

/* 加载动画 */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #00ffc8;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0, 255, 200, 0.2);
  border-top-color: #00ffc8;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 标签样式 */
.tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.tag-yes {
  background: rgba(0, 201, 167, 0.15);
  color: #00c9a7;
  border: 1px solid rgba(0, 201, 167, 0.3);
}

.tag-no {
  background: rgba(255, 107, 107, 0.15);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.tag-irrelevant {
  background: rgba(139, 155, 180, 0.15);
  color: #8b9bb4;
  border: 1px solid rgba(139, 155, 180, 0.3);
}

.tag-partial {
  background: rgba(255, 193, 7, 0.15);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #0a0e1a;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 200, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 200, 0.4);
}
</style>
