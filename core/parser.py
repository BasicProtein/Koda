import re
from pathlib import Path


INCLUDE_PATTERNS = [
    re.compile(r'\\input\{([^}]+)\}'),
    re.compile(r'\\include\{([^}]+)\}'),
    re.compile(r'\\subfile\{([^}]+)\}'),
    re.compile(r'\\import\{([^}]+)\}\{([^}]+)\}'),
]


def _read_tex(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def _strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith('%'):
            continue
        # Remove inline comments that are not escaped.
        line = re.sub(r'(?<!\\)%.*$', '', line)
        lines.append(line)
    return '\n'.join(lines)


def _resolve_path(base: Path, rel: str) -> Path:
    if not rel.endswith('.tex'):
        rel = rel + '.tex'
    return (base / rel).resolve()


def _flatten(text: str, base: Path, seen: set) -> str:
    text = _strip_comments(text)

    def repl(match):
        if match.re == INCLUDE_PATTERNS[3]:
            folder = match.group(1)
            fname = match.group(2)
            path = _resolve_path(base / folder, fname)
        else:
            path = _resolve_path(base, match.group(1))

        if path in seen or not path.exists():
            return ''
        seen.add(path)
        return _flatten(_read_tex(path), path.parent, seen)

    changed = True
    while changed:
        changed = False
        for pat in INCLUDE_PATTERNS:
            new_text, n = pat.subn(repl, text)
            if n > 0:
                changed = True
                text = new_text
    return text


def flatten_latex_tree(src_dir: Path) -> str:
    main_candidates = list(src_dir.rglob('*.tex'))
    if not main_candidates:
        raise ValueError('No .tex files found')

    main_file = None
    for cand in main_candidates:
        text = _read_tex(cand)
        if '\\begin{document}' in text:
            main_file = cand
            break
    if main_file is None:
        main_file = main_candidates[0]

    seen = {main_file}
    return _flatten(_read_tex(main_file), main_file.parent, seen)


def extract_frames(body_tex: str) -> list[str]:
    pattern = re.compile(r'\\begin\{frame\}.*?\\end\{frame\}', re.DOTALL)
    return pattern.findall(body_tex)
