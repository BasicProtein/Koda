我想做一个项目：有了 codex 和 cc 之后，我现在做科研论文分享 PPT 基本是“流水线”：下载 arXiv LaTeX 源码 → 丢进模板文件夹 → 让 Codex/cc 直接生成 Beamer 正文 → 编译 → 逐页修溢出。
优点很直白：几乎不用手工搬公式/表格/图注，初稿出来就有“论文味”，最后只做边界检查和少量排版。

0. 适用范围
适用：

论文在 arXiv 上，能下到 LaTeX source（强烈建议别用 PDF 去抠）
你有一份常用 Beamer 模板（实验室模板/公开模板都行）
你想要“组会风格”：方法细、公式全、实验+消融讲清楚
电脑可以编译 latex
1. 建一个干净的工作目录（建议每篇论文一个文件夹）
每篇论文我都会单独开一个文件夹，把两样东西放到一起就行：arXiv 的 LaTeX 源码（解压后）+ 你的 Beamer 模板（template.tex）。

paper-talk/
  AGENTS.md              # 固定的 prompt（下面给一份可复制完整版）
  template.tex           # beamer 模板
  paper_src/             # 论文 LaTeX 源码（解压后）
  talk.tex               # 最终 slides（或 talk_body.tex 由模型生成后再 include）
  figs/                  # 你后续替换/截图出来的图（可选）
2. 让 Codex / Claude 生成初稿（我用的prompt）
一般思路是：让它读取：

template.tex
paper_src/ 里论文 tex（主入口 + 相关 section）
然后输出：

talk.tex（或 talk_body.tex）里 \begin{document} 到 \end{document} 的正文
你可以直接对模型说类似这种（口吻随意，关键是约束）：

按 AGENTS.md 的规则，读取 template.tex 和 paper_src/ 的论文 LaTeX 源码，生成 Beamer 正文（只输出 document 环境内容），方法部分保留原公式，实验给主结果+消融表，整套按 columns 排版并避免一页太挤。
AGENTS.md# Role
你是资深学术组会 PPT（LaTeX Beamer）开发者。目标是为博士组会生成技术型分享：方法细、公式全、实验/消融讲清楚。# Inputs (Files in this folder)- Beamer 模板：`template.tex`（包含 preamble/theme/title page 等风格定义）- 论文 LaTeX 源码目录：`paper_src/`（包含论文正文、公式、表格、图注）# Output (Strict)- 只生成 Beamer 正文：仅输出 `\begin{document}` 到 `\end{document}` 之间的内容- 不要输出解释性文字、不要输出模板 preamble、不要新增可能冲突的宏包- 输出必须可编译（在既有模板下）# Talk Structure (Group meeting style)1. Title Page（使用模板的标题页命令/字段）2. Motivation & Problem Definition   - 任务/问题定义（沿用论文符号）   - 现有方法限制（gap，2-3 点即可）   - 本文核心 insight（1-2 句）3. Methodology（高优先级，必须拆成多页）   - Overview：整体框架与数据流   - Module Breakdown：关键模块逐页讲清楚（输入/输出/关键设计）   - 使用论文原始公式（不要过度简化数学）   - 给出训练目标/损失函数（总 loss + 分项）4. Experiments   - Setup：数据集、指标（如 SR/SPL）、实现细节（backbone/训练设置）   - Main Results：对比表（简化成 beamer 表格）   - Ablation：消融表 + 结论解释（为什么掉/为什么提升）   - Qualitative：可视化/失败案例（用占位图）5. Conclusion   - 贡献总结（3 点内）   - 局限   - Future work# Layout Rules (MTU3D-like)- 大量使用 `columns`：  - 左列 0.45\textwidth：要点（bullet）  - 右列 0.55\textwidth：图/表（占位图或简化表格）- 每页最多 5–7 条 bullet；超过必须拆页（Method I/II/III…）- 禁止把 Method 挤成一页；宁可多页也要可读# Figures/Tables- 图片统一用占位文件名，方便用户后续替换：  - `fig_architecture.png`, `fig_module1.png`, `fig_qualitative.png`- 表格从论文表格抽取，做“能讲清结论”的简化版：  - 保留关键 baseline + 本文方法  - 保留关键指标列（如 SR/SPL/Success 等）  - 最好成绩加粗（\textbf{}）  - 列太多就删列或拆表，不要硬 resize 到看不清# Text Style- 组会口吻：偏技术、偏分析，不要写成泛泛的科普总结- 符号命名以论文为准，全文一致- 不要堆砌形容词；每条 bullet 都要“信息密度高、可讲”# Safety- 不要引入新的宏包- 不要改动模板风格定义- 如果某些图/表无法从源码直接得到，就放占位并在 bullet 里注明“(placeholder)”
AGENTS.md# Role
You are an expert academic researcher and a LaTeX Beamer developer. I need you to create a high-quality presentation for a **doctoral group meeting** based on a research paper.# Inputs Provided
I will provide you with two distinct blocks of text:1.  **The Beamer Template Code:** This contains the preamble, theme definitions, custom packages, and title page setup.2.  **The Paper's LaTeX Source:** The raw content of the research paper (including abstract, intro, method, experiments, etc.).# Task
Your goal is to generate the **body content** of the Beamer presentation (everything between `\begin{document}` and `\end{document}`) by extracting information from the **Paper's LaTeX Source** and formatting it strictly according to the style defined in the **Beamer Template Code**.# Content & Logic Requirements (Modeled after "MTU3D" Logic)
Since this is for a **group meeting**, the focus must be on technical depth, methodology details, and experimental analysis, not just a high-level summary. Structure the presentation as follows:1.  **Title Page:** Use the commands from my template (e.g., `\title`, `\author`, `\institute`).2.  **Motivation & Problem Definition:**    * What is the specific problem? (e.g., Embodied Navigation, 3D Grounding).    * What are the limitations of existing methods? (The "Gap").    * What is the core insight of this paper?3.  **Methodology (High Priority - Split into Multiple Slides):**    * **Overview:** High-level framework diagram explanation.    * **Module Breakdown:** Create separate slides for key technical components found in the paper source (e.g., "Online Query Representation," "Dynamic Memory Bank," "Joint Optimization/Loss Functions").    * *Instruction:* Use the actual equations from the paper source. Do not simplify the math too much; PhD students need to see the formulas.4.  **Experiments:**    * **Setup:** Datasets, Metrics (e.g., SR, SPL).    * **Main Results:** Comparison tables (convert paper tables to simplified Beamer tables).    * **Ablation Studies:** Crucial for group meetings. Why does each module work?    * **Qualitative/Visualization:** Placeholders for trajectory or segmentation visualizations.5.  **Conclusion:** Summary and Future Work.# Formatting & Layout Constraints1.  **Layout Strategy:** Mimic the "MTU3D" style by extensively using the `columns` environment.    * **Left Column (0.4-0.5\textwidth):** Explanatory bullet points.    * **Right Column (0.5-0.6\textwidth):** Figure placeholder (`\includegraphics...`).2.  **Preventing Overflow (Strict Rule):**    * **Max 5-7 bullet points** per slide.    * If a methodology section is dense, **split it** into "Methodology I", "Methodology II", etc. Never squeeze too much text into one frame.3.  **Figure Handling:**    * Use the figure captions from the paper source to write the slide titles or descriptions.    * Use generic filenames for images (e.g., `fig_architecture.png`, `tab_results.png`) so I can replace them later.4.  **LaTeX Consistency:** Ensure the code compiles with the **Beamer Template Code** I provided. Do not introduce packages that conflict with my template.
3. 逐页修溢出：我一般只让模型改“这一页”
最省事的交互方式：把出问题的 frame 原样贴给模型，让它只改这一页（必要时拆成两页）。
我常用的修边prompt长这样：

