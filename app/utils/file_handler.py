import os
import tempfile
import contextlib

@contextlib.contextmanager
def create_temp_code_file(code: str, suffix: str = ".py"):
    """
    Creates a temporary file containing the provided code.
    Cleans up the file automatically when the context exits.
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
