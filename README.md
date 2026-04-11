# SparSamp-Stego-System | 基于稀疏采样的可证安全生成式隐写系统

本系统是基于 **SparSamp (Sparse Sampling)** 算法实现的生成式文本隐写原型。通过在大语言模型（LLM）推理过程中进行受控采样，实现了在不改变概率分布前提下的信息嵌入。

---

## 🏗️ 系统总体架构

系统采用前后端分离架构，确保隐写逻辑与模型推理逻辑的解耦。

```text
┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
│  数据交互层 (Web)   │       │  隐写调度层 (API)  │       │ 模型引擎层 (LLMs)  │
│ (Vue3 + Tailwind)  │ ────▶ │  (Flask Backend)   │ ────▶ │ (GPT-2 / Qwen-2.5) │
└────────────────────┘       └────────────────────┘       └────────────────────┘
```

| 组件 | 技术栈 | 核心职责 |
| :--- | :--- | :--- |
| **Frontend** | Vue.js 3, Vite, Tailwind | 用户交互、隐写文本展示、消息提取比对 |
| **Backend** | Python, Flask, PyTorch | 调度隐写引擎、参数管理、API 封装 |
| **Algorithm** | SparSamp Core | 概率分布计算、稀疏采样映射、信息流转换 |
| **Models** | GPT-2, Qwen-2.5 | 提供词表概率分布 (Logits) |

---

## 💡 设计理念 (Design Philosophy)

* **统计不可区分性 (Statistical Indistinguishability)**：核心设计目标是使隐写文本的概率分布与大模型原生生成的文本分布完全一致（KL散度趋于0），从而在理论层面免疫统计隐写分析。
* **低计算开销 (Efficient Complexity)**：采样算法的时间复杂度为 $O(1)$。
* **模型引擎解耦 (Engine Decoupling)**：隐写层仅依赖模型输出的概率向量。系统可无缝切换不同规模的 LLM 基座，具备极强的可扩展性。

---

## ✨ 功能特性

* **理论可证安全**：完美抗击基于频率分析和统计规律的隐写检测。
* **极速采样映射**：采样延迟极低，不影响大语言模型的实时推理输出。
* **双模适配**：支持基座模型（Base）与指令微调模型（Chat）的隐写任务。
* **可视化全流程**：直观展示从原始比特流到隐写文本的映射路径。

---

## 📡 API 端点说明

系统后端通过标准 RESTful 接口对外提供隐写服务：

| 方法 | 路径 | 参数 | 说明 |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/stego/embed` | `message`, `model_type`, `seed` | 秘密信息嵌入，返回生成的隐写文本 |
| `POST` | `/api/v1/stego/extract` | `stego_text`, `model_type`, `seed` | 从隐写文本中逆向提取原始信息 |
| `GET` | `/api/v1/model/status` | - | 获取当前模型引擎状态与显存占用情况 |

---

## 🔄 隐写通信流程



### 1. 发送端 (Alice) 嵌入流程
1. **比特转换**：将秘密信息映射为二进制流。
2. **分布预测**：根据上下文，通过模型获取下一步所有词的预测概率。
3. **稀疏采样**：SparSamp 算法根据当前比特位在候选空间中选定 Token。

### 2. 接收端 (Bob) 提取流程
1. **状态对齐**：使用共享密钥（Shared Seed）复现相同的预测分布。
2. **逆向推导**：识别隐写文本中的 Token，推导出对应的原始比特位。
3. **信息还原**：拼接比特流，恢复原始秘密消息。

---

## 🚀 快速开始

### 1. 启动后端 (Server)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. 启动前端 (Web)
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 项目结构

```text
.
├── backend/                # Flask 服务及核心算法
│   ├── app.py              # 服务入口
│   └── sparsamp_algorithm.py # SparSamp 算法核心实现
├── frontend/               # Vue3 前端源代码
├── gpt/                    # GPT-2 模型权重
├── qwen/                   # Qwen-2.5 模型权重
└── README.md               # 项目文档
```

---

## 📄 许可证

本项目遵循 **MIT License** 开源协议。
