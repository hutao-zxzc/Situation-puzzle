<template>
  <div class="mode-select">
    <h2 class="section-title">选择游戏模式</h2>
    <p class="section-desc">AI 海龟汤，每局最多 30 回合</p>

    <div class="modes">
      <div class="mode-card mode-ai" @click="$emit('select', 'ai')">
        <div class="mode-icon">✨</div>
        <h3>AI 生成</h3>
        <p>LLM 现场生成全新谜题</p>
        <div class="mode-tag">每次不同</div>
      </div>

      <div class="mode-card mode-preset" @click="$emit('select', 'preset')">
        <div class="mode-icon">📚</div>
        <h3>预置题库</h3>
        <p>经典海龟汤，百玩不厌</p>
        <div class="mode-tag">40+ 精选</div>
      </div>
    </div>

    <div class="rules">
      <h3>📋 游戏规则</h3>
      <ol>
        <li>系统给出「汤面」（谜题描述）</li>
        <li>你可以提问，AI 裁判会回答「是/否/无关/部分相关」</li>
        <li>每次回答附带简短提示</li>
        <li>最多 30 回合，猜中真相或揭晓汤底</li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
.mode-select {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-title {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #e0e6f0;
}

.section-desc {
  text-align: center;
  color: #8b9bb4;
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.mode-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 255, 200, 0.1);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.mode-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #00ffc8, transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.mode-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 255, 200, 0.3);
  box-shadow: 0 8px 32px rgba(0, 255, 200, 0.1);
}

.mode-card:hover::before {
  opacity: 1;
}

.mode-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.mode-card h3 {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  color: #e0e6f0;
}

.mode-card p {
  color: #8b9bb4;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.mode-tag {
  display: inline-block;
  padding: 0.35rem 1rem;
  background: rgba(0, 255, 200, 0.1);
  color: #00ffc8;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.rules {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
}

.rules h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: #e0e6f0;
}

.rules ol {
  padding-left: 1.2rem;
  color: #8b9bb4;
  line-height: 2;
  font-size: 0.9rem;
}

.rules li {
  padding-left: 0.5rem;
}
</style>
