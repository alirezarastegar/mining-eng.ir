"""CI-only compatibility shim: re-export stdlib pathlib with UTF-8 text defaults."""
import importlib.util
import os

_stdlib_file = os.path.join(os.path.dirname(os.__file__), "pathlib.py")
_spec = importlib.util.spec_from_file_location("_planjoy_stdlib_pathlib", _stdlib_file)
_stdlib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib)

for _name in dir(_stdlib):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_stdlib, _name)

_original_read_text = Path.read_text
_original_write_text = Path.write_text

def _read_text_utf8(self, encoding=None, errors=None):
    return _original_read_text(self, encoding=encoding or "utf-8", errors=errors)

def _write_text_utf8(self, data, encoding=None, errors=None, newline=None):
    return _original_write_text(self, data, encoding=encoding or "utf-8", errors=errors, newline=newline)

Path.read_text = _read_text_utf8
Path.write_text = _write_text_utf8
