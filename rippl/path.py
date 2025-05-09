from datetime import datetime
from pathlib import Path


def set_up_output(output_root: Path = Path.cwd() / Path("output")) -> Path:
    current_time = datetime.now().isoformat()
    output_dir = output_root / Path(current_time)
    output_dir.mkdir(parents=True)
    return output_dir
