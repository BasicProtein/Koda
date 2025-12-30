import json
import time
from pathlib import Path

import streamlit as st
import yaml

from core.fetcher import fetch_arxiv_source
from core.parser import extract_frames, flatten_latex_tree
from core.generator import fix_single_frame, generate_beamer_body
from core.compiler import compile_latex
from utils.pdf_renderer import render_pdf_pages


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def ensure_dirs(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)


def apply_apple_design():
    """应用纯正的Apple设计风格"""
    st.markdown("""
    <style>
    /* Apple SF Pro 字体栈 */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", 
                     "Helvetica Neue", Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* 全局背景 - Apple风格的浅灰 */
    .main {
        background: #F5F5F7;
        padding: 2rem;
    }
    
    /* 主标题 - Apple风格 */
    h1 {
        font-size: 3rem;
        font-weight: 600;
        color: #1D1D1F;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    /* 副标题 */
    .subtitle {
        font-size: 1.25rem;
        color: #86868B;
        font-weight: 400;
        margin-bottom: 3rem;
        letter-spacing: -0.01em;
    }
    
    /* 侧边栏 - Apple风格的毛玻璃 */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.72);
        backdrop-filter: saturate(180%) blur(20px);
        border-right: none;
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.04);
    }
    
    [data-testid="stSidebar"] h2 {
        color: #1D1D1F;
        font-weight: 600;
        font-size: 1.375rem;
        margin-bottom: 1.5rem;
        letter-spacing: -0.01em;
    }
    
    /* 输入框 - Apple风格 */
    .stTextInput input, .stNumberInput input {
        border: 1px solid #D2D2D7;
        border-radius: 8px;
        padding: 0.625rem 0.875rem;
        font-size: 1rem;
        transition: all 0.2s ease;
        background: #FFFFFF;
        color: #1D1D1F;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
        outline: none;
    }
    
    .stTextInput input::placeholder, .stNumberInput input::placeholder {
        color: #86868B;
    }
    
    /* Label文字 */
    .stTextInput label, .stNumberInput label {
        color: #1D1D1F;
        font-weight: 500;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    /* 按钮 - 纯正Apple风格 */
    .stButton button {
        background: #007AFF;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
        letter-spacing: -0.01em;
    }
    
    .stButton button:hover {
        background: #0051D5;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton button:active {
        background: #004FC4;
        transform: scale(0.98);
    }
    
    /* 次要按钮 */
    .secondary-button button {
        background: #F5F5F7;
        color: #1D1D1F;
        border: 1px solid #D2D2D7;
    }
    
    .secondary-button button:hover {
        background: #E8E8ED;
    }
    
    /* 卡片 - Apple风格 */
    .card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 
                    0 1px 2px rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    /* 扩展框 - Apple风格 */
    .streamlit-expanderHeader {
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        font-weight: 500;
        color: #1D1D1F;
        padding: 0.875rem 1rem;
        font-size: 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: #F5F5F7;
    }
    
    /* 文本区域 */
    .stTextArea textarea {
        border: 1px solid #D2D2D7;
        border-radius: 8px;
        padding: 0.875rem;
        font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        background: #FFFFFF;
        color: #1D1D1F;
    }
    
    .stTextArea textarea:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
        outline: none;
    }
    
    /* 成功提示 - Apple绿 */
    .stSuccess {
        background: #E8F5E9;
        border-radius: 8px;
        padding: 0.875rem 1rem;
        border-left: 3px solid #34C759;
        color: #1D1D1F;
    }
    
    /* 错误提示 - Apple红 */
    .stError {
        background: #FFEBEE;
        border-radius: 8px;
        padding: 0.875rem 1rem;
        border-left: 3px solid #FF3B30;
        color: #1D1D1F;
    }
    
    /* 警告提示 - Apple橙 */
    .stWarning {
        background: #FFF3E0;
        border-radius: 8px;
        padding: 0.875rem 1rem;
        border-left: 3px solid #FF9500;
        color: #1D1D1F;
    }
    
    /* 信息提示 - Apple蓝 */
    .stInfo {
        background: #E3F2FD;
        border-radius: 8px;
        padding: 0.875rem 1rem;
        border-left: 3px solid #007AFF;
        color: #1D1D1F;
    }
    
    /* 滑块 - Apple风格 */
    .stSlider [data-baseweb="slider"] {
        padding: 0 0.5rem;
    }
    
    .stSlider [role="slider"] {
        background: #007AFF;
        width: 20px;
        height: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    
    .stSlider [data-baseweb="slider"] [data-testid="stTickBar"] {
        background: #D2D2D7;
    }
    
    /* 图片容器 */
    .stImage {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* 分隔线 */
    hr {
        border: none;
        height: 1px;
        background: #D2D2D7;
        margin: 2rem 0;
    }
    
    /* Code块 */
    code {
        background: #F5F5F7;
        border: 1px solid #D2D2D7;
        border-radius: 4px;
        padding: 0.125rem 0.375rem;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 0.875rem;
        color: #1D1D1F;
    }
    
    /* Status容器 */
    [data-testid="stStatusWidget"] {
        background: #FFFFFF;
        border: 1px solid #D2D2D7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* 页脚 */
    .footer {
        text-align: center;
        color: #86868B;
        font-size: 0.875rem;
        margin-top: 3rem;
        padding: 1rem 0;
    }
    
    .footer a {
        color: #007AFF;
        text-decoration: none;
        transition: opacity 0.2s ease;
    }
    
    .footer a:hover {
        opacity: 0.7;
    }
    
    /* 移除Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: #86868B;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: #FFFFFF;
        color: #007AFF;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }
    
    /* 数字输入框的spinner按钮 */
    .stNumberInput button {
        color: #86868B;
    }
    
    .stNumberInput button:hover {
        color: #007AFF;
    }
    </style>
    """, unsafe_allow_html=True)


