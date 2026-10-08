# 🐢 AI 海龟汤 (AI Sea Turtle Soup)

> 一个 AI 驱动的海龟汤（情境推理游戏）Web 应用。玩家通过提问来推理出诡异故事背后的真相，AI 裁判负责回答「是 / 否 / 无关 / 部分相关」。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.4-42b883.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.109-009688.svg)

---

## ✨ 特性

- 🤖 **AI 驱动** — 支持接入 Kimi、智谱 GLM、通义千问、DeepSeek 等多种大模型
- 🎮 **双模式游戏**
  - 🎲 **AI 生成模式** — LLM 实时生成全新谜题
  - 📚 **题库模式** — 内置 39 道经典海龟汤谜题
- ⚡ **智能裁判** — AI 根据汤底严格判定玩家提问，只回答「是 / 否 / 无关 / 部分相关」
- 🎨 **暗黑科技风 UI** — 赛博朋克风格的沉浸式游戏体验
- 🔑 **前端配置 API Key** — 用户自行填写 LLM API Key，安全私密，服务端不存储任何密钥
- 📱 **响应式设计** — 支持桌面端和移动端浏览器
- 💾 **本地持久化** — 游戏配置保存在浏览器 localStorage

---

## 🏗️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite | 组合式 API，单页应用 |
| 后端 | FastAPI + Uvicorn | 异步 Python Web 框架 |
| 数据库 | SQLite | 轻量级，开箱即用 |
| LLM 接入 | OpenAI 兼容 API | 支持所有 OpenAI 格式接口的模型 |

---

## 📁 项目结构

. ├── backend/                    # FastAPI 后端 │   ├── main.py                 # 主程序入口（路由、游戏逻辑） │   ├── models.py               # SQLAlchemy 数据模型 │   ├── database.py             # 数据库连接与初始化 │   ├── llm_service.py          # LLM 服务（推理/非推理模型自适应） │   ├── puzzles_data.py         # 39 道内置题库 │   └── requirements.txt        # Python 依赖 │ ├── frontend/                   # Vue 3 前端 │   ├── src/ │   │   ├── App.vue             # 根组件（路由、全局状态） │   │   ├── main.js             # 入口文件 │   │   └── components/ │   │       ├── ModeSelect.vue  # 模式选择页 │   │       ├── PuzzleList.vue  # 题库列表 │   │       ├── GamePlay.vue    # 游戏对局页 │   │       └── SettingsModal.vue  # LLM 设置弹窗 │   ├── index.html │   ├── package.json │   └── vite.config.js          # Vite 配置（含 /api proxy） │ └── README.md                   # 本文件
```
---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- 一个 LLM API Key（推荐 [智谱 GLM](https://open.bigmodel.cn/) 免费额度）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai-sea-turtle-soup.git
cd ai-sea-turtle-soup
```
### 2. 启动后端
```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（默认端口 8000）
python3 main.py
```
后端服务将运行在 `http://localhost:8000`
### 3. 启动前端
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 5173）
npm run dev
```
前端页面将运行在 `http://localhost:5173`
### 4. 配置 LLM
1. 打开浏览器访问 `http://localhost:5173`
2. 点击右上角 **⚙️ 设置**
3. 选择服务商预设（Kimi / GLM / 通义 / DeepSeek）或手动填写
4. 填入你的 API Key
5. 点击 **保存**
> ⚠️ **API Key 仅保存在浏览器 localStorage 中，不会上传到任何第三方服务器。**
## 🔧 支持的 LLM 服务商
服务商	Base URL	推荐模型	备注
Moonshot (Kimi)	https://api.moo	kimi-lates	速度快
智谱 AI (GLM)	https://open.bigmodel	glm-4-flas	**免费**
阿里云 (通义)	https://dashscope.aliyuncs.c	qwen-turb	轻量便宜
DeepSeek	https://api.deep	deepseek-cha	高性价比
> 任何支持 OpenAI 兼容格式的 API 均可使用，只需填写对应的 Base URL 和模型名。
## 🎮 游戏玩法
1. **选择模式**
  - **🤖 AI 生成** — LLM 实时生成一道全新谜题
  - **📚 经典题库** — 从 39 道内置谜题中选择
