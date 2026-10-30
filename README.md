# WIPS: Machine-Learning Deauthentication Flood Detection and Prevention

A Wireless Intrusion Prevention System (WIPS) prototype that classifies Wi-Fi
traffic with a Random Forest and automatically blocks devices flooding
deauthentication frames.

**Author:** Hope Mbugua (182174) — BCNS, Wireless and Mobile Security, Strathmore University

## What it does

- Reads Wi-Fi traffic features (frame rate, deauth rate, signal strength,
  deauth ratio) for a device in a given second.
- Trains a Random Forest classifier (scikit-learn) to label traffic normal
  or attack.
- Reports accuracy and a confusion matrix.
- Replays traffic live, raises an alert on a detected deauth flood, and
  blocks the offending MAC address (the WIPS action).
- Includes a live Streamlit dashboard for demonstrations.

## Files

| File | What it does |
|---|---|
| `my_data.py` | Main pipeline: train, evaluate, live-detect, alert, block |
| `load_awid3.py` | Extracts per-device-per-second features from raw AWID3 packet captures |
| `dashboard.py` | Streamlit dashboard: stats + live detection feed |
| `awid3_features.csv` | Generated real-data feature set (not tracked in git — regenerate it, see below) |
| `blocklist.txt` | Output: MAC addresses blocked by the most recent run |
| `alerts.log` | Output: timestamped alert log |
| `confusion_matrix.png` | Output: saved confusion matrix chart |

## Setup

pip install pandas numpy scikit-learn matplotlib streamlit
## Running it

**1. Train and evaluate on synthetic data:**
Edit the `if __name__ == "__main__":` block in `my_data.py` to call
`make_data()` instead of `load_real_data()`, then:

python my_data.py
**2. Train and evaluate on real AWID3 data:**

First, regenerate the feature set from raw AWID3 captures. Place the
`Deauth_*.csv` files you're using (from the AWID3-CSV "1.Deauth" folder,
[University of the Aegean](https://icsdweb.aegean.gr/awid/awid3)) in this
folder, list them in the `files = [...]` line in `load_awid3.py`, then:

python load_awid3.py
This produces `awid3_features.csv`. Then, with `load_real_data()` set in
`my_data.py`'s main block:

python my_data.py
**3. Launch the live dashboard:**

streamlit run dashboard.py
Opens in your browser. Click "Start Live Detection" to watch alerts stream
in and attackers get blocked in real time.

## Results

- **Synthetic data** (1,050 rows, built to be cleanly separable):
  100% accuracy.
- **Real AWID3 data** (1,616 feature rows extracted from 5 Deauth capture
  files, 38 real attack windows): 99.01% accuracy, confusion matrix
  `[[393, 2], [2, 7]]` on a 404-row test set.

## How the AWID3 features were built

AWID3 provides one row per captured packet (254 columns). `load_awid3.py`:
1. Loads only the columns needed (sender MAC, timestamp, frame subtype,
   signal strength, ground-truth label) instead of all 254.
2. Groups packets into (device, second) windows.
3. Computes `frames_per_sec`, `deauth_per_sec` (frames with subtype 12),
   mean `signal_strength`, and `deauth_ratio` (deauth frames as a fraction
   of all frames that second) per window.
4. Labels a window "attack" if any packet in it carries AWID3's ground-truth
   attack label.

## Limitations

- The real-data sample is small and imbalanced (38 attacks of 1,616 rows,
  2.4%), consistent with how rare real attack windows are, but meaning the
  test set's attack count is limited.
- "Blocking" only appends a MAC to `blocklist.txt`. A deployed WIPS would
  need to enforce this on the access point or wireless controller.
- Classifies one second of traffic at a time, with no memory of a device's
  recent history.
- Source MAC addresses can be spoofed (seen in this data: attack packets
  sourced from the broadcast address `ff:ff:ff:ff:ff:ff`), so a production
  system should combine this with signal and sequence-number analysis, and
  802.11w where available.

## AI assistant use

I used Claude (Anthropic) as a coding assistant throughout this project,
working interactively in PyCharm. Claude explained the relevant Wi-Fi
security concepts, proposed the pipeline and feature-engineering approach
for AWID3's raw packet captures, and guided me step by step through writing
and debugging each function myself. Every line of code was written and run
by me, and I can explain how each part works during the live demonstration.
