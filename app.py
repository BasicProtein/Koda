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


# 多语言文本配置
TRANSLATIONS = {
    'en': {
        'title': 'Koda',
        'subtitle': 'AI Academic Presentation Generator',
        'config': 'Configuration',
        'arxiv_id': 'arXiv ID',
        'arxiv_placeholder': '2312.12345',
        'arxiv_help': 'Enter the arXiv paper ID',
        'template_path': 'Template Path',
        'template_placeholder': 'assets/templates/example_template.tex',
        'template_help': 'Path to your Beamer template file',
        'run_name': 'Run Name',
        'run_help': 'Identifier for this run',
        'generate_btn': 'Generate Presentation',
        'config_tip': 'API key configured in config.yaml',
        'generation_log': 'Generation Log',
        'pdf_preview': 'PDF Preview',
        'fetching': 'Fetching arXiv source...',
        'fetch_success': 'Source downloaded successfully',
        'fetch_failed': 'Download failed',
        'downloaded_to': 'Downloaded to:',
        'parsing': 'Parsing LaTeX files...',
        'parse_success': 'LaTeX parsed successfully',
        'parse_failed': 'Parsing failed',
        'flattened': 'Flattened',
        'characters': 'characters',
        'generating': 'Generating Beamer content...',
        'generate_success': 'Beamer generated successfully',
        'generate_failed': 'Generation failed',
        'generated': 'Generated',
        'compiling': 'Compiling PDF...',
        'compile_success': 'PDF compiled successfully',
        'compile_failed': 'Compilation failed',
        'pdf_generated': 'PDF generated:',
        'total_pages': 'Total pages:',
        'page_of': 'Page {0} of {1}',
        'preview_failed': 'PDF preview failed:',
        'fix_frame': 'Fix Individual Frame',
        'frame_number': 'Frame Number',
        'frame_help': 'Select frame to fix (1-indexed)',
        'edit_latex': 'Edit LaTeX Code',
        'edit_help': 'Edit manually or use AI to fix automatically',
        'auto_fix': 'Auto Fix Frame',
        'fixing': 'Fixing frame...',
        'fix_success': 'Frame fixed and recompiled successfully',
        'fix_failed': 'Fix failed:',
        'enter_arxiv': 'Please enter an arXiv ID',
        'failed_fetch': 'Failed to fetch source:',
        'failed_parse': 'Failed to parse LaTeX:',
        'failed_llm': 'LLM call failed:',
        'failed_compile': 'LaTeX compilation failed:',
    },
    'zh': {
        'title': 'Koda',
        'subtitle': 'AI学术演示文稿生成器',
        'config': '配置',
        'arxiv_id': 'arXiv ID',
        'arxiv_placeholder': '2312.12345',
        'arxiv_help': '输入arXiv论文的ID',
        'template_path': '模板路径',
        'template_placeholder': 'assets/templates/example_template.tex',
        'template_help': 'Beamer模板文件的路径',
        'run_name': '运行名称',
        'run_help': '本次运行的标识名称',
        'generate_btn': '生成演示文稿',
        'config_tip': 'API密钥已在config.yaml中配置',
        'generation_log': '生成日志',
        'pdf_preview': 'PDF预览',
        'fetching': '正在获取arXiv源码...',
        'fetch_success': '源码下载成功',
        'fetch_failed': '下载失败',
        'downloaded_to': '已下载到：',
        'parsing': '正在解析LaTeX文件...',
        'parse_success': 'LaTeX解析成功',
        'parse_failed': '解析失败',
        'flattened': '已扁平化',
        'characters': '个字符',
        'generating': '正在生成Beamer内容...',
        'generate_success': 'Beamer生成成功',
        'generate_failed': '生成失败',
        'generated': '已生成',
        'compiling': '正在编译PDF...',
        'compile_success': 'PDF编译成功',
        'compile_failed': '编译失败',
        'pdf_generated': 'PDF已生成：',
        'total_pages': '共{0}页',
        'page_of': '第{0}/{1}页',
        'preview_failed': 'PDF预览失败：',
        'fix_frame': '修复单个页面',
        'frame_number': '页面编号',
        'frame_help': '选择要修复的页面（从1开始）',
        'edit_latex': '编辑LaTeX代码',
        'edit_help': '可以手动编辑，或使用AI自动修复',
        'auto_fix': 'AI自动修复',
        'fixing': '正在修复页面...',
        'fix_success': '页面已修复并重新编译',
        'fix_failed': '修复失败：',
        'enter_arxiv': '请输入arXiv ID',
        'failed_fetch': '获取源码失败：',
        'failed_parse': 'LaTeX解析失败：',
        'failed_llm': 'LLM调用失败：',
        'failed_compile': 'LaTeX编译失败：',
    }
}


