from pathlib import Path
import tarfile
import zipfile

import arxiv


def fetch_arxiv_source(arxiv_id: str, dest_dir: Path) -> Path:
    if not arxiv_id:
        raise ValueError('arXiv ID is required')

    search = arxiv.Search(id_list=[arxiv_id])
    result = next(search.results(), None)
    if result is None:
        raise ValueError('arXiv ID not found')

    src_path = Path(result.download_source(dirpath=dest_dir))
    src_dir = dest_dir / 'paper_src'
    src_dir.mkdir(parents=True, exist_ok=True)

    if src_path.suffixes[-2:] == ['.tar', '.gz']:
        with tarfile.open(src_path, 'r:gz') as tar:
            tar.extractall(path=src_dir)
    elif src_path.suffix == '.zip':
        with zipfile.ZipFile(src_path, 'r') as zf:
            zf.extractall(path=src_dir)
    else:
        raise ValueError('Unsupported source archive')

    return src_dir
