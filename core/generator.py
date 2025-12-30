from pathlib import Path


def _build_prompt(agents_text: str, paper_tex: str) -> str:
    return '\n'.join([
        agents_text.strip(),
        '',
        '## Paper LaTeX Source',
        paper_tex.strip(),
    ])


def _build_fix_prompt(agents_text: str, frame_tex: str) -> str:
    return '\n'.join([
        agents_text.strip(),
        '',
        '## Task',
        'Only modify the following single frame. Do not output any extra text.',
        'Keep the output limited to one or two frames if splitting is needed.',
        '',
        '## Frame',
        frame_tex.strip(),
    ])


def _call_openai(prompt: str, cfg: dict) -> str:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError('openai package is required') from exc

    client_kwargs = {}
    base_url = cfg['llm'].get('base_url', '')
    if base_url:
        client_kwargs['base_url'] = base_url

    client = OpenAI(api_key=cfg['llm']['api_key'], **client_kwargs)
    resp = client.chat.completions.create(
        model=cfg['llm']['model'],
        messages=[{'role': 'user', 'content': prompt}],
        temperature=cfg['llm'].get('temperature', 0.2),
        max_tokens=cfg['llm'].get('max_tokens', 4000),
    )
    return resp.choices[0].message.content


def _call_anthropic(prompt: str, cfg: dict) -> str:
    try:
        import anthropic
    except Exception as exc:
        raise RuntimeError('anthropic package is required') from exc

    client = anthropic.Anthropic(api_key=cfg['llm']['api_key'])
    resp = client.messages.create(
        model=cfg['llm']['model'],
        max_tokens=cfg['llm'].get('max_tokens', 4000),
        temperature=cfg['llm'].get('temperature', 0.2),
        messages=[{'role': 'user', 'content': prompt}],
    )
    return resp.content[0].text


def _call_llm(prompt: str, cfg: dict) -> str:
    provider = cfg['llm']['provider']
    if provider == 'openai':
        return _call_openai(prompt, cfg)
    if provider == 'anthropic':
        return _call_anthropic(prompt, cfg)
    raise ValueError('Unsupported LLM provider')


def generate_beamer_body(paper_tex: str, agents_path: Path, cfg: dict, run_dir: Path) -> str:
    agents_text = agents_path.read_text(encoding='utf-8', errors='ignore')
    prompt = _build_prompt(agents_text, paper_tex)

    if run_dir:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / 'input_paper.tex').write_text(paper_tex, encoding='utf-8')
        (run_dir / 'prompt.txt').write_text(prompt, encoding='utf-8')

    output = _call_llm(prompt, cfg)

    if run_dir:
        (run_dir / 'output_body.tex').write_text(output, encoding='utf-8')

    if '\\begin{document}' not in output:
        output = '\n'.join([
            r'\\begin{document}',
            output.strip(),
            r'\\end{document}',
        ])

    return output


def fix_single_frame(frame_tex: str, agents_path: Path, cfg: dict, run_dir: Path, frame_index: int) -> str:
    agents_text = agents_path.read_text(encoding='utf-8', errors='ignore')
    prompt = _build_fix_prompt(agents_text, frame_tex)

    if run_dir:
        fname = f'fix_prompt_{frame_index:03d}.txt'
        (run_dir / fname).write_text(prompt, encoding='utf-8')

    output = _call_llm(prompt, cfg)

    if run_dir:
        fname = f'fix_output_{frame_index:03d}.tex'
        (run_dir / fname).write_text(output, encoding='utf-8')

    return output
