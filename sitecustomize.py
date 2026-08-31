"""PlanJoy CI helper: make pathlib text IO deterministic UTF-8 on Windows runners."""
from pathlib import Path

_original_read_text = Path.read_text
_original_write_text = Path.write_text

def _read_text_utf8(self, encoding=None, errors=None):
    return _original_read_text(self, encoding=encoding or "utf-8", errors=errors)

def _write_text_utf8(self, data, encoding=None, errors=None, newline=None):
    return _original_write_text(self, data, encoding=encoding or "utf-8", errors=errors, newline=newline)

Path.read_text = _read_text_utf8
Path.write_text = _write_text_utf8
