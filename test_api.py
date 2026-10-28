"""Basic local API checks. Start the server first, then run: python test_api.py"""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "http://127.0.0.1:5000"

def request_json(path, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(BASE_URL + path, data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))

def main():
    status, health = request_json("/health")
    assert status == 200 and health.get("model_loaded") is True, health
    print("PASS: health endpoint")

    samples = [
        {"student_name": "Juan Dela Cruz", "study_hours": 7},
        {"student_name": "Maria Santos", "study_hours": 2},
        {"student_name": "Alex Reyes", "study_hours": 5},
        {"student_name": "Jamie Cruz", "study_hours": 10},
        {"student_name": "Taylor Garcia", "study_hours": 0},
    ]
    for student in samples:
        status, result = request_json("/predict", "POST", student)
        assert status == 200, result
        assert result["student_name"] == student["student_name"]
        assert result["study_hours"] == student["study_hours"]
        assert result["prediction"] in {"PASS", "FAIL"}
        print(f"PASS: {result['student_name']} | {result['study_hours']} hours | {result['prediction']}")

    status, error = request_json("/predict", "POST", {"student_name": "", "study_hours": 4})
    assert status == 400, (status, error)
    print("PASS: invalid input is rejected")
    print("All API tests passed.")

if __name__ == "__main__":
    main()
