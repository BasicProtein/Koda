import subprocess
import os
from pathlib import Path


def _run(cmd, cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def compile_latex(talk_tex: Path, template_path: str, work_dir: Path, cfg: dict) -> Path:
    if not template_path:
        raise ValueError('Template path is required')

    template = Path(template_path).read_text(encoding='utf-8', errors='ignore')
    body = talk_tex.read_text(encoding='utf-8', errors='ignore')

    out_tex = work_dir / 'main.tex'
    out_tex.write_text(template + '\n' + body, encoding='utf-8')

    compiler = cfg['latex']['compiler']
    compiler_path = cfg['latex'].get('compiler_path') or compiler
    if compiler == 'latexmk':
        cmd = [compiler, '-pdf', '-xelatex', '-interaction=nonstopmode', '-output-directory=.', str(out_tex.name)]
    elif compiler == 'pdflatex':
        cmd = [compiler, '-interaction=nonstopmode', '-output-directory=.', str(out_tex.name)]
    else:
        # Fallback to original behavior for other compilers if not latexmk or pdflatex
        cmd = [compiler_path, out_tex.name]

    env = os.environ.copy()
    if 'bin_path' in cfg.get('latex', {}):
        bin_path = str(Path(cfg['latex']['bin_path']).resolve())
        env['PATH'] = f"{bin_path}{os.pathsep}{env['PATH']}"

    try:
        subprocess.run(cmd, cwd=work_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"LaTeX compile error:\n{exc.stderr.decode('utf-8', errors='ignore')}") from exc

    pdf_path = work_dir / 'main.pdf'
    if not pdf_path.exists():
        raise FileNotFoundError('PDF not generated')

    return pdf_path
