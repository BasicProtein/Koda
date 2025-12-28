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


def main() -> None:
    st.set_page_config(page_title='Koda', layout='wide')
    st.title('Koda')

    cfg = load_config('config.yaml')
    workspace_root = Path(cfg['app']['workspace_root'])
    runs_root = Path(cfg['app']['runs_root'])
    ensure_dirs(workspace_root)
    ensure_dirs(runs_root)

    with st.sidebar:
        st.header('Project')
        arxiv_id = st.text_input('arXiv ID', value='')
        template_path = st.text_input('Template path', value=cfg['app']['default_template'])
        run_name = st.text_input('Run name', value=time.strftime('%Y%m%d_%H%M%S'))
        compile_btn = st.button('Generate + Compile')

    left, right = st.columns([0.5, 0.5])

    if compile_btn:
        run_dir = runs_root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        work_dir = workspace_root / run_name
        work_dir.mkdir(parents=True, exist_ok=True)

        with left:
            st.subheader('Log')
            st.write('Fetching source...')
        try:
            src_dir = fetch_arxiv_source(arxiv_id, work_dir)
        except Exception as exc:
            st.error(f'Fetch failed: {exc}')
            return

        with left:
            st.write('Flattening LaTeX...')
        try:
            paper_tex = flatten_latex_tree(src_dir)
        except Exception as exc:
            st.error(f'Parse failed: {exc}')
            return

        with left:
            st.write('Generating body...')
        try:
            body_tex = generate_beamer_body(paper_tex, Path('assets/AGENTS.md'), cfg, run_dir)
        except Exception as exc:
            st.error(f'LLM failed: {exc}')
            return
        talk_tex = work_dir / 'talk.tex'
        talk_tex.write_text(body_tex, encoding='utf-8')

        with left:
            st.write('Compiling PDF...')
        try:
            pdf_path = compile_latex(talk_tex, template_path, work_dir, cfg)
        except Exception as exc:
            st.error(f'Compile failed: {exc}')
            return

        meta = {
            'arxiv_id': arxiv_id,
            'template_path': template_path,
            'run_name': run_name,
        }
        (run_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

        st.session_state['body_tex'] = body_tex
        st.session_state['work_dir'] = str(work_dir)
        st.session_state['run_name'] = run_name

        with right:
            st.subheader('Preview')
            pages = render_pdf_pages(pdf_path, dpi=cfg['pdf']['render_dpi'])
            for img_bytes in pages:
                st.image(img_bytes, use_column_width=True)

    if 'body_tex' in st.session_state:
        with st.expander('Fix Single Frame'):
            body_tex = st.session_state['body_tex']
            frames = extract_frames(body_tex)
            max_frame = max(len(frames), 1)

            frame_index = st.number_input('Frame index (1-based)', min_value=1, max_value=max_frame, value=1)
            current_frame = frames[frame_index - 1] if frames else ''
            frame_text = st.text_area('Frame LaTeX', value=current_frame, height=300)

            if st.button('Auto Fix This Frame'):
                run_dir = runs_root / st.session_state.get('run_name', run_name)
                try:
                    fixed = fix_single_frame(frame_text, Path('assets/AGENTS.md'), cfg, run_dir, frame_index)
                except Exception as exc:
                    st.error(f'LLM failed: {exc}')
                    return

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

                try:
                    pdf_path = compile_latex(talk_tex, template_path, work_dir, cfg)
                except Exception as exc:
                    st.error(f'Compile failed: {exc}')
                    return

                st.success('Frame updated and recompiled.')
                pages = render_pdf_pages(pdf_path, dpi=cfg['pdf']['render_dpi'])
                for img_bytes in pages:
                    st.image(img_bytes, use_column_width=True)


if __name__ == '__main__':
    main()
