from pydantic import BaseModel, Field
from typing import List, Optional

class TestCase(BaseModel):
    input: str = Field(..., description="String representation of the input parameters to the test case.")
    expected_output: str = Field(..., description="String representation of the expected output.")

class EvaluationRequest(BaseModel):
    language: str = Field(..., description="The programming language of the code snippet.")
    code: str = Field(..., description="The source code to be evaluated.")
    test_cases: Optional[List[TestCase]] = Field(default=[], description="List of test cases to run.")

class SyntaxCheckResult(BaseModel):
    status: str
    message: str

class LintingResult(BaseModel):
    status: str
    output: str

class ExecutionDetail(BaseModel):
    test_input: str
    passed: bool
    output: str
    error: Optional[str] = None

class ExecutionResult(BaseModel):
    status: str
    tests_passed: int
    total_tests: int
    details: List[ExecutionDetail]

class EvaluationResponse(BaseModel):
    status: str
    syntax_check: SyntaxCheckResult
    linting: LintingResult
    execution: Optional[ExecutionResult] = None
