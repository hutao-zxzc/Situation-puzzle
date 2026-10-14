<template>
  <div class="review-overlay" @click.self="$emit('close')">
    <div class="review-modal">
      <div class="review-header">
        <h2>📋 游戏复盘</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="review-body">
        <div class="review-section stats">
          <div class="stat-item">
            <span class="stat-num">{{ review.total_rounds || 0 }}</span>
            <span class="stat-label">总回合</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ review.hints_used || 0 }}</span>
            <span class="stat-label">消耗提示</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ statusIcon }}</span>
            <span class="stat-label">结果</span>
          </div>
        </div>

        <div class="review-section" v-if="review.highlights">
          <h3>💡 推理亮点</h3>
          <p>{{ review.highlights }}</p>
        </div>

        <div class="review-section" v-if="review.blind_spots">
          <h3>🔍 盲区分析</h3>
          <p>{{ review.blind_spots }}</p>
        </div>

        <div class="review-section soup-base-section">
          <h3>👁 完整汤底</h3>
          <div class="soup-base-content">
            <p>{{ review.soup_base }}</p>
          </div>
        </div>

        <div class="review-section verdict" v-if="review.verdict">
          <p class="verdict-text">{{ review.verdict }}</p>
        </div>
      </div>

      <div class="review-footer">
        <button class="btn btn-primary" @click="$emit('new-game')">🎮 再来一局</button>
        <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps(['review', 'status'])
defineEmits(['close', 'new-game'])

const statusIcon = computed(() => {
  const s = props.status || props.review?.status
  if (s === 'won') return '✅'
  if (s === 'lost') return '⏰'
  return '🏳️'
})
</script>

<style scoped>
.review-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.review-modal {
  background: #12121a;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  max-height: 85vh;
  overflow-y: auto;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.review-header h2 {
  font-size: 1.1rem;
  color: #fff;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 1.2rem;
  cursor: pointer;
}

.close-btn:hover { color: #fff; }

.review-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.review-section h3 {
  font-size: 0.95rem;
  color: #00ffc8;
  margin-bottom: 0.5rem;
}

.review-section p {
  color: #ccc;
  font-size: 0.9rem;
  line-height: 1.6;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  background: rgba(255,255,255,0.02);
  padding: 1rem;
  border-radius: 12px;
}

.stat-item {
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #00ffc8;
}

.stat-label {
  font-size: 0.8rem;
  color: #888;
}

.soup-base-section {
  background: rgba(0, 255, 200, 0.05);
  border: 1px solid rgba(0, 255, 200, 0.15);
  border-radius: 12px;
  padding: 1rem;
}

.soup-base-content p {
  color: #e0e6f0;
  line-height: 1.7;
}

.verdict {
  text-align: center;
  padding: 0.75rem;
}

.verdict-text {
  color: #00ffc8;
  font-size: 1rem;
  font-style: italic;
}

.review-footer {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.btn {
  padding: 0.65rem 1.5rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #00c9a7, #00a884);
  color: #0a0e1a;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 201, 167, 0.3);
}

.btn-secondary {
  background: rgba(255,255,255,0.05);
  color: #888;
  border: 1px solid rgba(255,255,255,0.1);
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
</style>
