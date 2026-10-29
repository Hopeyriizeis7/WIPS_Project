import pandas as pd

# Only pull the columns we actually need, out of 254, this is what keeps memory sane.
cols = [
    "frame.time_epoch", "wlan.sa", "wlan.fc.type", "wlan.fc.subtype",
    "wlan_radio.signal_dbm", "radiotap.dbm_antsignal", "Label",
]

raw = pd.read_csv("Deauth_32.csv", usecols=cols, low_memory=False)
print("Raw packets loaded:", len(raw))
print(raw["Label"].value_counts())        # sanity check: what labels actually appear
print(raw["wlan.fc.subtype"].value_counts().head(10))  # sanity check: how subtype is stored

# Drop rows with no sender address or no timestamp, nothing to group them by
raw = raw.dropna(subset=["wlan.sa", "frame.time_epoch"])

# Combine the two possible signal-strength columns (one is often mostly empty)
raw["signal"] = raw["wlan_radio.signal_dbm"].fillna(raw["radiotap.dbm_antsignal"])

# Bucket each packet into its 1-second window
raw["time_bucket"] = raw["frame.time_epoch"].astype(float).astype(int)

# Was this packet a deauthentication frame? (subtype 12)
raw["is_deauth"] = pd.to_numeric(raw["wlan.fc.subtype"], errors="coerce") == 12

# Group: one row per (device, second)
grouped = raw.groupby(["wlan.sa", "time_bucket"]).agg(
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
print(grouped.head())

print(grouped[grouped["label"] == 1][["mac", "frames_per_sec", "deauth_per_sec", "signal_strength"]])
