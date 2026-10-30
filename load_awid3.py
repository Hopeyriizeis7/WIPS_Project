import pandas as pd

cols = [
    "frame.time_epoch", "wlan.sa", "wlan.fc.type", "wlan.fc.subtype",
    "wlan_radio.signal_dbm", "radiotap.dbm_antsignal", "Label",
]

files = ["Deauth_32.csv", "Deauth_0.csv", "Deauth_15.csv", "Deauth_29.csv"]   # adjust paths if needed

all_raw = []
for f in files:
    chunk = pd.read_csv(f, usecols=cols, low_memory=False)
    chunk["source_file"] = f
    all_raw.append(chunk)
    print(f, "loaded:", len(chunk), "packets")

raw = pd.concat(all_raw, ignore_index=True)
print("\nTotal packets:", len(raw))
print(raw["Label"].value_counts())

raw = raw.dropna(subset=["wlan.sa", "frame.time_epoch"])
raw["signal"] = raw["wlan_radio.signal_dbm"].fillna(raw["radiotap.dbm_antsignal"])
raw["time_bucket"] = raw["frame.time_epoch"].astype(float).astype(int)
raw["is_deauth"] = pd.to_numeric(raw["wlan.fc.subtype"], errors="coerce") == 12
print(raw.groupby("source_file")["Label"].value_counts())

grouped = raw.groupby(["wlan.sa", "time_bucket", "source_file"]).agg(
    frames_per_sec=("wlan.sa", "size"),
    deauth_per_sec=("is_deauth", "sum"),
    signal_strength=("signal", "mean"),
    label_text=("Label", lambda s: s.iloc[0]),
).reset_index()

grouped["label"] = (grouped["label_text"].str.strip().str.lower() != "normal").astype(int)
grouped = grouped.rename(columns={"wlan.sa": "mac"})
grouped["deauth_ratio"] = grouped["deauth_per_sec"] / grouped["frames_per_sec"].clip(lower=1)

grouped.to_csv("awid3_features.csv", index=False)
print("\nFinal feature rows:", len(grouped))
print(grouped["label"].value_counts())