from datetime import datetime
from pathlib import Path


def set_up_output(output_root: Path = Path.cwd() / Path("output")) -> Path:
    current_time = datetime.now().isoformat()
    output_dir = output_root / Path(current_time)
    output_dir.mkdir(parents=True)
    return output_dir


def set_up_data(data_dir: Path) -> Path:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data path does not exist: {data_dir.as_posix()}")
    return data_dir
