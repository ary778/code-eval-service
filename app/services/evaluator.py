from app.models.schemas import EvaluationRequest, EvaluationResponse
from app.services.linter import run_syntax_check, run_linter
from app.services.runner import execute_test_cases
from app.utils.file_handler import create_temp_code_file

def evaluate_code(request: EvaluationRequest) -> EvaluationResponse:
    # 1. Syntax Check
    syntax_result = run_syntax_check(request.code)
    if syntax_result.status == "failed":
        return EvaluationResponse(
            status="failed",
            syntax_check=syntax_result,
            linting={"status": "skipped", "output": ""},
            execution=None
        )

    # Write code to temp file for linting and execution
    with create_temp_code_file(request.code) as temp_path:
        # 2. Linting
        linting_result = run_linter(temp_path)
        
        # 3. Execution
        execution_result = execute_test_cases(temp_path, request.test_cases)
        
    final_status = "passed" if execution_result.status == "passed" and syntax_result.status == "passed" else "failed"

    return EvaluationResponse(
        status=final_status,
        syntax_check=syntax_result,
        linting=linting_result,
        execution=execution_result
    )