def get_text(key: str, lang: str = 'en') -> str:
    """获取翻译文本"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


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
    
    /* 输入框和选择框 - Apple风格 */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border: 1px solid #D2D2D7;
        border-radius: 8px;
        padding: 0.625rem 0.875rem;
        font-size: 1rem;
        transition: all 0.2s ease;
        background: #FFFFFF;
        color: #1D1D1F;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
        outline: none;
    }
    
    .stTextInput input::placeholder, .stNumberInput input::placeholder {
        color: #86868B;
    }
    
    /* Selectbox特殊样式 */
    .stSelectbox {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text";
    }
    
    .stSelectbox label {
        color: #1D1D1F;
        font-weight: 500;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        border-color: #D2D2D7;
        border-radius: 8px;
        background-color: #FFFFFF;
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
    
    # 初始化语言设置
    if 'language' not in st.session_state:
        st.session_state['language'] = 'en'
    
    lang = st.session_state['language']
    
    # 语言切换器（右上角下拉菜单）
    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        language_options = {
            'English': 'en',
            '中文': 'zh'
        }
        
        # 获取当前语言的显示名称
        current_display = [k for k, v in language_options.items() if v == lang][0]
        
        selected_lang = st.selectbox(
            'Language',
            options=list(language_options.keys()),
            index=list(language_options.keys()).index(current_display),
            label_visibility='collapsed',
            key='lang_selector'
        )
        
        # 更新语言
        if language_options[selected_lang] != lang:
            st.session_state['language'] = language_options[selected_lang]
            st.rerun()
    
    # 主标题
    with col1:
        st.markdown(f'<h1>{get_text("title", lang)}</h1>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="subtitle">{get_text("subtitle", lang)}</p>', unsafe_allow_html=True)
    
    cfg = load_config('config.yaml')
    workspace_root = Path(cfg['app']['workspace_root'])
    runs_root = Path(cfg['app']['runs_root'])
    ensure_dirs(workspace_root)
    ensure_dirs(runs_root)

    # 侧边栏
    with st.sidebar:
        st.markdown(f'## {get_text("config", lang)}')
        st.markdown('')
        
        # arXiv ID
        arxiv_id = st.text_input(
            get_text('arxiv_id', lang),
            value='',
            placeholder=get_text('arxiv_placeholder', lang),
            help=get_text('arxiv_help', lang)
        )
        
        # 模板路径
        template_path = st.text_input(
            get_text('template_path', lang),
            value=cfg['app'].get('default_template', 'assets/templates/example_template.tex'),
            placeholder=get_text('template_placeholder', lang),
            help=get_text('template_help', lang)
        )
        
        # 运行名称
        run_name = st.text_input(
            get_text('run_name', lang),
            value=time.strftime('%Y%m%d_%H%M%S'),
            help=get_text('run_help', lang)
        )
        
        st.markdown('')
        
        # 生成按钮
        compile_btn = st.button(get_text('generate_btn', lang), use_container_width=True)
        
        st.markdown('---')
        st.info(get_text('config_tip', lang))

    # 主内容区 - 两栏布局
    left, right = st.columns([0.5, 0.5])

    if compile_btn:
        if not arxiv_id:
            st.error(get_text('enter_arxiv', lang))
            return
            
        run_dir = runs_root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        work_dir = workspace_root / run_name
        work_dir.mkdir(parents=True, exist_ok=True)

        with left:
            st.markdown(f'### {get_text("generation_log", lang)}')
            st.markdown('')
            
            # 步骤1: 获取源码
            with st.status(get_text('fetching', lang), expanded=True) as status:
                try:
                    src_dir = fetch_arxiv_source(arxiv_id, work_dir)
                    status.update(label=get_text('fetch_success', lang), state='complete')
                    st.success(f'{get_text("downloaded_to", lang)} `{src_dir}`')
                except Exception as exc:
                    status.update(label=get_text('fetch_failed', lang), state='error')
                    st.error(f'{get_text("failed_fetch", lang)} {exc}')
                    return

            # 步骤2: 解析LaTeX
            with st.status(get_text('parsing', lang), expanded=True) as status:
                try:
                    paper_tex = flatten_latex_tree(src_dir)
                    status.update(label=get_text('parse_success', lang), state='complete')
                    st.success(f'{get_text("flattened", lang)} {len(paper_tex):,} {get_text("characters", lang)}')
                except Exception as exc:
                    status.update(label=get_text('parse_failed', lang), state='error')
                    st.error(f'{get_text("failed_parse", lang)} {exc}')
                    return

            # 步骤3: AI生成
            with st.status(get_text('generating', lang), expanded=True) as status:
                try:
                    body_tex = generate_beamer_body(paper_tex, Path('assets/AGENTS.md'), cfg, run_dir)
                    status.update(label=get_text('generate_success', lang), state='complete')
                    st.success(f'{get_text("generated", lang)} {len(body_tex):,} {get_text("characters", lang)}')
                except Exception as exc:
                    status.update(label=get_text('generate_failed', lang), state='error')
                    st.error(f'{get_text("failed_llm", lang)} {exc}')
                    return
                    
            talk_tex = work_dir / 'talk.tex'
            talk_tex.write_text(body_tex, encoding='utf-8')

            # 步骤4: 编译PDF
            with st.status(get_text('compiling', lang), expanded=True) as status:
                try:
                    pdf_path = compile_latex(talk_tex, template_path, work_dir, cfg)
                    status.update(label=get_text('compile_success', lang), state='complete')
                    st.success(f'{get_text("pdf_generated", lang)} `{pdf_path.name}`')
                except Exception as exc:
                    status.update(label=get_text('compile_failed', lang), state='error')
                    st.error(f'{get_text("failed_compile", lang)} {exc}')
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
            st.markdown(f'### {get_text("pdf_preview", lang)}')
            st.markdown('')
            
            if 'pdf_path' in st.session_state:
                try:
                    pages = render_pdf_pages(Path(st.session_state['pdf_path']), dpi=cfg['pdf']['render_dpi'])
                    
                    page_count = len(pages)
                    if lang == 'zh':
                        st.info(get_text('total_pages', lang).format(page_count))
                    else:
                        st.info(f'{get_text("total_pages", lang)} {page_count}')
                    
                    # 页面选择器
                    page_num = st.slider('Page', 1, page_count, 1, label_visibility='collapsed')
                    
                    # 显示选中的页面
                    if lang == 'zh':
                        caption = get_text('page_of', lang).format(page_num, page_count)
                    else:
                        caption = get_text('page_of', lang).format(page_num, page_count)
                    
                    st.image(
                        pages[page_num - 1],
                        use_container_width=True,
                        caption=caption
                    )
                    
                except Exception as exc:
                    st.error(f'{get_text("preview_failed", lang)} {exc}')

    # 修复单页功能
    if 'body_tex' in st.session_state:
        st.markdown('---')
        with st.expander(get_text('fix_frame', lang), expanded=False):
            body_tex = st.session_state['body_tex']
            frames = extract_frames(body_tex)
            max_frame = max(len(frames), 1)

            col1, col2 = st.columns([1, 3])
            
            with col1:
                frame_index = st.number_input(
                    get_text('frame_number', lang),
                    min_value=1,
                    max_value=max_frame,
                    value=1,
                    help=get_text('frame_help', lang)
                )
            
            with col2:
                current_frame = frames[frame_index - 1] if frames else ''
                st.code(current_frame, language='latex', line_numbers=True)

            frame_text = st.text_area(
                get_text('edit_latex', lang),
                value=current_frame,
                height=300,
                help=get_text('edit_help', lang)
            )

            if st.button(get_text('auto_fix', lang), use_container_width=True):
                run_dir = runs_root / st.session_state.get('run_name', run_name)
                
                with st.spinner(get_text('fixing', lang)):
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

                        st.success(get_text('fix_success', lang))
                        st.rerun()
                        
                    except Exception as exc:
                        st.error(f'{get_text("fix_failed", lang)} {exc}')

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
