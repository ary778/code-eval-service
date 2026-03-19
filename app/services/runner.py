import subprocess
import tempfile
import sys
import os
from typing import List
from app.models.schemas import TestCase, ExecutionDetail, ExecutionResult

def execute_test_cases(file_path: str, test_cases: List[TestCase]) -> ExecutionResult:
    details = []
    tests_passed = 0

    if not test_cases:
        # Dry run the file
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=2
            )
            passed = result.returncode == 0
            details.append(
                ExecutionDetail(
                    test_input="None (Dry Run)",
                    passed=passed,
                    output=result.stdout,
                    error=result.stderr if not passed else None
                )
            )
            return ExecutionResult(
                status="passed" if passed else "failed",
                tests_passed=1 if passed else 0,
                total_tests=1,
                details=details
            )
        except subprocess.TimeoutExpired:
             return ExecutionResult(
                 status="failed",
                 tests_passed=0,
                 total_tests=1,
                 details=[ExecutionDetail(test_input="None", passed=False, output="", error="Execution timed out.")]
             )

    for test in test_cases:
        runner_code = f"""
import sys
# Execute the user code in the current namespace
with open(r'{file_path}', 'r') as f:
    exec(f.read())

# Run the test input
try:
    result = eval('{test.input}')
    print(result)
except Exception as e:
    print(repr(e), file=sys.stderr)
    sys.exit(1)
"""
        fd, runner_path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(runner_code)
            
            result = subprocess.run(
                [sys.executable, runner_path],
                capture_output=True,
                text=True,
                timeout=2
            )
            output = result.stdout.strip()
            passed = (result.returncode == 0 and output == test.expected_output.strip())
            
            if passed:
                tests_passed += 1
                
            details.append(
                ExecutionDetail(
                    test_input=test.input,
                    passed=passed,
                    output=output,
                    error=result.stderr if not passed else None
                )
            )
        except subprocess.TimeoutExpired:
            details.append(
                ExecutionDetail(test_input=test.input, passed=False, output="", error="Execution timed out.")
            )
        finally:
            if os.path.exists(runner_path):
                os.remove(runner_path)

    return ExecutionResult(
        status="passed" if tests_passed == len(test_cases) else "failed",
        tests_passed=tests_passed,
        total_tests=len(test_cases),
        details=details
    )
