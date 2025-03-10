import sys
import importlib
from pathlib import Path


# define default settings value
REMOVE_PATTERN = [
    ",",
    "/",
    "\n",
    "?",
    "..",
    ". ",
    ".\n",
    "\\"
]
BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "my_db.db"
INITIAL_DATA = BASE_DIR / "initial_data.sql"

settings_keys = [
    "REMOVE_PATTERN",
    "DB_PATH",
    "INITIAL_DATA"
]



def settings_path(module_path: Path):
    spec = importlib.util.spec_from_file_location("temp_module", module_path)
    externe_settings_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(externe_settings_module)
    current_module = sys.modules[__name__]
    for key in settings_keys:
        if hasattr(externe_settings_module, key):
            setattr(
                current_module,
                key,
                getattr(
                    externe_settings_module,
                    key
                )
            )
