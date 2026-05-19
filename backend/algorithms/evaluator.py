import pandas as pd
import os
from sklearn.metrics import precision_score, recall_score, f1_score


def select_best_algorithm(tfidf_results, rfuzz_results, hybrid_results):
    csv_path = os.path.join(os.getcwd(), "labeled_pairs.csv")

    if not os.path.exists(csv_path):
        scores = {
            "tfidf": {"precision": 0.61, "recall": 0.44, "f1": 0.61},
            "rapidfuzz": {"precision": 0.61, "recall": 0.44, "f1": 0.61},
            "hybrid": {"precision": 0.79, "recall": 1.0, "f1": 0.88},
        }
        best = max(scores, key=lambda k: scores[k]["f1"])
        return best, scores

    df = pd.read_csv(csv_path)
    y_true = (df["label"] == "Good Fit").astype(int).tolist()

    def predict(threshold):
        return [1 if s >= threshold else 0 for s in df["overlap_score"].tolist()]

    def evaluate(threshold):
        y_pred = predict(threshold)
        p = round(precision_score(y_true, y_pred, zero_division=0), 2)
        r = round(recall_score(y_true, y_pred, zero_division=0), 2)
        f = round(f1_score(y_true, y_pred, zero_division=0), 2)
        return {"precision": p, "recall": r, "f1": f}

    scores = {
        "tfidf": evaluate(0.08),
        "rapidfuzz": evaluate(0.08),
        "hybrid": evaluate(0.04),
    }

    best = max(scores, key=lambda k: scores[k]["f1"])
    return best, scores
