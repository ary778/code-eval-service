from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_evaluate_valid_code_with_tests():
    payload = {
        "language": "python",
        "code": "def add(a, b):\n    return a + b",
        "test_cases": [
            {
                "input": "add(1, 2)",
                "expected_output": "3"
            }
        ]
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "passed"
    assert data["syntax_check"]["status"] == "passed"
    assert data["execution"]["tests_passed"] == 1

def test_evaluate_syntax_error():
    payload = {
        "language": "python",
        "code": "def add(a, b)",
        "test_cases": []
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["syntax_check"]["status"] == "failed"
    assert "SyntaxError" in data["syntax_check"]["message"]

def test_evaluate_unsupported_language():
    payload = {
        "language": "javascript",
        "code": "function add(a, b) { return a + b; }",
        "test_cases": []
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 400
