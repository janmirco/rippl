from pathlib import Path


def set_up(output_dir_name: str = "output") -> Path:
    output_dir = Path.cwd() / Path(output_dir_name)
    if not output_dir.exists():
        output_dir.mkdir()
    return output_dir
