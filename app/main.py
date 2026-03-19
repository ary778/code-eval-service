from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import EvaluationRequest, EvaluationResponse
from app.services.evaluator import evaluate_code

app = FastAPI(
    title="Code Evaluation Service",
    description="API for securely evaluating Python code snippets.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest):
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400, 
            detail="Unsupported language. Currently only 'python' is supported."
        )
    
    if not request.code.strip():
        raise HTTPException(
            status_code=400,
            detail="Code snippet cannot be empty."
        )
    
    try:
        response = evaluate_code(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"An internal error occurred: {str(e)}"}
        )
