from pathlib import Path
import csv
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"

def read_dataset():
    hours, labels = [], []
    with DATASET_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"study_hours", "result"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("dataset.csv must contain study_hours and result columns.")
        for row in reader:
            hours.append([float(row["study_hours"])])
            label = row["result"].strip().upper()
            if label not in {"PASS", "FAIL"}:
                raise ValueError(f"Invalid result label: {label}")
            labels.append(label)
    if len(hours) < 20:
        raise ValueError(f"Dataset must contain at least 20 records; found {len(hours)}.")
    if len(set(labels)) < 2:
        raise ValueError("Dataset must contain both PASS and FAIL examples.")
    return hours, labels

def main():
    X, y = read_dataset()
    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(X, y)
    with MODEL_PATH.open("wb") as file:
        pickle.dump({"model": model, "feature": "study_hours", "labels": ["FAIL", "PASS"]}, file)
    predictions = model.predict(X)
    print(f"Training records: {len(X)}")
    print(f"Training accuracy (not a measure of real-world reliability): {accuracy_score(y, predictions):.1%}")
    print(f"Saved trained model to: {MODEL_PATH}")
    print("The API loads this saved file and does not retrain the model at startup.")

if __name__ == "__main__":
    main()
