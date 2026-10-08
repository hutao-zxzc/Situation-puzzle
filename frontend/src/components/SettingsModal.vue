<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal card">
      <div class="modal-header">
        <h3>⚙️ LLM 设置</h3>
        <button class="close-btn" @click="close">✕</button>
      </div>

      <div class="form-group">
        <label>API Key</label>
        <input
          v-model="localConfig.api_key"
          type="password"
          placeholder="sk-..."
          @input="changed = true"
        />
        <p class="hint">你的 API Key，仅存储在本地浏览器</p>
      </div>

      <div class="form-group">
        <label>Base URL</label>
        <input
          v-model="localConfig.base_url"
          type="text"
          placeholder="https://api.moonshot.cn/v1"
          @input="changed = true"
        />
      </div>

      <div class="form-group">
        <label>模型</label>
        <input
          v-model="localConfig.model"
          type="text"
          placeholder="kimi-latest"
          @input="changed = true"
        />
      </div>

      <div class="preset-links">
        <span class="preset-label">快速设置（推荐快模型）：</span>
        <button class="preset-btn" @click="setPreset('kimi')">🌙 Kimi</button>
        <button class="preset-btn" @click="setPreset('glm')">🧠 GLM免费</button>
        <button class="preset-btn" @click="setPreset('qwen')">⚡ 通义</button>
        <button class="preset-btn" @click="setPreset('deepseek')">🔥 DeepSeek</button>
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" @click="close">取消</button>
        <button class="btn btn-primary" @click="save" :disabled="!localConfig.api_key">
          💾 保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  config: Object
})

const emit = defineEmits(['update:show', 'save'])

const changed = ref(false)
const localConfig = ref({
  api_key: '',
  base_url: 'https://api.moonshot.cn/v1',
  model: 'kimi-latest'
})

watch(() => props.show, (val) => {
  if (val) {
    localConfig.value = { ...props.config }
    changed.value = false
  }
})

function close() {
  emit('update:show', false)
}

function save() {
  emit('save', { ...localConfig.value })
  close()
}

function setPreset(name) {
  changed.value = true
  const presets = {
    kimi: { base_url: 'https://api.moonshot.cn/v1', model: 'kimi-latest' },
    'kimi-reasoning': { base_url: 'https://api.moonshot.cn/v1', model: 'kimi-k2-6' },
    glm: { base_url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-flash' },
    'glm-pro': { base_url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4' },
    qwen: { base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-turbo' },
    deepseek: { base_url: 'https://api.deepseek.com/v1', model: 'deepseek-chat' }
  }
  const p = presets[name]
  if (p) {
    localConfig.value.base_url = p.base_url
    localConfig.value.model = p.model
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  width: 100%;
  max-width: 420px;
  animation: modalIn 0.2s ease;
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  font-size: 1.1rem;
  color: #e0e6f0;
}

.close-btn {
  background: none;
  border: none;
  color: #8b9bb4;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #e0e6f0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: #8b9bb4;
  margin-bottom: 0.35rem;
}

.form-group input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #e0e6f0;
  font-family: inherit;
  font-size: 0.9rem;
}

.form-group input:focus {
  outline: none;
  border-color: rgba(0, 255, 200, 0.4);
}

.form-group input::placeholder {
  color: #4a5568;
}

.hint {
  font-size: 0.75rem;
  color: #5a6a7d;
  margin-top: 0.25rem;
}

.preset-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.preset-label {
  font-size: 0.8rem;
  color: #8b9bb4;
}

.preset-btn {
  padding: 0.3rem 0.8rem;
  background: rgba(0, 255, 200, 0.1);
  border: 1px solid rgba(0, 255, 200, 0.2);
  border-radius: 6px;
  color: #00ffc8;
  font-size: 0.8rem;
  cursor: pointer;
  font-family: inherit;
}

.preset-btn:hover {
  background: rgba(0, 255, 200, 0.2);
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}
</style>
