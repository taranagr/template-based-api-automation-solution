# 🧪 Template-Based API Automation Solution

This repository contains a Python-based API automation framework built with Behave for validating REST API scenarios against public sample endpoints. It is designed to demonstrate behavior-driven testing, reusable request templates, and environment-based configuration.

## 🔍 What this project does

The test suite covers:

- Product API scenarios such as add, get, update, and delete operations
- User authentication and user profile retrieval
- Request body and header templating using JSON files
- Response validation through step definitions
- Environment-specific configuration for DEV, INT, and STG

## 📁 Project structure

- [main.py](main.py) - entry point placeholder for the project
- [requirements.txt](requirements.txt) - Python dependencies
- [api_templates/](api_templates) - JSON request/response templates used by the tests
- [common_library/api_lib.py](common_library/api_lib.py) - shared API helper functions
- [features/](features) - Behave feature files and step definitions
  - [features/add_product.feature](features/add_product.feature)
  - [features/get_product.feature](features/get_product.feature)
  - [features/update_product.feature](features/update_product.feature)
  - [features/e2e_product.feature](features/e2e_product.feature)
  - [features/user.feature](features/user.feature)
  - [features/steps/product.py](features/steps/product.py)
  - [features/steps/user.py](features/steps/user.py)
- [global_config/api_config.ini](global_config/api_config.ini) - environment URLs and configuration values
- [utilities/](utilities) - encryption, decryption, and key management helpers

## ✅ Prerequisites

Before running the tests, make sure you have:

- Python 3.8 or newer
- pip
- Internet access to reach the sample APIs used by the suite

## ⚙️ Setup

1. Clone or open the project folder.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Confirm the environment is configured. The tests default to the STG section in [global_config/api_config.ini](global_config/api_config.ini), but you can override the environment by setting the TEST_ENVIRONMENT variable if required.

## ▶️ Running tests

Run a single feature file:

```bash
behave features/add_product.feature
```

Run a single scenario by name:

```bash
behave features/add_product.feature --name "Add_Product_01: Add Product API with Mandatory fields"
```

Run the full suite:

```bash
behave
```

Run with a readable console report:

```bash
behave -f pretty
```

You can also output JSON results for CI or reporting:

```bash
behave -f json -o reports/behave-results.json
```

## 🧠 Test design approach

The framework uses Behave feature files written in Gherkin. Each step is mapped to Python functions that:

- build request URLs from config values
- load JSON request bodies and headers from the templates folder
- update payload values dynamically
- send requests via requests
- validate status codes and expected response content

This keeps the test cases readable while separating the API logic into reusable helpers.

## ⚙️ Configuration details

The main configuration file is [global_config/api_config.ini](global_config/api_config.ini). It contains sections such as:

- DEV
- INT
- STG

Each section contains endpoint definitions used by the step files. If you need to point the suite to different services, update the relevant URLs there.

## 🧩 Template files

The JSON files in [api_templates/](api_templates) define reusable request bodies and headers for the tests. These templates are loaded dynamically by the step definitions, which makes the suite easier to extend for new scenarios.

## 🖥️ Chrome extension bridge

The repository includes a working local bridge for a Chrome extension that can trigger actual Behave scenarios through HTTP.

- [extension_bridge.py](extension_bridge.py) starts a local HTTP server on `http://127.0.0.1:8000`
- `GET /health` returns the backend status
- `POST /api/run` accepts a JSON payload with `feature`, `scenario`, and `environment`
- The bridge executes Behave using the selected scenario and returns the result JSON

Example request:

```bash
$body = @{
  feature = 'user.feature'
  scenario = 'User Details_01: Run User API'
  environment = 'STG'
} | ConvertTo-Json -Compress

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/run' -Method Post -ContentType 'application/json' -Body $body
```

Example response:

```json
{
  "status": "ok",
  "result": "pass",
  "feature": "user.feature",
  "scenario": "User Details_01: Run User API",
  "environment": "STG",
  "message": "1 scenario(s) passed out of 1.",
  "exit_code": 0,
  "passed": 1,
  "failed": 0,
  "total": 1
}
```

The extension UI files are in [extension_prototype/](extension_prototype), and they call this backend when a scenario is run.

## ▶️ Start the extension backend

From the project root:

```bash
python extension_bridge.py
```

You can then verify it is alive with:

```bash
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
```

## 📝 Notes

- Some scenarios depend on live external APIs, so test results may vary if the upstream service changes.
- The suite is intentionally simple and educational, making it a good starting point for learning API automation with Behave and Python.
- If you encounter issues, verify that the Python dependencies are installed and that your environment can reach the configured endpoints.
