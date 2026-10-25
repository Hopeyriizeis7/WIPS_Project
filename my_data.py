import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

rng = np.random.default_rng(42)
n_normal = 800
n_attack = 200

def make_data():
    # Normal devices
    normal = pd.DataFrame({
        "frames_per_sec": rng.integers(5, 80, n_normal),
        "deauth_per_sec": rng.integers(0, 2, n_normal),  # 0 or 1
        "signal_strength": rng.normal(-60, 10, n_normal),  # average -60, spread 10
        "label": 0,
    })

    # Attackers
    attack = pd.DataFrame({
        "frames_per_sec": rng.integers(60, 300, n_attack),
        "deauth_per_sec": rng.integers(50, 250, n_attack),
        "signal_strength": rng.normal(-55, 10, n_attack),
        "label": 1,
    })

    # Combine and shuffle
    data = pd.concat([normal, attack]).sample(frac=1, random_state=1).reset_index(drop=True)
    print(data.head(10))
    print(data["label"].value_counts())
    return data

def split_data(data):
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier

    # X = the inputs the model looks at, y = the answer we want it to predict
    X = data[["frames_per_sec", "deauth_per_sec", "signal_strength"]]
    y = data["label"]

    # Hold back 25% of rows that the model never sees during training
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y)

    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    # Create and train the Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Training rows:", len(X_train))
    return model

def evaluate_model(model, X_test, y_test):
    from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    # Ask the trained model to label the 250 rows it has never seen
    predictions = model.predict(X_test)

    # Compare its answers with the true labels
    acc = accuracy_score(y_test, predictions)
    print(f"Accuracy: {acc * 100:.2f}%")

    cm = confusion_matrix(y_test, predictions)
    print(cm)

    # Draw it
    disp = ConfusionMatrixDisplay(cm, display_labels=["normal", "attack"])
    disp.plot(cmap="Blues")
    plt.title("Confusion matrix")
    plt.savefig("confusion_matrix.png", dpi=150)
    return predictions

def run_live_detection(model, X_test):
    # Pretend the test rows are live traffic arriving one at a time
    blocked = set()  # MACs we have blocked

    open("blocklist.txt", "w").close()
    test_rows = X_test.copy()
    test_rows["mac"] = [f"AA:BB:CC:00:00:{i:02d}" for i in range(len(test_rows))]  # fake MACs

    for _, row in test_rows.iterrows():
        mac = row["mac"]
        if mac in blocked:
            continue  # already blocked, ignore

        features = pd.DataFrame([row[["frames_per_sec", "deauth_per_sec", "signal_strength"]]])
        result = model.predict(features)[0]

        if result == 1:  # which label means attack?
            print(f"[ALERT] Deauth flood from {mac} ({row['deauth_per_sec']:.0f} deauth frames/sec)")
            blocked.add(mac)
            with open("blocklist.txt", "a") as f:
                f.write(mac + "\n")
            print(f"        -> ACTION: {mac} blocked")

    print(f"\n{len(blocked)} attackers blocked")

if __name__ == "__main__":
    data = make_data()
    X_train, X_test, y_train, y_test = split_data(data)
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    run_live_detection(model, X_test)