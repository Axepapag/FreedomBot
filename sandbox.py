import tempfile
import subprocess
import os
import time
from logs import log_event

SAFE_MODULES = ["math", "random", "datetime"]

def run_code(code: str) -> str:
    """
    Executes Python code in a sandboxed environment using subprocess.
    Returns output or error.
    """
    if _contains_dangerous_imports(code):
        return "[SECURITY] Unsafe imports are not allowed."

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        os.unlink(temp_path)

        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "[SUCCESS] Code executed with no output."
        else:
            return f"[ERROR]\n{result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Execution took too long."
    except Exception as e:
        return f"[SANDBOX ERROR] {e}"

def test_code(code_block: str) -> bool:
    """
    Test a Python code block (e.g. patch) safely before applying.
    Returns True if the code runs cleanly, False otherwise.
    """
    import re

    try:
        code = code_block
        if "```python" in code:
            code = re.search(r"```python(.*?)```", code, re.DOTALL).group(1).strip()

        if _contains_dangerous_imports(code):
            return False

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            timeout=5
        )

        os.unlink(temp_path)
        return result.returncode == 0

    except Exception as e:
        print(f"[test_code ERROR] {e}")
        return False

def _contains_dangerous_imports(code: str) -> bool:
    """
    Checks for dangerous imports or keywords.
    """
    blocked = ["os", "sys", "shutil", "subprocess", "socket", "open", "input", "eval", "exec", "pickle", "ctypes"]
    lines = code.splitlines()
    for line in lines:
        if "import" in line or "__" in line:
            for b in blocked:
                if b in line:
                    return True
    return False