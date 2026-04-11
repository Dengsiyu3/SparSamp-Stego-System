# 🛡️ SparSamp-Stego-System | 基于稀疏采样的可证安全隐写系统

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

本仓库是基于 **SparSamp (Sparse Sampling)** 算法实现的可证安全生成式隐写系统。系统能够在不改变大语言模型（如 GPT-2、Qwen-2.5）原始概率分布的前提下，以 $O(1)$ 的时间复杂度实现秘密消息的高效嵌入与完美提取。

> 🎓 **本项目为本人的本科毕业设计成果**

## ✨ 核心特性 (Features)

- **可证安全 (Provably Secure)**：理论上隐写文本分布与自然文本分布的 KL 散度趋近于 0，完美抗击统计学隐写分析。
- **极速采样 ($O(1)$ Complexity)**：摈弃了传统方法对全词表重排序的耗时操作，生成速度等同于大模型原生推理速度。
- **高嵌入率 (High Utilization)**：支持长文本分段嵌入（推荐 $LM=64$），实际信息熵利用率可达 99% 以上。
- **全栈可视化界面**：提供现代化 Vue3 前端交互界面，实时展示 Token 采样路径与二进制转换过程。

## 📸 系统演示 (Demo)

![System Demo](./assets/demo.png)
*(图：系统前端界面展示，成功将秘密消息嵌入 GPT-2 生成文本并完美逆向提取)*

## 🛠️ 技术栈 (Tech Stack)

- **核心算法**：PyTorch, Transformers, SciPy
- **后端服务**：Python, Flask, Flask-CORS
- **前端交互**：Vue 3, Vite, Tailwind CSS, Axios

## 🚀 快速启动 (Quick Start)

### 1. 启动后端 (Flask)
请确保你的电脑已安装 Python 3.8+ 及相关依赖环境。
```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 启动服务 (默认运行在 [http://127.0.0.1:5000](http://127.0.0.1:5000))
python app.py