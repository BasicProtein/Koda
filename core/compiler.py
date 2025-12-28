import subprocess
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
        cmd = [compiler_path, '-pdf', out_tex.name]
    else:
        cmd = [compiler_path, out_tex.name]

    _run(cmd, work_dir)

    pdf_path = work_dir / 'main.pdf'
    if not pdf_path.exists():
        raise FileNotFoundError('PDF not generated')

    return pdf_path
