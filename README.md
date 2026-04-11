# SparSamp-Stego-System | 基于稀疏采样的可证安全隐写系统

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-000000.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

本仓库是基于 **SparSamp (Sparse Sampling)** 算法实现的生成式语言隐写系统。系统能够在不改变大语言模型（如 GPT-2、Qwen-2.5）原始概率分布的前提下，以 O(1) 的时间复杂度实现秘密消息的高效嵌入与完美提取。

---

## ✨ 核心特性 (Features)

* **可证安全 (Provably Secure)**：理论上隐写文本分布与自然文本分布的 KL 散度严格趋近于 0，完美抗击基于统计学的隐写分析（Steganalysis）。
* **极速采样 (Zero-Overhead Complexity)**：摒弃了传统算术编码（Arithmetic Coding）对全词表重排序的耗时操作，生成速度等同于大模型原生推理速度。
* **模型引擎解耦 (Model-Agnostic)**：系统架构采用松耦合设计，可无缝热切换后端大语言模型（默认支持 `GPT-2` 与 `Qwen-2.5`）。
* **全栈可视化通信 (Full-Stack UI)**：提供现代化 Web 界面，直观展示文本生成、秘密信息嵌入及提取比对的完整流程。

---

## 💡 设计理念 (Design Philosophy)

* **绝对的统计学安全**：基于 SparSamp 算法的核心思想，使得携带秘密信息的隐写文本概率分布，与大语言模型原始的自然语言概率分布完全一致。在理论和实践上抵御任何基于语言统计特性的检测工具。
* **极速推理生成**：不同于传统的编码方式需要对动辄几万大小的词表进行复杂的浮点运算，本系统在每步生成时仅需进行简单的哈希与模运算，将隐写过程的时间复杂度降至 O(1)，真正实现“大模型生成多快，隐写就有多快”。
* **无缝的跨模型兼容**：系统的调度层与模型引擎层完全解耦。无论是自回归的基座模型，还是最新的指令微调大模型，只需对外暴露 Next-Token 的概率分布（Logits），即可无缝接入本隐写系统。

---

## 🏗️ 系统总体架构

本隐写系统采用松耦合的设计理念，总体架构划分为三个主要部分：**数据交互层（前端）**、**隐写调度层（后端）**和**模型引擎层（AI 模型）**。

```text
┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
│  数据交互层 (Web)   │──────▶│  隐写调度层 (API)  │──────▶│ 模型引擎层 (LLMs)  │
│    (Vue3 + Vite)   │◀──────│  (Flask Backend)   │◀──────│  (GPT-2 / Qwen)    │
└────────────────────┘  REST └────────────────────┘ Local └────────────────────┘
                                      │                            │
                                      ▼                            ▼
                           ┌────────────────────┐       ┌────────────────────┐
                           │ SparSamp 核心算法  │       │  自然语言概率分布  │
                           └────────────────────┘       └────────────────────┘
🔄 核心算法流程 (Algorithm Flow)系统采用对称共享密钥（如相同的模型权重、Temperature 参数和随机种子 Seed）来保证通信双方的概率分布强同步。1. 隐写嵌入流程 (Embedding Process)Plaintext发送方 (Alice)                            SparSamp 算法引擎
  │  1. 输入秘密消息 (Secret Message)          │
  │ ───────────────────────────────────────▶ │
  │  2. 转化为二进制比特流 (Bitstream)           │ ──▶ 1. 调用 LLM 获取 Next-Token 概率分布
  │                                          │ ◀── 2. 返回截断后的候选词表 (Candidate Pool)
  │  3. 根据比特流进行稀疏采样 (Sparse Sample)   │
  │ ◀─────────────────────────────────────── │
  │  4. 拼接入参，生成隐写文本 (Stego Text)       │
  ▼
通过微信、邮件等公开社交媒体发送
2. 秘密提取流程 (Extraction Process)Plaintext接收方 (Bob)                              SparSamp 算法引擎
  │  1. 接收隐写文本 (Stego Text)              │
  │ ───────────────────────────────────────▶ │
  │  2. 解析文本，还原出原始 Token 序列         │ ──▶ 1. LLM 使用相同的 Seed 复现前置上下文
  │                                          │ ◀── 2. 返回与发送端完全一致的候选词表
  │  3. 逆向计算 (Inverse Sample) 提取比特     │
  │ ◀─────────────────────────────────────── │
  │  4. 将比特流解码为原始秘密消息               │
  ▼
🚀 快速开始 (Quick Start)环境要求Python: 3.10+Node.js: 18+硬件建议: 推荐使用配备 CUDA 显存的 GPU 以加速 Qwen-2.5 推理，CPU 环境下默认使用 GPT-2。1. 启动后端隐写服务 (Server)Bash# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 启动 Flask 服务
python app.py
服务默认运行在 http://127.0.0.1:50002. 启动前端可视化界面 (Web)Bash# 打开一个新的终端窗口，进入前端目录
cd frontend

# 安装 Node 依赖
npm install

# 启动开发服务器
npm run dev
前端默认运行在 http://localhost:5173，浏览器打开此地址即可使用。📂 项目结构 (Project Structure)PlaintextSparSamp-Stego-System/
├── backend/                    # 隐写调度层 (Flask)
│   ├── app.py                  # API 路由与系统总线
│   ├── requirements.txt        # Python 依赖清单
│   └── sparsamp_algorithm.py   # 稀疏采样核心算法实现
│
├── frontend/                   # 数据交互层 (Vue.js)
│   ├── src/
│   │   ├── App.vue             # 主界面组件
│   │   ├── main.js             # Vue 挂载入口
│   │   └── assets/             # 静态资源与样式
│   ├── package.json            # Node 依赖
│   ├── tailwind.config.js      # CSS 样式配置
│   └── vite.config.js          # Vite 构建配置
│
├── gpt/                        # 模型引擎层: GPT-2 本地权重
├── qwen/                       # 模型引擎层: Qwen-2.5 本地权重
├── DDPM/                       # (扩展) 基于去噪扩散模型的图像隐写研究代码
│
└── README.md                   # 项目说明文档
📡 API 端点说明系统后端通过 RESTful API 提供独立的隐写嵌入与提取服务，方便二次开发接入：方法路径功能说明POST/embed接收秘密消息与模型配置，返回隐写文本及采样 Token 路径POST/extract接收隐写 Token 序列，逆向提取出原始秘密消息📄 许可证 (License)本项目仅用于学术研究与毕业设计展示。项目代码遵循 MIT License。系统内集成的 Qwen-2.5 及 GPT-2 模型权重需遵守其所属机构的开源协议。