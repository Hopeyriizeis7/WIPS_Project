import streamlit as st
import pandas as pd
from my_data import load_real_data, split_data, train_model, evaluate_model

st.set_page_config(page_title="WIPS Dashboard", layout="wide")
st.title("WIPS: Deauth Flood Detection Dashboard")
st.caption("Live demonstration — Hope Mbugua, BCNS, Wireless and Mobile Security")

# @st.cache_resource means: run this once, keep the result, don't retrain every time
# Streamlit re-runs your whole script on every interaction, so without caching
# you'd retrain the model every time you click anything.
@st.cache_resource
def get_model_and_data():
    data = load_real_data()
    X_train, X_test, y_train, y_test = split_data(data)
    model = train_model(X_train, y_train)
    return model, X_test, y_test

model, X_test, y_test = get_model_and_data()
predictions = model.predict(X_test)

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", f"{(predictions == y_test).mean() * 100:.2f}%")
col2.metric("Test rows", len(X_test))
col3.metric("Attacks in test set", int(y_test.sum()))

st.subheader("Confusion Matrix")
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, predictions)
cm_df = pd.DataFrame(cm, index=["Actual Normal", "Actual Attack"], columns=["Predicted Normal", "Predicted Attack"])
st.dataframe(cm_df)

import time
from sklearn.model_selection import train_test_split

st.subheader("Live Detection")

# Re-create the same test split, but keeping the full row (including mac)
# this uses the same random_state/test_size as split_data, so it's the same rows
data = load_real_data()
_, test_full = train_test_split(data, test_size=0.25, random_state=42, stratify=data["label"])

FEATURES = ["frames_per_sec", "deauth_per_sec", "signal_strength", "deauth_ratio"]

if st.button("Start Live Detection"):
    blocked = set()
    alerts = []
    feed = st.empty()          # a placeholder we keep overwriting
    counter = st.empty()

    for _, row in test_full.iterrows():
        mac = row["mac"]
        if mac in blocked:
            continue

        features = pd.DataFrame([row[FEATURES]])
        result = model.predict(features)[0]

        if result == 1:
            blocked.add(mac)
            alerts.append({
                "MAC": mac,
                "Deauth/sec": row["deauth_per_sec"],
                "Action": "BLOCKED",
            })
            feed.dataframe(pd.DataFrame(alerts))
            counter.metric("Attackers blocked", len(blocked))
            time.sleep(0.3)   # small pause so it visibly streams in, not an instant dump

    st.success(f"Detection run finished. {len(blocked)} attackers blocked.")