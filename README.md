# Code Evaluation Service

A robust backend REST API built with FastAPI that accepts Python code snippets, runs basic validation checks (syntax checking and linting), securely evaluates simple test cases, and returns comprehensive evaluation results. 

## Features
- **FastAPI Backend**: Fast, asynchronous processing with auto-generated OpenAPI documentation.
- **Syntax Validation**: Checks code validity before running.
- **Linting**: Leverages `flake8` to enforce code quality.
- **Secure Test Execution**: Safely evaluates the user's Python code against predefined inputs using isolated processes and hard timeouts to prevent infinite loops.

## Project Structure

```text
code-eval-service/
├── app/
│   ├── main.py              # FastAPI application initialization and endpoints
│   ├── models/              # Pydantic schema models
│   ├── services/            # Core business logic (Runner, Linter, Evaluator)
│   └── utils/               # File handlers and temporary execution contexts
├── tests/                   # Pytest test suite
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Setup Instructions

### 1. Prerequisites
- Python 3.10+ installed
- Git
- Docker and Docker Compose (recommended)

> **IMPORTANT**: Please read the [SECURITY.md](SECURITY.md) before integrating this service in a production environment or executing untrusted code.

### 2. Run with Docker (Recommended)
This is the easiest way to run the service:
```bash
docker-compose up --build
```
The application will be available at `http://localhost:8000`.

### 3. Clone the repository
```bash
git clone https://github.com/ary778/code-eval-service.git
cd code-eval-service
```

### 3. Install Dependencies
It is recommended to create a virtual environment first:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```
Install required packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Server
Use `uvicorn` to start the application:
```bash
uvicorn app.main:app --reload
```
The application will be running at `http://localhost:8000`.
You can view the interactive Swagger API documentation at `http://localhost:8000/docs`.

### 5. Run tests
To run the automated test suite, ensure your virtual environment is active and run:
```bash
pytest
```

## API Endpoints

### 1. Health Check
Checks if the API is running correctly.

- **URL**: `/health`
- **Method**: `GET`
- **Success Response**: 
  - **Code**: 200 OK
  - **Content**: `{"status": "healthy"}`

### 2. Evaluate Code
Evaluates a Python code snippet against provided test cases.

- **URL**: `/api/v1/evaluate`
- **Method**: `POST`
- **Body**: 
```json
{
  "language": "python",
  "code": "def multiply(a, b):\n    return a * b",
  "test_cases": [
    {
      "input": "multiply(3, 4)",
      "expected_output": "12"
    },
    {
      "input": "multiply(5, 0)",
      "expected_output": "0"
    }
  ]
}
```

- **Success Response**:
  - **Code**: 200 OK
  - **Content**: 
```json
{
  "status": "passed",
  "syntax_check": {
    "status": "passed",
    "message": "Syntax is valid."
  },
  "linting": {
    "status": "passed",
    "output": ""
  },
  "execution": {
    "status": "passed",
    "tests_passed": 2,
    "total_tests": 2,
    "details": [
      {
        "test_input": "multiply(3, 4)",
        "passed": true,
        "output": "12",
        "error": null
      },
      {
        "test_input": "multiply(5, 0)",
        "passed": true,
        "output": "0",
        "error": null
      }
    ]
  }
}
```
