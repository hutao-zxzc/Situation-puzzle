<template>
  <div class="about-view">
    <div class="about-header">
      <button class="back-btn" @click="$emit('back')">← 返回</button>
    </div>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-icon">🐢</div>
      <h1>AI 海龟汤</h1>
      <p class="hero-subtitle">AI Sea Turtle Soup</p>
      <p class="hero-desc">
        一个 AI 驱动的海龟汤（情境推理游戏）Web 应用。<br>
        玩家通过提问来推理出诡异故事背后的真相，<br>
        AI 裁判负责回答「是 / 否 / 无关 / 部分相关」。
      </p>
      <div class="hero-badges">
        <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
        <img src="https://img.shields.io/badge/vue-3.4-42b883.svg" alt="Vue">
        <img src="https://img.shields.io/badge/fastapi-0.109-009688.svg" alt="FastAPI">
      </div>
      <div class="hero-actions">
        <a href="https://github.com/hutao-zxzc/Situation-puzzle" target="_blank" rel="noopener" class="btn btn-primary">
          <svg class="github-icon" viewBox="0 0 16 16"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
          GitHub 仓库
        </a>
      </div>
    </section>

    <!-- 特性 -->
    <section class="section">
      <h2 class="section-title">✨ 特性</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="f in features" :key="f.icon">
          <div class="feature-icon">{{ f.icon }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 技术栈 -->
    <section class="section">
      <h2 class="section-title">🏗️ 技术栈</h2>
      <div class="tech-grid">
        <div class="tech-item" v-for="t in techStack" :key="t.layer">
          <span class="tech-layer">{{ t.layer }}</span>
          <span class="tech-name">{{ t.tech }}</span>
          <span class="tech-desc">{{ t.desc }}</span>
        </div>
      </div>
    </section>

    <!-- 项目结构 -->
    <section class="section">
      <h2 class="section-title">📁 项目结构</h2>
      <pre class="code-block"><code>{{ projectStructure }}</code></pre>
    </section>

    <!-- 快速开始 -->
    <section class="section">
      <h2 class="section-title">🚀 快速开始</h2>
      <div class="hint-box">
        <strong>前置要求</strong>
        <p>Python 3.10+ · Node.js 18+ · 一个 LLM API Key（推荐 <a href="https://open.bigmodel.cn/" target="_blank">智谱 GLM</a> 免费额度）</p>
      </div>
      <div class="steps">
        <div class="step" v-for="(step, i) in steps" :key="i">
          <div class="step-num">{{ i + 1 }}</div>
          <div class="step-body">
            <h4>{{ step.title }}</h4>
            <p v-if="step.desc">{{ step.desc }}</p>
            <pre v-if="step.code"><code>{{ step.code }}</code></pre>
          </div>
        </div>
      </div>
      <div class="hint-box warn">
        <strong>⚠️ 隐私提醒</strong>
        <p>API Key 仅保存在浏览器 localStorage 中，不会上传到任何第三方服务器。</p>
      </div>
    </section>

    <!-- LLM 服务商 -->
    <section class="section">
      <h2 class="section-title">🔧 支持的 LLM 服务商</h2>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>服务商</th><th>Base URL</th><th>推荐模型</th><th>备注</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in providers" :key="p.name">
              <td>{{ p.name }}</td>
              <td><code>{{ p.url }}</code></td>
              <td><code>{{ p.model }}</code></td>
              <td>{{ p.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="note">任何支持 OpenAI 兼容格式的 API 均可使用，只需填写对应的 Base URL 和模型名。</p>
    </section>

    <!-- 游戏玩法 -->
    <section class="section">
      <h2 class="section-title">🎮 游戏玩法</h2>
      <div class="gameplay-list">
        <div class="gameplay-item" v-for="(item, i) in gameplay" :key="i">
          <span class="gameplay-emoji">{{ item.emoji }}</span>
          <div class="gameplay-text">
            <strong>{{ item.title }}</strong>
            <p v-html="item.desc"></p>
          </div>
        </div>
      </div>
      <div class="answers-box">
        <h4>AI 裁判回答类型</h4>
        <div class="answer-tags">
          <span class="tag tag-yes">✅ 是 — 推断正确</span>
          <span class="tag tag-no">❌ 否 — 与真相矛盾</span>
          <span class="tag tag-irrelevant">🔵 无关 — 无直接关联</span>
          <span class="tag tag-partial">🟡 部分相关 — 部分正确</span>
        </div>
      </div>
      <div class="hint-box">
        <strong>📝 回合限制</strong>
        <p>每局最多 <strong>30 轮</strong>提问，超时自动揭示真相。</p>
      </div>
    </section>

    <!-- API 接口 -->
    <section class="section">
      <h2 class="section-title">🔌 API 接口</h2>
      <p class="api-info">
        基础 URL: <code>http://localhost:8000</code><br>
        所有 LLM 相关接口需要在请求体中传入 <code>llm_config</code> 对象
      </p>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>方法</th><th>路径</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="api in apis" :key="api.path">
              <td><code>{{ api.method }}</code></td>
              <td><code>{{ api.path }}</code></td>
              <td>{{ api.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <h4 class="subsection-title">请求示例</h4>
      <pre class="code-block"><code>{{ curlExample }}</code></pre>
    </section>

    <!-- 配置说明 -->
    <section class="section">
      <h2 class="section-title">⚙️ 配置说明</h2>
      <h4 class="subsection-title">前端配置</h4>
      <p class="para">前端配置存储在浏览器 <code>localStorage</code> 中，键名为 <code>turtle_soup_llm_config</code>：</p>
      <pre class="code-block"><code>{{ configJson }}</code></pre>
      <h4 class="subsection-title">后端配置</h4>
      <p class="para">后端<strong>不读取任何环境变量或配置文件</strong>来设置 LLM，所有配置均通过前端请求传入。这保证了：</p>
      <ul class="check-list">
        <li>✅ 多用户可各自使用不同的 LLM 和 API Key</li>
        <li>✅ 服务端不存储任何敏感信息</li>
        <li>✅ 部署简单，无需配置 <code>.env</code></li>
      </ul>
    </section>

    <!-- 开发指南 -->
    <section class="section">
      <h2 class="section-title">🛠️ 开发指南</h2>
      <h4 class="subsection-title">添加新谜题</h4>
      <p class="para">编辑 <code>backend/puzzles_data.py</code>，在 <code>INITIAL_PUZZLES</code> 列表中添加：</p>
      <pre class="code-block"><code>{{ addPuzzleCode }}</code></pre>
      <p class="para">重启后端后自动入库。</p>

      <h4 class="subsection-title">前端开发</h4>
      <pre class="code-block"><code>cd frontend
npm run dev      # 开发模式
npm run build    # 生产构建
npm run preview  # 预览生产构建</code></pre>

      <h4 class="subsection-title">后端开发</h4>
      <pre class="code-block"><code>cd backend
python3 main.py  # 启动服务</code></pre>
    </section>

    <!-- 贡献指南 -->
    <section class="section">
      <h2 class="section-title">🤝 贡献指南</h2>
      <p class="para">欢迎提交 Issue 和 Pull Request！</p>
      <ol class="numbered-list">
        <li>Fork 本仓库</li>
        <li>创建功能分支 (<code>git checkout -b feature/amazing-feature</code>)</li>
        <li>提交更改 (<code>git commit -m 'Add some amazing feature'</code>)</li>
        <li>推送到分支 (<code>git push origin feature/amazing-feature</code>)</li>
        <li>创建 Pull Request</li>
      </ol>
    </section>

    <!-- 开源协议 -->
    <section class="section">
      <h2 class="section-title">📄 开源协议</h2>
      <p class="para">本项目基于 <a href="https://github.com/hutao-zxzc/Situation-puzzle/blob/main/LICENSE" target="_blank">MIT License</a> 开源。</p>
    </section>

    <!-- 致谢 -->
    <section class="section">
      <h2 class="section-title">🙏 致谢</h2>
      <ul class="bullet-list">
        <li><a href="https://vuejs.org/" target="_blank">Vue.js</a> — 渐进式前端框架</li>
        <li><a href="https://fastapi.tiangolo.com/" target="_blank">FastAPI</a> — 高性能 Python Web 框架</li>
        <li><a href="https://vitejs.dev/" target="_blank">Vite</a> — 下一代前端构建工具</li>
        <li>所有参与测试和反馈的朋友们</li>
      </ul>
    </section>

    <!-- Footer -->
    <footer class="about-footer">
      <p>
        <a href="https://github.com/hutao-zxzc/Situation-puzzle" target="_blank" rel="noopener">
          github.com/hutao-zxzc/Situation-puzzle
        </a>
      </p>
      <p class="quote">🐢 海龟汤的魅力在于，真相往往比表面看起来更加离奇。</p>
      <p class="license">MIT License © 2024</p>
    </footer>
  </div>
</template>

<script setup>
const features = [
  { icon: '🤖', title: 'AI 驱动', desc: '支持接入 Kimi、智谱 GLM、通义千问、DeepSeek 等多种大模型' },
  { icon: '🎲', title: 'AI 生成模式', desc: 'LLM 实时生成全新谜题，每次不同' },
  { icon: '📚', title: '题库模式', desc: '内置 39 道经典海龟汤谜题，百玩不厌' },
  { icon: '⚡', title: '智能裁判', desc: 'AI 根据汤底严格判定，只回答「是 / 否 / 无关 / 部分相关」' },
  { icon: '🎨', title: '暗黑科技风 UI', desc: '赛博朋克风格的沉浸式游戏体验' },
  { icon: '🔑', title: '前端配置 API Key', desc: '用户自行填写 LLM API Key，安全私密，服务端不存储任何密钥' },
  { icon: '📱', title: '响应式设计', desc: '支持桌面端和移动端浏览器' },
  { icon: '💾', title: '本地持久化', desc: '游戏配置保存在浏览器 localStorage' },
]

const techStack = [
  { layer: '前端', tech: 'Vue 3 + Vite', desc: '组合式 API，单页应用' },
  { layer: '后端', tech: 'FastAPI + Uvicorn', desc: '异步 Python Web 框架' },
  { layer: '数据库', tech: 'SQLite', desc: '轻量级，开箱即用' },
  { layer: 'LLM 接入', tech: 'OpenAI 兼容 API', desc: '支持所有 OpenAI 格式接口的模型' },
]

const projectStructure = `.
├── backend/                 # FastAPI 后端
│   ├── main.py              # 主程序入口（路由、游戏逻辑）
│   ├── models.py            # SQLAlchemy 数据模型
│   ├── database.py          # 数据库连接与初始化
│   ├── llm_service.py       # LLM 服务（推理/非推理模型自适应）
│   ├── puzzles_data.py      # 39 道内置题库
│   └── requirements.txt     # Python 依赖
│
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── App.vue          # 根组件（路由、全局状态）
│   │   ├── main.js          # 入口文件
│   │   └── components/
│   │       ├── ModeSelect.vue      # 模式选择页
│   │       ├── PuzzleList.vue      # 题库列表
│   │       ├── GamePlay.vue        # 游戏对局页
│   │       └── SettingsModal.vue   # LLM 设置弹窗
│   ├── index.html
│   ├── package.json
│   └── vite.config.js       # Vite 配置（含 /api proxy）
│
└── README.md                # 本文件`

const steps = [
  { title: '克隆项目', code: 'git clone https://github.com/hutao-zxzc/Situation-puzzle.git\ncd Situation-puzzle' },
  { title: '启动后端', desc: 'Python 3.10+，默认端口 8000', code: 'cd backend\npython3 -m venv venv && source venv/bin/activate\npip install -r requirements.txt\npython3 main.py' },
  { title: '启动前端', desc: 'Node.js 18+，默认端口 5173', code: 'cd frontend\nnpm install\nnpm run dev' },
  { title: '配置 LLM', desc: '打开页面 → 点击 ⚙️ 设置 → 选择服务商 → 填入 API Key → 保存' },
]

const providers = [
  { name: 'Moonshot (Kimi)', url: 'https://api.moonshot.cn/v1', model: 'kimi-latest', note: '速度快' },
  { name: '智谱 AI (GLM)', url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-flash', note: '免费' },
  { name: '阿里云 (通义)', url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-turbo', note: '轻量便宜' },
  { name: 'DeepSeek', url: 'https://api.deepseek.com/v1', model: 'deepseek-chat', note: '高性价比' },
]

const gameplay = [
  { emoji: '🎲', title: '选择模式', desc: '<strong>AI 生成</strong> — LLM 实时生成全新谜题，或 <strong>经典题库</strong> — 从 39 道内置谜题中选择' },
  { emoji: '📖', title: '阅读汤面', desc: '阅读题目给出的诡异场景描述' },
  { emoji: '❓', title: '提问推理', desc: '输入<strong>封闭式问题</strong>（能用「是/否」回答），例：「死者是自杀吗？」' },
  { emoji: '🤖', title: '获得回答', desc: 'AI 裁判根据汤底判定并回答' },
  { emoji: '🔍', title: '猜测真相', desc: '点击「<strong>我猜到了</strong>」提交你的答案' },
  { emoji: '👁', title: '查看汤底', desc: '点击「<strong>揭示真相</strong>」查看完整真相' },
]

const apis = [
  { method: 'GET', path: '/puzzles', desc: '获取所有内置谜题' },
  { method: 'POST', path: '/game/start', desc: '开始新游戏' },
  { method: 'POST', path: '/game/{id}/ask', desc: '提交问题' },
  { method: 'POST', path: '/game/{id}/guess', desc: '猜测真相' },
  { method: 'POST', path: '/game/{id}/reveal', desc: '揭示真相' },
  { method: 'POST', path: '/puzzle/generate', desc: 'AI 生成新谜题' },
  { method: 'POST', path: '/debug/llm', desc: '调试 LLM 配置' },
]

const curlExample = `# 开始游戏（题库模式）
curl -X POST http://localhost:8000/game/start \\
  -H "Content-Type: application/json" \\
  -d '{
    "mode": "preset",
    "puzzle_id": 1,
    "llm_config": {
      "api_key": "sk-your-key",
      "base_url": "https://api.moonshot.cn/v1",
      "model": "kimi-latest"
    }
  }'

# 提交问题
curl -X POST http://localhost:8000/game/{session_id}/ask \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "死者是自杀吗？",
    "llm_config": { ... }
  }'`

const configJson = `{
  "api_key": "sk-your-api-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "kimi-latest"
}`

const addPuzzleCode = `{
    "id": 40,
    "title": "新题目名称",
    "soup_surface": "汤面描述...",
    "soup_base": "汤底真相...",
    "key_details": ["线索1", "线索2", "线索3"]
}`
</script>

<style scoped>
.about-view {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.about-header {
  margin-bottom: 1rem;
}

.back-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #8b9bb4;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(0, 255, 200, 0.1);
  border-color: rgba(0, 255, 200, 0.3);
  color: #00ffc8;
}

/* Hero */
.hero {
  text-align: center;
  padding: 2rem 1rem;
  border-bottom: 1px solid rgba(0, 255, 200, 0.1);
  margin-bottom: 2rem;
}

.hero-icon {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.hero h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: #00ffc8;
  text-shadow: 0 0 20px rgba(0, 255, 200, 0.3);
}

.hero-subtitle {
  font-size: 1rem;
  color: #6b7a94;
  margin-top: 0.25rem;
  letter-spacing: 2px;
}

.hero-desc {
  color: #8b9bb4;
  margin-top: 0.75rem;
  line-height: 1.6;
  font-size: 0.9rem;
}

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.4rem;
  margin-top: 1.25rem;
}

.hero-badges img {
  height: 20px;
}

.hero-actions {
  margin-top: 1.25rem;
}

.github-icon {
  width: 16px;
  height: 16px;
}

/* Section */
.section {
  margin-bottom: 2.5rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(0, 255, 200, 0.2);
  color: #e0e6f0;
  display: inline-block;
}

.subsection-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 1.25rem 0 0.5rem;
  color: #8b9bb4;
}

.para {
  color: #8b9bb4;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0.5rem 0;
}

.note {
  color: #6b7a94;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

/* Features */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 255, 200, 0.08);
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.2s;
}

.feature-card:hover {
  border-color: rgba(0, 255, 200, 0.25);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.5rem;
  margin-bottom: 0.4rem;
}

.feature-card h3 {
  font-size: 0.9rem;
  margin: 0 0 0.3rem;
  color: #e0e6f0;
}

.feature-card p {
  font-size: 0.8rem;
  color: #6b7a94;
  margin: 0;
  line-height: 1.4;
}

/* Tech */
.tech-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tech-item {
  display: grid;
  grid-template-columns: 70px 1fr 1.5fr;
  gap: 0.75rem;
  align-items: center;
  padding: 0.6rem 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  font-size: 0.85rem;
}

.tech-layer {
  color: #00ffc8;
  font-weight: 500;
}

.tech-name {
  color: #e0e6f0;
}

.tech-desc {
  color: #6b7a94;
  font-size: 0.8rem;
}

/* Code blocks */
.code-block {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 0.875rem 1rem;
  overflow-x: auto;
  margin: 0.5rem 0;
  color: #00ffc8;
  font-size: 0.78rem;
  line-height: 1.6;
  font-family: 'Fira Code', 'SF Mono', monospace;
}

/* Steps */
.steps {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.step {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.step-num {
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00c9a7, #00a884);
  color: #0a0e1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
}

.step-body h4 {
  margin: 0 0 0.15rem;
  color: #e0e6f0;
  font-size: 0.9rem;
}

.step-body p {
  margin: 0 0 0.3rem;
  color: #6b7a94;
  font-size: 0.8rem;
}

.step-body pre {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  overflow-x: auto;
  margin: 0;
  color: #00ffc8;
  font-size: 0.75rem;
  line-height: 1.5;
  font-family: 'Fira Code', monospace;
}

/* Hint box */
.hint-box {
  background: rgba(0, 255, 200, 0.04);
  border: 1px solid rgba(0, 255, 200, 0.1);
  border-radius: 8px;
  padding: 0.875rem 1rem;
  margin-top: 1rem;
}

.hint-box.warn {
  background: rgba(255, 193, 7, 0.06);
  border-color: rgba(255, 193, 7, 0.15);
}

.hint-box strong {
  color: #00ffc8;
  font-size: 0.85rem;
}

.hint-box.warn strong {
  color: #ffc107;
}

.hint-box p {
  margin: 0.2rem 0 0;
  color: #6b7a94;
  font-size: 0.8rem;
}

.hint-box a {
  color: #00ffc8;
}

/* Table */
.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th,
.data-table td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.data-table th {
  color: #00ffc8;
  font-weight: 600;
  border-bottom: 2px solid rgba(0, 255, 200, 0.25);
  white-space: nowrap;
}

.data-table td {
  color: #8b9bb4;
}

.data-table code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #00ffc8;
}

/* Gameplay */
.gameplay-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.gameplay-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(0, 255, 200, 0.06);
  border-radius: 10px;
  padding: 0.75rem 1rem;
}

.gameplay-emoji {
  font-size: 1.3rem;
}

.gameplay-text strong {
  color: #e0e6f0;
  font-size: 0.9rem;
}

.gameplay-text p {
  margin: 0.1rem 0 0;
  color: #6b7a94;
  font-size: 0.8rem;
  line-height: 1.5;
}

.gameplay-text :deep(strong) {
  color: #00ffc8;
}

.answers-box {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
}

.answers-box h4 {
  margin: 0 0 0.6rem;
  color: #e0e6f0;
  font-size: 0.85rem;
}

.answer-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

/* API info */
.api-info {
  color: #8b9bb4;
  font-size: 0.85rem;
  line-height: 1.8;
  margin-bottom: 0.75rem;
}

.api-info code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  color: #00ffc8;
}

/* Lists */
.check-list,
.bullet-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0;
}

.check-list li,
.bullet-list li {
  color: #8b9bb4;
  font-size: 0.9rem;
  padding: 0.2rem 0;
  line-height: 1.6;
}

.bullet-list li::before {
  content: '• ';
  color: #00ffc8;
}

.numbered-list {
  padding-left: 1.2rem;
  margin: 0.5rem 0;
}

.numbered-list li {
  color: #8b9bb4;
  font-size: 0.9rem;
  padding: 0.2rem 0;
  line-height: 1.6;
}

.numbered-list code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  color: #00ffc8;
  font-size: 0.8rem;
}

/* Links in content */
.about-view :deep(a),
.about-view a {
  color: #00ffc8;
  text-decoration: none;
}

.about-view :deep(a:hover),
.about-view a:hover {
  text-decoration: underline;
}

/* Footer */
.about-footer {
  text-align: center;
  padding: 1.5rem 1rem;
  border-top: 1px solid rgba(0, 255, 200, 0.1);
  margin-top: 1rem;
}

.about-footer a {
  color: #00ffc8;
  text-decoration: none;
  font-size: 0.85rem;
}

.about-footer a:hover {
  text-decoration: underline;
}

.quote {
  color: #6b7a94;
  font-style: italic;
  margin-top: 0.75rem;
  font-size: 0.85rem;
}

.license {
  color: #4a5568;
  font-size: 0.75rem;
  margin-top: 0.4rem;
}

/* Mobile */
@media (max-width: 600px) {
  .hero h1 { font-size: 1.6rem; }
  .features-grid { grid-template-columns: 1fr; }
  .tech-item { grid-template-columns: 60px 1fr; }
  .tech-desc { display: none; }
  .data-table { font-size: 0.75rem; }
  .data-table th, .data-table td { padding: 0.4rem; }
  .gameplay-item { flex-wrap: wrap; }
}
</style>
