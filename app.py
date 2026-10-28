
from pathlib import Path
import sys
import threading
import webbrowser
import pickle
import json
from datetime import datetime

from flask import Flask, jsonify, request, render_template_string

BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"
HISTORY_PATH = BASE_DIR / "prediction_history.json"

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">

<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Exam Result Prediction</title>

<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#172033;background:#f3f5f9}
*{box-sizing:border-box}body{margin:0;padding:32px 16px}
main{max-width:900px;margin:auto}
.card{background:white;border:1px solid #e2e7ef;border-radius:18px;padding:26px;box-shadow:0 12px 35px #18243b0c;margin-bottom:24px}
h1{margin:0 0 8px;font-size:clamp(1.5rem,4vw,2.1rem)}
h2{margin:0 0 18px;font-size:1.3rem}
.sub{color:#657086;margin:0 0 24px;line-height:1.5}
label{display:block;font-weight:650;margin:15px 0 7px}
input{width:100%;padding:12px 13px;border:1px solid #cbd3e1;border-radius:10px;font-size:1rem}
button{margin-top:20px;background:#172033;color:white;border:0;border-radius:10px;padding:12px 18px;font-size:1rem;font-weight:700;cursor:pointer}
button:hover{background:#2a3a58}
.clear-btn{margin-top:0;background:#fff0ed;color:#a52c1c;border:1px solid #ffc2b7}
.clear-btn:hover{background:#ffe0da}
.result{display:none;margin-top:20px;padding:16px;border-radius:12px;line-height:1.55}
.pass{display:block;background:#e8f8ef;border:1px solid #a8e2bd;color:#17643a}
.fail{display:block;background:#fff0ed;border:1px solid #ffc2b7;color:#9b2c1b}
.error{display:block;background:#fff8df;border:1px solid #f1d77d;color:#795b00}
.meta{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.pill{background:#eef2f8;border-radius:999px;padding:7px 11px;font-size:.85rem;color:#43516a}
code{background:#f0f2f6;padding:2px 5px;border-radius:5px}
details{margin-top:24px;color:#566176}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;padding:12px;border-radius:8px}
.history-header{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.history-header h2{margin:0}
.history-header button{margin:0}
.table-wrap{width:100%;overflow-x:auto}
table{width:100%;border-collapse:collapse;min-width:540px;text-align:left}
th,td{padding:13px 12px;border-bottom:1px solid #e6eaf0;font-size:.92rem}
th{background:#f5f7fa;color:#526078;font-size:.82rem;text-transform:uppercase;letter-spacing:.04em}
tbody tr:hover{background:#fafbfe}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;font-size:.8rem;font-weight:700}
.badge-pass{background:#e8f8ef;color:#17643a}
.badge-fail{background:#fff0ed;color:#9b2c1b}
.empty{text-align:center;padding:28px 12px;color:#657086}
.history-status{font-size:.9rem;color:#657086;margin-top:12px}
@media(max-width:600px){body{padding:16px 10px}.card{padding:19px;border-radius:14px}}
</style>
</head>

<body>
<main>

<section class="card">
<h1>Student Exam Result Prediction</h1>

<p class="sub">
Enter a student name and study hours to get a PASS/FAIL prediction
from the locally saved machine-learning model.
</p>

<form id="predict-form">
<label for="student_name">Student name</label>
<input id="student_name" name="student_name"
placeholder="e.g., Juan Dela Cruz" maxlength="100" required>

<label for="study_hours">Study hours</label>
<input id="study_hours" name="study_hours" type="number"
min="0" max="24" step="0.5" placeholder="e.g., 7" required>

<button type="submit">Predict result</button>
</form>

<div id="result" class="result" role="status" aria-live="polite"></div>

<!--
<div class="meta">
<span class="pill">Runs offline</span>
<span class="pill">Saved model: model.pkl</span>
<span class="pill">Flask API: port 5000</span>
</div> 


<details>
<summary>API endpoints and example</summary>
<p>POST <code>/predict</code> with JSON:</p>
<pre>{"student_name":"Juan Dela Cruz","study_hours":7}</pre>
<p>GET <code>/health</code> checks the service and saved model.</p>
</details>
-->

</section>


<section class="card">
<div class="history-header">
<h2>Prediction History</h2>
<button type="button" id="clear-history" class="clear-btn">
Clear History
</button>
</div>

<p class="sub">
Your previous successful predictions are saved locally and remain
available after refreshing or restarting the application.
</p>

<div class="table-wrap">
<table>
<thead>
<tr>
<th>#</th>
<th>Student Name</th>
<th>Study Hours</th>
<th>Prediction</th>
<th>Date &amp; Time</th>
</tr>
</thead>
<tbody id="history-body">
<tr><td colspan="5" class="empty">Loading prediction history...</td></tr>
</tbody>
</table>
</div>

<p id="history-status" class="history-status" aria-live="polite"></p>
</section>

</main>

<script>
const form = document.getElementById('predict-form');
const box = document.getElementById('result');
const historyBody = document.getElementById('history-body');
const historyStatus = document.getElementById('history-status');
const clearButton = document.getElementById('clear-history');

form.addEventListener('submit', async e => {
    e.preventDefault();

    box.className = 'result';
    box.style.display = 'block';
    box.textContent = 'Calculating prediction...';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                student_name: document.getElementById('student_name').value,
                study_hours: Number(
                    document.getElementById('study_hours').value
                )
            })
        });

        const data = await response.json();

        if (!response.ok) {
            box.className = 'result error';
            box.textContent = data.error || 'Could not make prediction.';
            return;
        }

        // Display the successful prediction as formatted JSON.
        box.className = 'result';
        box.style.display = 'block';

        const output = {
            student_name: data.student_name,
            study_hours: data.study_hours,
            prediction: data.prediction
        };

        box.replaceChildren();
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(output, null, 4);
        box.appendChild(pre);

        // Refresh history after every successful prediction.
        await loadHistory();

    } catch (err) {
        box.className = 'result error';
        box.textContent =
            'Unable to contact the local API. Make sure app.py is running.';
    }
});

async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Unable to load history.');
        }

        historyBody.replaceChildren();

        if (data.history.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');

            cell.colSpan = 5;
            cell.className = 'empty';
            cell.textContent = 'No prediction history yet.';

            row.appendChild(cell);
            historyBody.appendChild(row);
        } else {
            data.history.forEach((item, index) => {
                const row = document.createElement('tr');

                addCell(row, index + 1);
                addCell(row, item.student_name);
                addCell(row, item.study_hours + ' hours');

                const predictionCell = document.createElement('td');
                const badge = document.createElement('span');

                badge.className = 'badge badge-' +
                    String(item.prediction).toLowerCase();
                badge.textContent = item.prediction;

                predictionCell.appendChild(badge);
                row.appendChild(predictionCell);

                addCell(row, item.timestamp);

                historyBody.appendChild(row);
            });
        }

        historyStatus.textContent =
            'Total predictions: ' + data.history.length;

    } catch (err) {
        historyStatus.textContent = 'Could not load prediction history.';
    }
}

function addCell(row, value) {
    const cell = document.createElement('td');
    cell.textContent = String(value);
    row.appendChild(cell);
}

clearButton.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to clear all prediction history?')) {
        return;
    }

    clearButton.disabled = true;
    historyStatus.textContent = 'Clearing prediction history...';

    try {
        const response = await fetch('/history/clear', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Unable to clear history.');
        }

        // Refresh the table, then restore the form for the next student.
        await loadHistory();
        form.reset();

        // Clear the previous prediction message.
        box.className = 'result';
        box.style.display = 'none';
        box.textContent = '';

        // Keep the input fields enabled and focus the student name field.
        document.getElementById('student_name').disabled = false;
        document.getElementById('study_hours').disabled = false;
        document.querySelector('#predict-form button[type="submit"]').disabled = false;
        historyStatus.textContent = 'Prediction history cleared successfully. You can enter a new student.';
        document.getElementById('student_name').focus();

    } catch (err) {
        console.error('Clear history error:', err);
        historyStatus.textContent = 'Could not clear prediction history.';
        alert(err.message || 'Unable to clear history. Please try again.');
    } finally {
        clearButton.disabled = false;
    }
});

// Load saved history when the page opens.
loadHistory();
</script>

</body>
</html>"""


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Saved model model.pkl was not found. Run `python train_model.py` first."
        )

    with MODEL_PATH.open("rb") as file:
        bundle = pickle.load(file)

    return bundle["model"]


# NEW: Read prediction history from a local JSON file.
def read_history():
    if not HISTORY_PATH.exists():
        return []

    try:
        with HISTORY_PATH.open("r", encoding="utf-8") as file:
            history = json.load(file)

        return history if isinstance(history, list) else []

    except (json.JSONDecodeError, OSError):
        return []


# NEW: Save prediction history to a local JSON file.
def save_history(history):
    with HISTORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/health")
def health():
    try:
        load_model()

        return jsonify({
            "status": "ok",
            "model_loaded": True,
            "model_file": MODEL_PATH.name
        })

    except Exception as exc:
        return jsonify({
            "status": "error",
            "model_loaded": False,
            "error": str(exc)
        }), 503


# EXISTING: Prediction endpoint, now also records successful predictions.
@app.post("/predict")
def predict():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    name = payload.get("student_name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "error": "student_name is required and must be a non-empty string."
        }), 400

    name = name.strip()

    if len(name) > 100:
        return jsonify({
            "error": "student_name must be 100 characters or fewer."
        }), 400

    raw_hours = payload.get("study_hours")

    if isinstance(raw_hours, bool):
        return jsonify({
            "error": "study_hours must be a number from 0 to 24."
        }), 400

    try:
        hours = float(raw_hours)

    except (TypeError, ValueError):
        return jsonify({
            "error": "study_hours must be a number from 0 to 24."
        }), 400

    if not 0 <= hours <= 24:
        return jsonify({
            "error": "study_hours must be between 0 and 24."
        }), 400

    try:
        model = load_model()
        prediction = str(model.predict([[hours]])[0]).upper()

    except Exception as exc:
        return jsonify({
            "error": f"Prediction failed: {exc}"
        }), 500

    # NEW: Record the successful prediction.
    record = {
        "student_name": name,
        "study_hours": hours,
        "prediction": prediction,
        "timestamp": datetime.now().astimezone().strftime(
            "%Y-%m-%d %I:%M:%S %p %Z"
        )
    }

    try:
        history = read_history()

        # Most recent prediction appears first.
        history.insert(0, record)
        save_history(history)

    except OSError as exc:
        app.logger.exception("Could not save prediction history.")
        return jsonify({
            "error": f"Prediction was made, but history could not be saved: {exc}"
        }), 500

    return jsonify({
        "student_name": name,
        "study_hours": hours,
        "prediction": prediction
    })


# NEW: Return all saved predictions.
@app.get("/history")
def prediction_history():
    return jsonify({
        "history": read_history()
    })


# NEW: Clear saved prediction history.
@app.post("/history/clear")
def clear_history():
    try:
        save_history([])

        return jsonify({
            "message": "Prediction history cleared successfully."
        })

    except OSError as exc:
        app.logger.exception("Could not clear prediction history.")

        return jsonify({
            "error": f"Could not clear history: {exc}"
        }), 500


if __name__ == "__main__":
    # Open the local web interface automatically when launched as a desktop app.
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    # Local-only server; no internet connection is required.
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
