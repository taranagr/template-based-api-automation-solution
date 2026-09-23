import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FEATURES_DIR = ROOT_DIR / "features"
HISTORY_PATH = ROOT_DIR / "reports" / "extension-run-history.json"
API_TEMPLATES_DIR = ROOT_DIR / "api_templates"
GLOBAL_CONFIG_DIR = ROOT_DIR / "global_config"
TEMPLATES_DIR = ROOT_DIR / "templates"
STEPS_DIR = FEATURES_DIR / "steps"


def validate_api_name(api_name: str) -> str:
    api_name = (api_name or "").strip()
    if not api_name or not re.fullmatch(r"[A-Za-z0-9_]+", api_name):
        raise ValueError("API / Feature Name can only contain letters, numbers, and underscores.")
    return api_name


def update_ini_file(token_key: str, token_url: str, actual_key: str, actual_url: str):
    config_path = GLOBAL_CONFIG_DIR / "api_config.ini"
    lines = config_path.read_text(encoding="utf-8").splitlines() if config_path.exists() else []
    sections = {"DEV": [], "INT": [], "STG": []}
    current_section = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            sections.setdefault(current_section, [])
            continue
        if current_section is not None:
            sections[current_section].append(line)

    for section_name in ("DEV", "INT", "STG"):
        section_lines = sections[section_name]
        replacements = {token_key: token_url, actual_key: actual_url}
        found_keys = set()
        updated_lines = []
        for line in section_lines:
            match = re.match(r"^\s*([A-Za-z0-9_]+)\s*=", line)
            if match and match.group(1) in replacements:
                key = match.group(1)
                updated_lines.append(f"{key}={replacements[key].strip()}")
                found_keys.add(key)
            else:
                updated_lines.append(line)
        for key, value in replacements.items():
            if key not in found_keys:
                updated_lines.append(f"{key}={value.strip()}")
        sections[section_name] = updated_lines

    output = []
    for section_name, section_lines in sections.items():
        if output:
            output.append("")
        output.append(f"[{section_name}]")
        output.extend(section_lines)
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def generate_framework_files(payload):
    actual_name = validate_api_name(payload.get("actual-name"))
    token_url = (payload.get("token-url") or "").strip()
    actual_url = (payload.get("actual-url") or "").strip()
    actual_method = (payload.get("actual-method") or "").upper()
    header_content = payload.get("header-content")
    body_content = payload.get("body-content")

    if not token_url or not actual_url:
        raise ValueError("Both token URL and actual API URL are required.")
    if actual_method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        raise ValueError("Unsupported actual API method.")
    if not isinstance(header_content, str) or not isinstance(body_content, str):
        raise ValueError("Header and body JSON content are required.")
    json.loads(header_content)
    json.loads(body_content)

    API_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    STEPS_DIR.mkdir(parents=True, exist_ok=True)

    header_path = API_TEMPLATES_DIR / f"{actual_name}_headers.json"
    body_path = API_TEMPLATES_DIR / f"{actual_name}_body.json"
    header_path.write_text(header_content, encoding="utf-8")
    body_path.write_text(body_content, encoding="utf-8")

    token_key = f"{actual_name}_token_url"
    actual_key = f"{actual_method}_{actual_name}_url"
    update_ini_file(token_key, token_url, actual_key, actual_url)

    display_name = "".join(part.capitalize() for part in re.split(r"[_\-\s]+", actual_name) if part)
    step_template = (TEMPLATES_DIR / "steps_template.py").read_text(encoding="utf-8")
    step_content = step_template.replace("Product", display_name).replace("product", display_name[:1].lower() + display_name[1:])
    output_name = actual_name.lower()
    (STEPS_DIR / f"{output_name}.py").write_text(step_content, encoding="utf-8")

    feature_template = TEMPLATES_DIR / f"{actual_method}_template.feature"
    if not feature_template.exists():
        raise FileNotFoundError(f"Feature template not found: {feature_template.name}")
    feature_content = feature_template.read_text(encoding="utf-8")
    feature_content = feature_content.replace("Product", display_name).replace("product", display_name[:1].lower() + display_name[1:])
    (FEATURES_DIR / f"{actual_method.lower()}_{output_name}.feature").write_text(feature_content, encoding="utf-8")

    return {
        "api_templates": [header_path.name, body_path.name],
        "feature": {
            "path": f"features/{actual_method.lower()}_{output_name}.feature",
            "content": feature_content,
        },
        "step": {
            "path": f"features/steps/{output_name}.py",
            "content": step_content,
        },
        "config": {
            "path": "global_config/api_config.ini",
            "content": (GLOBAL_CONFIG_DIR / "api_config.ini").read_text(encoding="utf-8"),
        },
    }


def save_generated_files(payload):
    files = payload.get("files") or {}
    allowed_roots = {
        "feature": FEATURES_DIR,
        "step": FEATURES_DIR / "steps",
        "config": GLOBAL_CONFIG_DIR,
    }
    saved = []
    for file_type, root in allowed_roots.items():
        item = files.get(file_type) or {}
        relative_path = str(item.get("path") or "").replace("\\", "/")
        content = item.get("content")
        if not relative_path or not isinstance(content, str):
            raise ValueError(f"Missing {file_type} file path or content.")
        target = (ROOT_DIR / relative_path).resolve()
        expected_root = root.resolve()
        if target.parent != expected_root or target.suffix not in {".feature", ".py", ".ini"}:
            raise ValueError(f"Invalid generated {file_type} file path.")
        target.write_text(content, encoding="utf-8")
        saved.append(relative_path)
    return saved


