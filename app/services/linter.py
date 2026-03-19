import ast
import subprocess
from app.models.schemas import SyntaxCheckResult, LintingResult

def run_syntax_check(code: str) -> SyntaxCheckResult:
    try:
        ast.parse(code)
        return SyntaxCheckResult(status="passed", message="Syntax is valid.")
    except SyntaxError as e:
        return SyntaxCheckResult(
            status="failed",
            message=f"SyntaxError: {e.msg} at line {e.lineno}"
        )

def run_linter(file_path: str) -> LintingResult:
    try:
        result = subprocess.run(
            ["flake8", file_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return LintingResult(status="passed", output=result.stdout)
        else:
            return LintingResult(status="failed", output=result.stdout)
    except subprocess.TimeoutExpired:
        return LintingResult(status="failed", output="Linting timed out.")
    except Exception as e:
         return LintingResult(status="failed", output=str(e))