2. **阅读汤面** — 阅读题目给出的诡异场景描述
3. **提问推理** — 在输入框中输入**封闭式问题**（能用「是/否」回答的问题）
  - 例：「死者是自杀吗？」「现场有第三个人吗？」
4. **获得回答** — AI 裁判根据汤底判定，回答：
  - ✅ **是** — 你的推断正确
  - ❌ **否** — 与真相矛盾
  - 🔵 **无关** — 与案件无直接关联
  - 🟡 **部分相关** — 部分正确但不完全准确
5. **猜测真相** — 当你认为已经推理出完整真相时，点击「🔍 我猜到了」提交你的答案
6. **查看汤底** — 无论猜对与否，都可以随时点击「👁 揭示真相」查看完整汤底
> 📝 每局最多 **30 轮**提问，超时自动揭示真相。
## 🔌 API 接口
### 基础信息
- 基础 URL: `http://localhost:8000`
- 所有 LLM 相关接口需要在请求体中传入 `llm_config` 对象
### 接口列表
方法	路径	说明
GET	/puzzle	获取所有内置谜题
POST	/game/star	开始新游戏
POST	/game/{id}/as	提交问题
POST	/game/{id}	猜测真相
POST	/game/{id}	揭示真相
POST	/puzzle/ge	AI 生成新谜题
POST	/debug/ll	调试 LLM 配置
### 请求示例
```bash
# 开始游戏（题库模式）
curl -X POST http://localhost:8000/game/start \
  -H "Content-Type: application/json" \
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
curl -X POST http://localhost:8000/game/{session_id}/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "死者是自杀吗？",
    "llm_config": { ... }
  }'
```
## ⚙️ 配置说明
### 前端配置
前端配置存储在浏览器 `localStorage` 中，键名为 `turtle_soup_llm_config`：
```json
{
  "api_key": "sk-your-api-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "kimi-latest"
}
```
### 后端配置
后端**不读取任何环境变量或配置文件**来设置 LLM，所有配置均通过前端请求传入。这保证了：
- ✅ 多用户可各自使用不同的 LLM 和 API Key
- ✅ 服务端不存储任何敏感信息
- ✅ 部署简单，无需配置 `.env`
## 🛠️ 开发指南
### 添加新谜题
编辑 `backend/puzzles_data.py`，在 `INITIAL_PUZZLES` 列表中添加：
```python
{
    "id": 40,
    "title": "新题目名称",
    "soup_surface": "汤面描述...",
    "soup_base": "汤底真相...",
    "key_details": ["线索1", "线索2", "线索3"]
}
```
重启后端后自动入库。
### 前端开发
```bash
cd frontend
npm run dev        # 开发模式
npm run build      # 生产构建
npm run preview    # 预览生产构建
```
### 后端开发
```bash
cd backend
python3 main.py    # 启动服务
```
## 🤝 贡献指南
欢迎提交 Issue 和 Pull Request！
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request
## 📄 开源协议
本项目基于 [MIT License](LICENSE) 开源。
## 🙏 致谢
- [Vue.js](https://vuejs.org/) — 渐进式前端框架
- [FastAPI](https://fastapi.tiangolo.com/) — 高性能 Python Web 框架
- [Vite](https://vitejs.dev/) — 下一代前端构建工具
- 所有参与测试和反馈的朋友们
> 🐢 *海龟汤的魅力在于，真相往往比表面看起来更加离奇。*
```
---

文件路径：`/home/ubuntu/workspace/README.md`

README 包含：
- 项目介绍与徽章
- 特性列表（双模式、AI 裁判、暗黑科技 UI、前端配置 API Key 等）
- 技术栈表格
- 项目结构树
- 快速开始（克隆、启动前后端、配置 LLM）
- 支持的 LLM 服务商表格（含免费选项）
- 游戏玩法说明
- API 接口文档 + curl 示例
- 配置说明（前后端配置方式）
- 开发指南（添加谜题、前后端开发命令）
- 贡献指南
- MIT 开源协议
```