def main() -> None:
    # 页面配置
    st.set_page_config(
        page_title='Koda',
        page_icon='🎯',
        layout='wide',
        initial_sidebar_state='expanded'
    )
    
    # 应用Apple设计
    apply_apple_design()
    
    # 主标题
    st.markdown('<h1>Koda</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI Academic Presentation Generator</p>', unsafe_allow_html=True)
    
    cfg = load_config('config.yaml')
    workspace_root = Path(cfg['app']['workspace_root'])
    runs_root = Path(cfg['app']['runs_root'])
    ensure_dirs(workspace_root)
    ensure_dirs(runs_root)

    # 侧边栏
    with st.sidebar:
        st.markdown('## Configuration')
        st.markdown('')
        
        # arXiv ID
        arxiv_id = st.text_input(
            'arXiv ID',
            value='',
            placeholder='2312.12345',
            help='Enter the arXiv paper ID'
        )
        
        # 模板路径
        template_path = st.text_input(
            'Template Path',
            value=cfg['app'].get('default_template', 'assets/templates/example_template.tex'),
            placeholder='assets/templates/example_template.tex',
            help='Path to your Beamer template file'
        )
        
        # 运行名称
        run_name = st.text_input(
            'Run Name',
            value=time.strftime('%Y%m%d_%H%M%S'),
            help='Identifier for this run'
        )
        
        st.markdown('')
        
        # 生成按钮
        compile_btn = st.button('Generate Presentation', use_container_width=True)
        
        st.markdown('---')
        st.info('Make sure API key is configured in config.yaml')

    # 主内容区 - 两栏布局
    left, right = st.columns([0.5, 0.5])

    if compile_btn:
        if not arxiv_id:
            st.error('Please enter an arXiv ID')
            return
            
        run_dir = runs_root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        work_dir = workspace_root / run_name
        work_dir.mkdir(parents=True, exist_ok=True)

        with left:
            st.markdown('### Generation Log')
            st.markdown('')
            
            # 步骤1: 获取源码
            with st.status('Fetching arXiv source...', expanded=True) as status:
                try:
                    src_dir = fetch_arxiv_source(arxiv_id, work_dir)
                    status.update(label='Source downloaded successfully', state='complete')
                    st.success(f'Downloaded to: `{src_dir}`')
                except Exception as exc:
                    status.update(label='Download failed', state='error')
                    st.error(f'Failed to fetch source: {exc}')
                    return

            # 步骤2: 解析LaTeX
            with st.status('Parsing LaTeX files...', expanded=True) as status:
                try:
                    paper_tex = flatten_latex_tree(src_dir)
                    status.update(label='LaTeX parsed successfully', state='complete')
                    st.success(f'Flattened {len(paper_tex):,} characters')
                except Exception as exc:
                    status.update(label='Parsing failed', state='error')
                    st.error(f'Failed to parse LaTeX: {exc}')
                    return

            # 步骤3: AI生成
            with st.status('Generating Beamer content...', expanded=True) as status:
                try:
                    body_tex = generate_beamer_body(paper_tex, Path('assets/AGENTS.md'), cfg, run_dir)
                    status.update(label='Beamer generated successfully', state='complete')
                    st.success(f'Generated {len(body_tex):,} characters')
                except Exception as exc:
                    status.update(label='Generation failed', state='error')
                    st.error(f'LLM call failed: {exc}')
                    return
                    
            talk_tex = work_dir / 'talk.tex'
            talk_tex.write_text(body_tex, encoding='utf-8')

            # 步骤4: 编译PDF
            with st.status('Compiling PDF...', expanded=True) as status:
                try:
                    pdf_path = compile_latex(talk_tex, template_path, work_dir, cfg)
                    status.update(label='PDF compiled successfully', state='complete')
                    st.success(f'PDF generated: `{pdf_path.name}`')
                except Exception as exc:
                    status.update(label='Compilation failed', state='error')
                    st.error(f'LaTeX compilation failed: {exc}')
                    return

            # 保存元数据
            meta = {
                'arxiv_id': arxiv_id,
                'template_path': template_path,
                'run_name': run_name,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            (run_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

            st.session_state['body_tex'] = body_tex
            st.session_state['work_dir'] = str(work_dir)
            st.session_state['run_name'] = run_name
            st.session_state['pdf_path'] = str(pdf_path)

        with right:
            st.markdown('### PDF Preview')
            st.markdown('')
            
            if 'pdf_path' in st.session_state:
                try:
                    pages = render_pdf_pages(Path(st.session_state['pdf_path']), dpi=cfg['pdf']['render_dpi'])
                    
                    page_count = len(pages)
                    st.info(f'Total pages: {page_count}')
                    
                    # 页面选择器
                    page_num = st.slider('Page', 1, page_count, 1, label_visibility='collapsed')
                    
                    # 显示选中的页面
                    st.image(
                        pages[page_num - 1],
                        use_container_width=True,
                        caption=f'Page {page_num} of {page_count}'
                    )
                    
                except Exception as exc:
                    st.error(f'PDF preview failed: {exc}')

    # 修复单页功能
    if 'body_tex' in st.session_state:
        st.markdown('---')
        with st.expander('Fix Individual Frame', expanded=False):
            body_tex = st.session_state['body_tex']
            frames = extract_frames(body_tex)
            max_frame = max(len(frames), 1)

            col1, col2 = st.columns([1, 3])
            
            with col1:
                frame_index = st.number_input(
                    'Frame Number',
                    min_value=1,
                    max_value=max_frame,
                    value=1,
                    help='Select frame to fix (1-indexed)'
                )
            
            with col2:
                current_frame = frames[frame_index - 1] if frames else ''
                st.code(current_frame, language='latex', line_numbers=True)

            frame_text = st.text_area(
                'Edit LaTeX Code',
                value=current_frame,
                height=300,
                help='Edit manually or use AI to fix automatically'
            )

            if st.button('Auto Fix Frame', use_container_width=True):
                run_dir = runs_root / st.session_state.get('run_name', run_name)
                
                with st.spinner('Fixing frame...'):
                    try:
                        fixed = fix_single_frame(frame_text, Path('assets/AGENTS.md'), cfg, run_dir, frame_index)
                        fixed = fixed.replace('\\begin{document}', '').replace('\\end{document}', '').strip()
                        
                        if frames:
                            frames[frame_index - 1] = fixed
                            new_body = body_tex
                            if current_frame in new_body:
                                new_body = new_body.replace(current_frame, fixed, 1)
                            else:
                                new_body = new_body.replace(frame_text, fixed, 1)
                        else:
                            new_body = fixed

                        st.session_state['body_tex'] = new_body
                        work_dir = Path(st.session_state['work_dir'])
                        talk_tex = work_dir / 'talk.tex'
                        talk_tex.write_text(new_body, encoding='utf-8')

                        # 重新编译
                        pdf_path = compile_latex(talk_tex, template_path, work_dir, cfg)
                        st.session_state['pdf_path'] = str(pdf_path)

                        st.success('Frame fixed and recompiled successfully')
                        st.rerun()
                        
                    except Exception as exc:
                        st.error(f'Fix failed: {exc}')

    # 页脚
    st.markdown('---')
    st.markdown(
        '<div class="footer">'
        'Koda · AI Academic Presentation Generator · '
        '<a href="https://github.com/BasicProtein/Koda">GitHub</a>'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()
