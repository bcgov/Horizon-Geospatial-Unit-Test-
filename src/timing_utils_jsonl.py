"""
timing_utils_jsonl.py

Simple timing recorder that writes structured events as JSONL (one JSON object per line).

Usage:
    from timing_utils_jsonl import timeit, Timer, set_run_context

    @timeit(jsonl_path="timings/session.jsonl")
    def work(x):
        ...

    with Timer(step="reproject", jsonl_path="timings/session.jsonl"):
        ...

Notes:
- No external dependencies required.
- Safe for basic users/environments (ArcGIS Pro minimal Python).
- For heavy concurrent writers you may still see interleaving on non-POSIX systems; this is best-effort atomic append.
"""
from functools import wraps
import logging
import os
import time
import datetime
import json
import threading
import traceback
import getpass
from typing import Optional, Callable, Any, Dict
import uuid

# Basic structured logger (callers may reconfigure)
_logger = logging.getLogger("timing_utils_jsonl")
if not _logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    _logger.addHandler(h)
    _logger.setLevel(logging.INFO)

_thread_local = threading.local()


def set_run_context(run_id: str):
    """Set a run identifier for this thread (useful in test sessions)."""
    _thread_local.run_id = run_id


def get_run_context() -> Optional[str]:
    return getattr(_thread_local, "run_id", None)


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _ensure_parent_dir(path: str):
    parent = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(parent, exist_ok=True)


def _append_jsonl_atomic(path: str, obj: Dict[str, Any]):
    """
    Append a single JSON line atomically where possible.
    Uses os.open with O_APPEND to avoid partial-writes on POSIX.
    """
    _ensure_parent_dir(path)
    line = json.dumps(obj, default=str, ensure_ascii=False) + "\n"
    data = line.encode("utf-8")
    try:
        flags = os.O_CREAT | os.O_WRONLY | os.O_APPEND
        # mode 0o666 -> respect umask
        fd = os.open(path, flags, 0o666)
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
    except Exception:
        # Fallback to normal append (windows and other cases)
        try:
            with open(path, "a", encoding="utf-8", newline="") as f:
                f.write(line)
        except Exception:
            _logger.exception("Failed to append JSONL timing record")


def _make_record(
    user: Optional[str],
    module: str,
    func_name: str,
    step: Optional[str],
    start_ts: float,
    end_ts: float,
    status: str,
    notes: Optional[str],
    extra: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    duration = end_ts - start_ts
    rec = {
        "id": str(uuid.uuid4()),
        "timestamp_utc": _now_iso(),
        "user": user or getpass.getuser(),
        "run_id": get_run_context(),
        "module": module,
        "function": func_name,
        "step": step or "",
        "start_iso": datetime.datetime.utcfromtimestamp(start_ts).isoformat() + "Z",
        "end_iso": datetime.datetime.utcfromtimestamp(end_ts).isoformat() + "Z",
        "duration_seconds": round(duration, 6),
        "status": status,
        "notes": notes or "",
        "extra": extra or {},
    }
    return rec


def _log_structured(row: Dict[str, Any], level=logging.INFO):
    try:
        _logger.log(level, json.dumps(row, default=str))
    except Exception:
        _logger.exception("Failed to emit structured log")


def timeit(
    step: Optional[str] = None,
    user: Optional[str] = None,
    jsonl_path: Optional[str] = None,
    log_level: int = logging.INFO,
    include_exception_trace: bool = True,
):
    """
    Decorator factory to time functions/methods and write JSONL records.

    - step: short step name (defaults to function name)
    - user: override recorded user (defaults to system username)
    - jsonl_path: if provided, append records to that JSONL file
    - log_level: logging level used for structured log line
    - include_exception_trace: include traceback in notes on failure
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            status = "success"
            notes = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                status = "failure"
                notes = str(exc)
                if include_exception_trace:
                    notes = (notes or "") + "\n" + traceback.format_exc()
                raise
            finally:
                end = time.time()
                rec = _make_record(
                    user=user,
                    module=getattr(func, "__module__", ""),
                    func_name=getattr(func, "__qualname__", getattr(func, "__name__", "")),
                    step=step or getattr(func, "__name__", ""),
                    start_ts=start,
                    end_ts=end,
                    status=status,
                    notes=notes,
                    extra={},
                )
                _log_structured(rec, level=log_level)
                if jsonl_path:
                    try:
                        _append_jsonl_atomic(jsonl_path, rec)
                    except Exception:
                        _logger.exception("Failed to write JSONL timing record")
        return wrapper
    return decorator


class Timer:
    """
    Context manager to time arbitrary blocks and optionally write JSONL records.

    Example:
        with Timer(step="reproject", jsonl_path="timings/session.jsonl"):
            do_work()
    """
    def __init__(
        self,
        step: Optional[str] = None,
        user: Optional[str] = None,
        jsonl_path: Optional[str] = None,
        log_level: int = logging.INFO,
        notes: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.step = step or "block"
        self.user = user
        self.jsonl_path = jsonl_path
        self.log_level = log_level
        self.notes = notes
        self.extra = extra or {}

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        end = time.time()
        status = "success" if exc_type is None else "failure"
        notes = self.notes
        if exc_type is not None:
            notes = (notes or "") + "\n" + (str(tb) or "")
        rec = _make_record(
            user=self.user,
            module="__block__",
            func_name=self.step,
            step=self.step,
            start_ts=self.start,
            end_ts=end,
            status=status,
            notes=notes,
            extra=self.extra,
        )
        _log_structured(rec, level=self.log_level)
        if self.jsonl_path:
            try:
                _append_jsonl_atomic(self.jsonl_path, rec)
            except Exception:
                _logger.exception("Failed to write JSONL timing record")
        # Do not suppress exceptions
        return False


# Simple usage demo when run directly
if __name__ == "__main__":
    set_run_context("manual-demo")
    demo_path = os.path.join("timings", "demo-session.jsonl")

    @timeit(jsonl_path=demo_path)
    def slow_square(x):
        time.sleep(0.2)
        return x * x

    class P:
        @timeit(jsonl_path=demo_path)
        def run(self):
            time.sleep(0.1)

    slow_square(3)
    with Timer(step="demo-block", jsonl_path=demo_path):
        time.sleep(0.05)
    P().run()