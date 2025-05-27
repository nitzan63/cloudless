import pandas as pd
import pickle
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def main():
    # This script fails validation because:
    # 1. No URL argument handling
    # 2. Hardcoded URL instead of accepting it as an argument
    csv_url = "https://example.com/dataset.csv"
    print(f"📥 Loading dataset from: {csv_url}")

    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return

    if 'target' not in df.columns:
        print("❌ Dataset must contain a 'target' column.")
        return

    X = df.drop(columns='target')
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("⚙️ Training Logistic Regression model...")
    model = LogisticRegression()
    model.fit(X_train, y_train)

    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("✅ model.pkl saved.")

    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0)
    }

    with open("metrics.json", "w") as f:
        json.dump(metrics, f)
    print("✅ metrics.json saved.")
    print("📊 Metrics:", json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main() 