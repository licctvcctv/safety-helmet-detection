import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


APP_NAME = "SafetyHelmetDetection"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_resource_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return PROJECT_ROOT


def get_launch_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return PROJECT_ROOT


def _ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def _is_writable(path):
    try:
        path = _ensure_dir(path)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def get_data_root():
    launch_root = get_launch_root()
    if _is_writable(launch_root):
        return launch_root

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return _ensure_dir(Path(local_app_data) / APP_NAME)
    return _ensure_dir(Path.home() / f".{APP_NAME}")


def get_dialog_root():
    for candidate in (get_launch_root(), Path.home(), Path.cwd()):
        if candidate.exists():
            return candidate
    return Path.cwd()


def get_bundled_model_dir():
    return get_resource_root() / "ptmodel"


def get_user_model_dir():
    return _ensure_dir(get_data_root() / "ptmodel")


def iter_model_dirs():
    seen = set()
    for model_dir in (get_bundled_model_dir(), get_user_model_dir()):
        resolved = str(model_dir.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        yield model_dir


def get_results_root():
    return _ensure_dir(get_data_root() / "result")


def get_logs_root():
    return _ensure_dir(get_data_root() / "logs")


def get_log_file():
    return get_logs_root() / "runtime.log"


def append_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_log_file().open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


def append_exception(prefix, exc):
    details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    append_log(f"{prefix}\n{details}".rstrip())
