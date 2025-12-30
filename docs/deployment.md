# Koda 部署文档

## 📋 环境要求

### 1. Python环境
- **Python版本**: 3.10 或更高
- **推荐使用**: Anaconda 或 uv 进行环境管理

### 2. LaTeX环境
根据您的操作系统安装以下LaTeX发行版之一：

| 操作系统 | 推荐发行版 | 下载链接 |
|---------|-----------|---------|
| Windows | TeX Live  | https://tug.org/texlive/ |
| macOS   | MacTeX    | https://tug.org/mactex/ |
| Linux   | TeX Live  | `sudo apt install texlive-full` |

**验证安装**：
```bash
# 检查 latexmk 是否可用
latexmk --version

# 如果没有 latexmk，检查 pdflatex
pdflatex --version
```

### 3. LLM API密钥
需要以下至少一种API密钥：
- **OpenAI API Key**: https://platform.openai.com/api-keys
- **Anthropic API Key**: https://console.anthropic.com/

---

## 🚀 安装步骤

### 方法一：使用 pip（推荐）

```bash
# 1. 克隆或下载项目
cd Koda

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv

# Windows 激活
venv\Scripts\activate

# macOS/Linux 激活
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 方法二：使用 uv（更快）

```bash
# 1. 安装 uv（如果还没有）
pip install uv

# 2. 创建虚拟环境并安装依赖
uv venv
uv pip install -r requirements.txt

# 3. 激活环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

---

## ⚙️ 配置

编辑 `config.yaml` 文件：

```yaml
app:
  default_template: "assets/templates/example_template.tex"  # 默认模板路径
  workspace_root: "workspace"  # 工作目录
  runs_root: "runs"           # 运行日志目录

llm:
  provider: "openai"          # 或 "anthropic"
  api_key: "YOUR_API_KEY_HERE"  # 替换为您的API密钥
  model: "gpt-4o"             # OpenAI模型，或 "claude-3-5-sonnet-20241022" for Anthropic
  base_url: ""                # 可选，自定义API端点
  temperature: 0.2
  max_tokens: 4000

latex:
  compiler: "latexmk"         # 或 "pdflatex"
  compiler_path: ""           # 可选，编译器完整路径

pdf:
  render_dpi: 150             # PDF预览分辨率
```

### 配置说明

#### LLM配置
- **OpenAI示例**:
  ```yaml
  llm:
    provider: "openai"
    api_key: "sk-proj-xxxxx"
    model: "gpt-4o"
  ```

- **Anthropic示例**:
  ```yaml
  llm:
    provider: "anthropic"
    api_key: "sk-ant-xxxxx"
    model: "claude-3-5-sonnet-20241022"
  ```

- **自定义API端点**（如使用代理）:
  ```yaml
  llm:
    provider: "openai"
    api_key: "your-key"
    model: "gpt-4o"
    base_url: "https://your-proxy-domain.com/v1"
  ```

---

## 🎯 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

---

## 📝 准备Beamer模板

### 使用示例模板
项目已包含一个示例模板：`assets/templates/example_template.tex`

### 使用自己的模板
1. 准备您的Beamer模板（只包含导言区，不包含 `\begin{document}`）
2. 将模板文件放在 `assets/templates/` 目录
3. 在 `config.yaml` 中更新 `default_template` 路径

**模板示例结构**：
```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{Madrid}
\usepackage{graphicx}
% ... 其他包和设置 ...

\title{论文标题}
\author{作者}
\institute{机构}
\date{\today}

% 不要包含 \begin{document} ！
```

---

## ⚠️ 常见问题

### 1. LaTeX编译失败
**问题**: "PDF not generated" 错误
**解决**:
```bash
# 检查编译器是否可用
latexmk --version

# 如果 latexmk 不可用，修改 config.yaml:
latex:
  compiler: "pdflatex"
```

### 2. API调用失败
**问题**: "openai.AuthenticationError" 或 "anthropic.AuthenticationError"
**解决**:
- 检查 `config.yaml` 中的 `api_key` 是否正确
- 确认API密钥有效且有足够余额

### 3. 找不到arXiv论文
**问题**: "arXiv ID not found"
**解决**:
- 检查arXiv ID格式是否正确（如 `2312.12345`）
- 确认论文在arXiv上存在且提供了LaTeX源码

### 4. 依赖安装失败
**问题**: PyMuPDF安装失败
**解决**:
```bash
# Windows
pip install PyMuPDF --upgrade

# macOS (可能需要)
brew install mupdf

# Linux
sudo apt-get install mupdf mupdf-tools
```

---

## 🔧 高级配置

### 自定义Prompt
编辑 `assets/AGENTS.md` 文件以自定义AI生成的风格和要求。

### 调整PDF渲染质量
在 `config.yaml` 中修改 `render_dpi`:
- 低质量（快速）: 100
- 中等质量: 150 (默认)
- 高质量: 300

---

## 📂 项目结构说明

```
Koda/
├── app.py                 # Streamlit主应用
├── config.yaml            # 配置文件
├── requirements.txt       # Python依赖
├── core/                  # 核心功能模块
│   ├── fetcher.py         # arXiv下载
│   ├── parser.py          # LaTeX解析
│   ├── generator.py       # LLM调用
│   └── compiler.py        # LaTeX编译
├── utils/                 # 工具函数
│   └── pdf_renderer.py    # PDF渲染
├── assets/
│   ├── AGENTS.md          # AI Prompt模板
│   └── templates/         # Beamer模板库
├── workspace/             # 临时工作目录（自动生成）
└── runs/                  # 运行日志（自动生成）
```

---

## 📞 获取帮助

如果遇到问题：
1. 检查 `runs/` 目录下的日志文件
2. 查看终端输出的错误信息
3. 确认所有环境要求都已满足
