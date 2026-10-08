<template>
  <div class="puzzle-list">
    <div class="header">
      <button class="btn btn-secondary" @click="$emit('back')">← 返回</button>
      <h2>选择题目</h2>
      <button class="btn btn-primary" @click="$emit('generate')" :disabled="loading">
        ✨ AI 生成新题
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else class="puzzles">
      <div
        v-for="puzzle in puzzles"
        :key="puzzle.id"
        class="puzzle-card"
        @click="$emit('select', puzzle.id)"
      >
        <div class="puzzle-header">
          <h3>{{ puzzle.title }}</h3>
          <span class="tag" :class="puzzle.source === 'ai_generated' ? 'tag-ai' : 'tag-preset'">
            {{ puzzle.source === 'ai_generated' ? 'AI生成' : '经典' }}
          </span>
        </div>
        <p class="puzzle-preview">{{ puzzle.soup_surface.substring(0, 80) }}...</p>
        <div class="puzzle-stats">
          <span>🎮 {{ puzzle.play_count }} 次游玩</span>
          <span>🎯 {{ puzzle.solve_count }} 次破解</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  puzzles: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})
</script>

<style scoped>
.puzzle-list {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.header h2 {
  font-size: 1.3rem;
  color: #e0e6f0;
}

.puzzles {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.puzzle-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 255, 200, 0.08);
  border-radius: 12px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.puzzle-card:hover {
  border-color: rgba(0, 255, 200, 0.25);
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
}

.puzzle-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.puzzle-header h3 {
  font-size: 1.1rem;
  color: #e0e6f0;
}

.tag {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.tag-preset {
  background: rgba(0, 150, 255, 0.15);
  color: #0096ff;
  border: 1px solid rgba(0, 150, 255, 0.3);
}

.tag-ai {
  background: rgba(0, 255, 200, 0.15);
  color: #00ffc8;
  border: 1px solid rgba(0, 255, 200, 0.3);
}

.puzzle-preview {
  color: #8b9bb4;
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.puzzle-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #5a6a7d;
}
</style>
