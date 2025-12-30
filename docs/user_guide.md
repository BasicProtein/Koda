# Koda 使用指南

## 📖 快速开始

Koda 帮助您自动从 arXiv 论文生成学术组会 PPT（Beamer 格式）。完整工作流程：

```
arXiv论文ID → 下载LaTeX源码 → AI生成Beamer → 编译PDF → 逐页修复溢出
```

---

## 🎬 基本使用流程

### 第一步：启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 Koda 界面。

### 第二步：准备工作

在左侧边栏输入以下信息：

| 字段 | 说明 | 示例 |
|-----|------|------|
| **arXiv ID** | 论文的arXiv编号 | `2312.12345` |
| **Template path** | Beamer模板路径 | `assets/templates/example_template.tex` |
| **Run name** | 本次运行的名称 | `paper_talk_20241230` |

### 第三步：生成PPT

点击 **"Generate + Compile"** 按钮，系统会自动：

1. ✅ 从arXiv下载论文LaTeX源码
2. ✅ 解析并扁平化LaTeX文件树
3. ✅ 调用LLM生成Beamer正文
4. ✅ 编译生成PDF
5. ✅ 在右侧显示PDF预览

**⏱️ 时间估计**:
- 下载源码：10-30秒
- LLM生成：30-120秒（取决于模型）
- 编译PDF：5-15秒
- **总计约1-3分钟**

### 第四步：修复溢出页面

生成后，如果发现某些页面内容溢出：

1. 展开 **"Fix Single Frame"** 区域
2. 输入要修复的页面编号（从1开始）
3. 查看/编辑该页的LaTeX代码
4. 点击 **"Auto Fix This Frame"**
5. AI会自动修复该页（可能拆分成多页）
6. 重新编译并预览

---

## 💡 实战示例

### 示例1：生成Vision Transformer论文的PPT

假设您要做 "An Image is Worth 16x16 Words" 这篇论文的分享：

1. **找到arXiv ID**: `2010.11929`
2. **填写信息**:
   - arXiv ID: `2010.11929`
   - Template path: `assets/templates/example_template.tex`
   - Run name: `vit_paper_2024`
3. **点击生成**
4. **等待1-2分钟**
5. **查看结果**，右侧会显示生成的PPT预览

### 示例2：修复第5页的溢出

假设生成后发现第5页公式太多，内容溢出：

1. 展开 "Fix Single Frame"
2. Frame index 输入: `5`
3. 查看文本框中显示的第5页LaTeX代码
4. 点击 "Auto Fix This Frame"
5. AI会自动：
   - 减少bullet数量
   - 拆分公式
   - 或将该页拆分为"Methodology II"和"Methodology III"

---

## 🎯 最佳实践

### 1. 选择合适的论文

✅ **推荐**：
- 在arXiv上有LaTeX源码的论文
- 方法型论文（有公式、算法、实验）
- 近期发表的论文（LaTeX格式更标准）

❌ **不推荐**：
- 只有PDF的论文（无法获取LaTeX）
- 纯理论证明的论文（公式过于密集）
- 过老的论文（LaTeX格式可能不兼容）

### 2. 准备好模板

**自定义模板的要点**：
- 只包含导言区（`\documentclass` 到 `\begin{document}` 之前）
- 不要有 `\begin{document}` 和 `\end{document}`
- 确保包含 `graphicx`, `amsmath`, `booktabs` 等常用包
- 设置好 `\title`, `\author`, `\institute`

**示例模板头部**：
```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{Madrid}
\usecolortheme{beaver}

\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}

\title{Your Paper Title}
\author{Your Name}
\institute{Your Institution}
\date{\today}
```

### 3. 理解生成的结构

AI会按照以下结构生成PPT：

```
1. Title Page（标题页）
2. Motivation & Problem（动机与问题定义）
3. Methodology I/II/III...（方法，拆分多页）
4. Experiments - Setup（实验设置）
5. Experiments - Main Results（主要结果）
6. Experiments - Ablation（消融实验）
7. Conclusion（结论）
```

每页通常使用 **两栏布局**：
- 左栏：要点（bullet points）
- 右栏：图/表（占位符）

### 4. 高效修复溢出

**常见溢出原因**：
1. Bullet点太多（超过7条）
2. 公式太长
3. 表格太宽
4. 图片太大

**AI自动修复策略**：
1. **拆页**（最优）：将一页拆成两页
2. **简化**：减少bullet、删除次要信息
3. **缩放**：适度调整字号或图片大小
4. **重排**：优化columns布局

---

## 📁 生成文件说明

每次运行后，会在以下目录生成文件：

### `workspace/<run_name>/`
工作目录，包含：
- `paper_src/`: 下载的论文LaTeX源码
- `talk.tex`: 生成的Beamer正文
- `main.tex`: 组合后的完整LaTeX（模板+正文）
- `main.pdf`: 最终编译的PDF
- 其他LaTeX编译产物（`.aux`, `.log`, `.out`等）