“下面这个 frame #number 溢出了。只改这一页：最多 6 条 bullet；允许拆成两页；公式符号保持论文一致；表格不要 resize 太狠。输出替换后的 frame 代码。”
然后贴：

该 frame 的 LaTeX
log 里 Overfull 提示那一行（可选）
常用修法（按优先级）：

拆页（Method II/III、Ablation I/II）——最稳
表格：删列/删行/拆表（比 \resizebox 更可读）
公式：align 断行、把 “where …” 放 bullet 里
字号：只对局部 \small/\scriptsize（别全局缩，观感很惨）
图：右栏图缩一点，或者减少一张图
4. 结尾：这套流程我觉得值的点
arXiv 源码是最干净的信息源：公式/表格/图注本来就是结构化的，模型搬运+重排比你手动快太多
AGENTS.md 把“输出形态”锁死后，模型就更像“排版工+助教”，而不是“写作文选手”
最后只剩一个工作：逐页把溢出修掉（这部分反而很好外包给模型做）
然后就可以尽情摸鱼了（甚至可以让生成一个对应的稿子，偷偷照着读）

详细的项目规划（更新版）



你说得对。兵马未动，粮草先行。如果不先把技术栈定死，后面写代码就会变成“面多了加水，水多了加面”。

针对 **Koda** 这种“文本重构 + 编译器调用 + 视觉反馈”的工具，我推荐一套**“轻量级 Python + 交互式 Web UI”**的技术栈。

这是我认为性价比最高的组合：

### 核心技术栈推荐 (The Golden Stack)

