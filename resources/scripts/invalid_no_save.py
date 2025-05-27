import sys
import pandas as pd
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def main():
    # This script fails validation because:
    # 1. Doesn't save model.pkl at all
    if len(sys.argv) < 2:
        print("❌ Please provide the CSV URL as the first argument.")
        sys.exit(1)

    csv_url = sys.argv[1]
    print(f"📥 Loading dataset from: {csv_url}")

    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        sys.exit(1)

    if 'target' not in df.columns:
        print("❌ Dataset must contain a 'target' column.")
        sys.exit(1)

    X = df.drop(columns='target')
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("⚙️ Training Logistic Regression model...")
    model = LogisticRegression()
    model.fit(X_train, y_train)
    print("✅ Model trained successfully!")

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