### `runs/<run_name>/`
日志目录，包含：
- `meta.json`: 运行元数据（arXiv ID、模板路径等）
- `input_paper.tex`: 输入给LLM的论文内容
- `prompt.txt`: 完整的LLM提示词
- `output_body.tex`: LLM原始输出
- `fix_prompt_001.txt`: 第1次修复的提示词
- `fix_output_001.tex`: 第1次修复的输出
- ... （后续修复）

**💡 提示**：这些日志对调试和复现非常有用！

---

## 🔄 工作流进阶技巧

### 技巧1：本地编辑后重新编译

如果您想手动编辑生成的LaTeX：

1. 找到 `workspace/<run_name>/talk.tex`
2. 用文本编辑器打开并修改
3. 在 `workspace/<run_name>/` 目录下手动编译：
   ```bash
   latexmk -pdf main.tex
   ```

### 技巧2：批量生成多篇论文

创建一个脚本批量处理：
```python
import subprocess

papers = [
    ('2010.11929', 'vit'),
    ('2103.14030', 'beit'),
    # 添加更多...
]

for arxiv_id, name in papers:
    # 修改config.yaml或通过API调用
    # 运行生成流程
    pass
```

### 技巧3：自定义AGENTS.md提示词

如果您想要不同的生成风格：

1. 打开 `assets/AGENTS.md`
2. 修改约束规则，例如：
   - 改变每页bullet数量限制
   - 调整图表位置偏好
   - 修改语言风格（正式/轻松）
3. 保存后重新生成

**示例修改**：
```markdown
# 原始
- **Max 5-7 bullet points** per slide.

# 修改为更简洁
- **Max 3-5 bullet points** per slide.
```

---

## 🎨 定制化输出

### 修改标题页信息

在模板中设置：
```latex
\title[会议简称]{完整论文标题}
\subtitle{副标题}
\author[姓名]{姓名 \inst{1}}
\institute{\inst{1} 单位名称}
\date{2024年12月}
```

### 添加自定义图片

生成后手动替换占位符：
1. 找到 `\includegraphics{fig_architecture.png}`
2. 将真实图片放入 `workspace/<run_name>/` 目录
3. 重新编译

### 使用不同主题

在模板中尝试其他Beamer主题：
```latex
\usetheme{Berlin}      % 经典主题
\usetheme{Copenhagen}  % 简洁主题
\usetheme{Boadilla}    % 适合学术报告
```

---

## ⚡ 性能优化

### 减少Token消耗

1. **简化论文源码**：如果论文很长，可手动删除无关章节（如附录）
2. **使用更便宜的模型**：从 `gpt-4o` 降级到 `gpt-4o-mini`
3. **调整max_tokens**：如果PPT不需要太详细，降低到2000

### 加快生成速度

1. **使用更快的模型**：`claude-3-haiku` 或 `gpt-3.5-turbo`
2. **并行处理**：如果有多篇论文，使用多线程
3. **本地缓存**：已下载的论文源码会缓存，避免重复下载

---

## ❓ 常见问题

### Q1: 生成的PPT内容不够详细？
**A**: 修改 `config.yaml` 中的 `max_tokens`，增加到6000-8000。同时在 `assets/AGENTS.md` 中强调"详细"。

### Q2: AI生成的公式有错误？
**A**: 通常是LaTeX解析问题。检查：
1. 论文源码是否完整
2. 是否有特殊的自定义宏
解决：在"Fix Single Frame"中手动修正该页。

### Q3: 编译时缺少宏包？
**A**: 确保您的LaTeX发行版是完整安装（`texlive-full`）。如果缺少特定包：
```bash
# TeX Live
tlmgr install <package-name>

# MiKTeX
mpm --install <package-name>
```

### Q4: PDF预览显示不出来？
**A**: 检查：
1. PDF是否成功生成（查看 `workspace/<run_name>/main.pdf`）
2. PyMuPDF是否正确安装：`pip install --upgrade PyMuPDF`

### Q5: 如何处理非英文论文？
**A**: 确保：
1. 模板支持相应语言（如中文需要 `\usepackage{ctex}`）
2. 编译器使用 `xelatex` 而非 `pdflatex`
3. 在 `config.yaml` 中设置：
   ```yaml
   latex:
     compiler: "xelatex"
   ```

---

## 📚 延伸阅读

- [Beamer用户手册](https://ctan.org/pkg/beamer)
- [arXiv LaTeX指南](https://arxiv.org/help/submit_tex)
- [Streamlit文档](https://docs.streamlit.io/)

---

## 🎓 典型使用场景

1. **博士组会**: 详细技术分享，保留完整公式
2. **实验室内部讨论**: 深入方法细节和消融分析
3. **快速原型**: 快速了解新论文的核心思路
4. **教学辅助**: 生成课程讲义的初稿

---

祝您使用愉快！🚀