| **模块**       | **技术选型**                               | **理由**                                                     |
| -------------- | ------------------------------------------ | ------------------------------------------------------------ |
| **编程语言**   | **Python 3.10+**                           | 不二之选。拥有最强的 arXiv 库、最方便的文本处理能力，且是 LLM 调用的原生环境。 |
| **UI 框架**    | **Streamlit**                              | **关键决策点**。不要写 CLI，也不要写 Electron。 你需要一边看 PDF 预览，一边点“修复这一页”。Streamlit 可以让你用 Python 极速写出带“左侧控制台 + 右侧 PDF 预览”的界面。 |
| **LLM 交互**   | **Anthropic SDK / OpenAI SDK**             | 建议直连，**不使用** LangChain。 原因：你的 Prompt (`AGENTS.md`) 非常结构化且长，LangChain 的抽象层反而会增加调试难度。直接封装一个 `call_llm(prompt, context)` 函数最稳。 |
| **LaTeX 编译** | **Local TeXLive (latexmk 优先)**           | 必须依赖本地环境。Python 通过 `subprocess` 调用系统命令。latexmk 更稳，自动处理多次编译和引用。 |
| **PDF 处理**   | **PyMuPDF (fitz)**                         | Windows 上更省心，不依赖 poppler；可直接把 PDF 页面渲染成图片用于 Streamlit 预览。 |
| **数据源**     | **arxiv (Python Lib)**                     | 官方 API 的 Python 封装，下载源码包、获取元数据（标题、作者）非常稳。 |

------

### 详细组件与依赖分析

#### 1. 后端逻辑 (Python)

这是项目的“大脑”，负责脏活累活。

- **`arxiv`**: 用于 `search` 和 `download_source`。
- **`tarfile` & `zipfile`**: arXiv 的源码通常是 `.tar.gz`，需要自动解压。
- **`regex` (re)**: **这是核心中的核心**。你需要用正则做以下清洗：
  - 去除 LaTeX 注释 (`%` 开头的内容)，节省 Token。
  - 扁平化文件：识别 `\input{sections/intro.tex}`、`\include{...}`、`\subfile{...}`、`\import{...}`，把子文件内容读出来替换进去，把多文件合并成一个长 String 给 LLM。
  - 提取 `\begin{frame}` 到 `\end{frame}` 的块，用于后续的“单页修复”。
- **`tenacity`**: 调用 LLM 时的重试机制（网络波动是常态）。

#### 2. 用户界面 (Streamlit)

这是你的“控制台”。为什么我强烈推荐 Streamlit 而不是 CLI？

因为你的第 3 步是 “逐页修溢出”。

- **CLI 体验**：

  1. 生成代码。

  2. 打开 PDF 阅读器看一眼。

  3. 发现第 5 页炸了。

  4. 回到终端输入 python koda.py --fix-page 5。

     评价：割裂，累。

-- **Streamlit 体验**：

  - **左栏**：显示每一页生成的 LaTeX 源码（Text Area）。
  - **右栏**：显示对应页的渲染图。
  - **交互**：右边看到第 5 页溢出了 -> 左边点击“Auto Fix This Slide”按钮 -> 局部调用 LLM -> 局部重编译 -> 右侧图片自动刷新。
  - *评价：丝滑。*

#### 3. 编译环境 (System)

- 确保电脑上装了 **TeXLive** (Windows/Linux) 或 **MacTeX** (macOS)。
- 确保 `latexmk` 在系统环境变量 PATH 里（若不可用再退回 `pdflatex`）。

------

### 项目文件结构 (基于此技术栈)

基于这个技术栈，你的工程目录应该长这样：

Plaintext

```
Koda/
├── app.py                 # Streamlit 入口 (UI逻辑)
├── config.yaml            # 运行配置 (API key / 默认模板 / 编译器路径)
├── core/
│   ├── fetcher.py         # 处理 arXiv 下载、解压
│   ├── parser.py          # 处理 LaTeX 清洗、扁平化、合并
│   ├── generator.py       # 封装 LLM API (Claude/GPT)
│   └── compiler.py        # 封装 subprocess 调用 latexmk/pdflatex
├── assets/
│   ├── AGENTS.md          # 核心 Prompt (保留单一权威版本)
│   └── templates/         # Beamer 模板库
├── utils/
│   └── pdf_renderer.py    # 用 PyMuPDF 把 PDF 转图供 Streamlit 显示
├── requirements.txt       # python 依赖
├── runs/                  # 每次任务的日志与快照 (prompt/context/output)
└── workspace/             # 运行时生成的临时目录
```

### 为什么不选别的？

1. **为什么不选 PyQt/Tkinter？**
   - 开发太慢，界面太丑。你需要把精力花在 Prompt Tuning 上，而不是调整按钮的 padding。
2. **为什么不选 Web 前端 (React/Vue) + FastAPI？**
   - 杀鸡用牛刀。你是单人开发，前后端分离会增加一倍的工作量。Streamlit 是“全栈 Python”，写完逻辑界面就有了。

### 现在的行动点

如果你同意这个技术栈，我们需要做的第一件事不是写代码，而是**验证环境**。

你需要确认：

1. Python 环境就绪。
2. 本地终端能直接运行 `latexmk -pdf your_template.tex` 并成功编译（若没有 latexmk，再用 pdflatex）。
3. 拥有 OpenAI 或 Anthropic 的 API Key。

如果这三点都没问题，我们可以直接开始写 **Core 模块的 MVP**（最小可行性产品）。你觉得如何？

