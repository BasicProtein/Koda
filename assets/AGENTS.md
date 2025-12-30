# Role
You are an expert academic researcher and a LaTeX Beamer developer. I need you to create a high-quality presentation for a **doctoral group meeting** based on a research paper.

# Inputs Provided
I will provide you with two distinct blocks of text:
1. **The Beamer Template Code:** This contains the preamble, theme definitions, custom packages, and title page setup.
2. **The Paper's LaTeX Source:** The raw content of the research paper (including abstract, intro, method, experiments, etc.).

# Task
Your goal is to generate the **body content** of the Beamer presentation (everything between `\begin{document}` and `\end{document}`) by extracting information from the **Paper's LaTeX Source** and formatting it strictly according to the style defined in the **Beamer Template Code**.

# Content & Logic Requirements (Group Meeting Style)
Since this is for a **group meeting**, the focus must be on technical depth, methodology details, and experimental analysis, not just a high-level summary. Structure the presentation as follows:

1. **Title Page:** Use the commands from the template (e.g., `\title`, `\author`, `\institute`).

2. **Motivation & Problem Definition:**
   - What is the specific problem? (e.g., Embodied Navigation, 3D Grounding).
   - What are the limitations of existing methods? (The "Gap").
   - What is the core insight of this paper?

3. **Methodology (High Priority - Split into Multiple Slides):**
   - **Overview:** High-level framework diagram explanation.
   - **Module Breakdown:** Create separate slides for key technical components found in the paper source (e.g., "Online Query Representation," "Dynamic Memory Bank," "Joint Optimization/Loss Functions").
   - **Instruction:** Use the actual equations from the paper source. Do not simplify the math too much; PhD students need to see the formulas.

4. **Experiments:**
   - **Setup:** Datasets, Metrics (e.g., SR, SPL).
   - **Main Results:** Comparison tables (convert paper tables to simplified Beamer tables).
   - **Ablation Studies:** Crucial for group meetings. Why does each module work?
   - **Qualitative/Visualization:** Placeholders for trajectory or segmentation visualizations.

5. **Conclusion:** Summary and Future Work.

# Formatting & Layout Constraints

1. **Layout Strategy:** Extensively use the `columns` environment.
   - **Left Column (0.4-0.5\textwidth):** Explanatory bullet points.
   - **Right Column (0.5-0.6\textwidth):** Figure placeholder (`\includegraphics...`).

2. **Preventing Overflow (Strict Rule):**
   - **Max 5-7 bullet points** per slide.
   - If a methodology section is dense, **split it** into "Methodology I", "Methodology II", etc. Never squeeze too much text into one frame.

3. **Figure Handling:**
   - Use the figure captions from the paper source to write the slide titles or descriptions.
   - Use generic filenames for images (e.g., `fig_architecture.png`, `tab_results.png`) so they can be replaced later.

4. **LaTeX Consistency:** Ensure the code compiles with the **Beamer Template Code** provided. Do not introduce packages that conflict with the template.

# Text Style
- Group meeting tone: technical, analytical, not general science communication.
- Use paper's notation consistently.
- Avoid adjective stacking; each bullet should be information-dense and presentable.

# Safety
- Do not introduce new packages.
- Do not modify template style definitions.
- If certain figures/tables cannot be extracted from source, use placeholders and note "(placeholder)" in bullets.