def normalize_feature_name(feature_name: str) -> str:
    feature_name = (feature_name or "").strip()
    if not feature_name:
        raise ValueError("Feature name is required.")

    if feature_name.endswith(".feature"):
        feature_path = FEATURES_DIR / feature_name
    else:
        feature_path = FEATURES_DIR / f"{feature_name}.feature"

    if not feature_path.exists():
        raise FileNotFoundError(f"Feature file not found: {feature_path}")

    return str(feature_path)


def summarize_behave_result(json_path: str):
    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    passed = 0
    failed = 0
    total = 0
    scenario_statuses = []

    for feature in data:
        for element in feature.get("elements", []):
            if element.get("type") != "scenario":
                continue
            total += 1
            name = element.get("name", "Unnamed scenario")
            status = element.get("status", "unknown")
            steps = []
            for step in element.get("steps", []):
                result = step.get("result", {})
                steps.append({
                    "keyword": step.get("keyword", ""),
                    "name": step.get("name", ""),
                    "status": result.get("status", "unknown"),
                    "error": result.get("error_message", ""),
                })
            scenario_statuses.append({"name": name, "status": status, "steps": steps})
            if status == "passed":
                passed += 1
            else:
                failed += 1

    if failed > 0:
        result = "fail"
        message = f"{failed} scenario(s) failed out of {total}."
    elif total > 0:
        result = "pass"
        message = f"{passed} scenario(s) passed out of {total}."
    else:
        result = "unknown"
        message = "No scenarios were executed."

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "result": result,
        "message": message,
        "scenarios": scenario_statuses,
    }


def load_run_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def save_run_history(history):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history[-50:], indent=2), encoding="utf-8")


def run_behave(feature_name: str, scenario_name: str = None, environment: str = "STG"):
    feature_path = normalize_feature_name(feature_name)
    command = [sys.executable, "-m", "behave", feature_path]
    if scenario_name:
        command.extend(["--name", scenario_name])

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_path = tmp.name

    env = os.environ.copy()
    env["TEST_ENVIRONMENT"] = environment
    command.extend(["-f", "json", "-o", output_path])

    completed = subprocess.run(command, cwd=str(ROOT_DIR), env=env, capture_output=True, text=True)
    summary = summarize_behave_result(output_path) if os.path.exists(output_path) else {
        "result": "fail",
        "message": "Behave did not generate a JSON result file.",
        "details": completed.stdout,
        "stderr": completed.stderr,
    }

    if os.path.exists(output_path):
        os.remove(output_path)

    summary["exit_code"] = completed.returncode
    summary["feature"] = feature_name
    summary["scenario"] = scenario_name
    summary["environment"] = environment
    summary["stdout"] = completed.stdout
    summary["stderr"] = completed.stderr

    history = load_run_history()
    timestamp = int(time.time() * 1000)
    for scenario in summary.get("scenarios", []):
        history.append({
            "name": scenario.get("name", scenario_name or "Unnamed scenario"),
            "status": "Passed" if scenario.get("status") == "passed" else "Failed",
            "time": datetime.now().strftime("%I:%M %p"),
            "timestamp": timestamp,
            "steps": scenario.get("steps", []),
            "feature": feature_name,
            "environment": environment,
        })
    save_run_history(history)

    return summary


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "PulseRunnerBridge/1.0"

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json({"status": "ok"}, status=200)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send_json({"status": "ok"})
            return

        if path == "/api/features":
            features = []
            for feature_path in sorted(FEATURES_DIR.glob("*.feature")):
                feature_name = feature_path.name
                try:
                    with open(feature_path, "r", encoding="utf-8") as fp:
                        lines = fp.readlines()
                except Exception:
                    lines = []

                scenarios = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("Scenario") or stripped.startswith("Scenario Outline"):
                        scenarios.append(stripped)

                features.append({"name": feature_name, "scenarios": scenarios})

            self._send_json({"features": features})
            return

        if path == "/api/history":
            self._send_json({"history": load_run_history()})
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path not in {"/api/generate", "/api/generated-files", "/api/run"}:
            self._send_json({"error": "Route not found"}, status=404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8") or "{}")
        except Exception as exc:
            self._send_json({"error": f"Invalid JSON payload: {exc}"}, status=400)
            return

        try:
            if path == "/api/generate":
                generated = generate_framework_files(payload)
                self._send_json({"status": "ok", "message": "Framework files generated successfully.", "files": generated})
                return

            if path == "/api/generated-files":
                saved = save_generated_files(payload)
                self._send_json({"status": "ok", "message": "Generated file changes saved.", "files": saved})
                return

            feature_name = payload.get("feature")
            scenario_name = payload.get("scenario")
            environment = payload.get("environment", "STG")

            summary = run_behave(feature_name, scenario_name, environment)
            result = summary.get("result", "fail")
            status_code = 200 if result == "pass" else 500 if summary.get("exit_code") else 400
            self._send_json({
                "status": "ok",
                "result": result,
                "feature": feature_name,
                "scenario": scenario_name,
                "environment": environment,
                "message": summary.get("message", "Execution completed."),
                "exit_code": summary.get("exit_code", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "total": summary.get("total", 0),
                "scenarios": summary.get("scenarios", []),
            }, status=status_code)
        except Exception as exc:
            self._send_json({"status": "error", "result": "fail", "message": str(exc)}, status=500)

    def do_DELETE(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/history":
            save_run_history([])
            self._send_json({"status": "ok", "history": []})
            return
        self._send_json({"error": "Route not found"}, status=404)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), BridgeHandler)
    print(f"Pulse Runner bridge listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down bridge server...")
    finally:
        server.server_close()
