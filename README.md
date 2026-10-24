# WIPS prototype: deauthentication flood detection

A small Wireless Intrusion Prevention System that uses a scikit-learn Random Forest
to label Wi-Fi traffic as normal or a deauth flood, raises an alert, and blocks the
offending MAC address.

## Files

| File | What it does |
|---|---|
| `make_data.py` | Creates `traffic.csv`, a **synthetic** dataset (one row = one device in one second) |
| `wips.py` | Trains the model, reports accuracy and confusion matrix, then replays traffic and alerts/blocks |
| `traffic.csv` | Generated dataset |
| `confusion_matrix.png` | Output: confusion matrix for the poster |
| `feature_importance.png` | Output: which features the model relied on |
| `alerts.log` | Output: one line per alert |
| `blocklist.txt` | Output: MAC addresses the WIPS blocked |

## Run it

```
pip install pandas scikit-learn matplotlib numpy
python make_data.py
python wips.py
```

## How it works

1. **Features**: each row has `frames_per_sec`, `deauth_per_sec`, `deauth_ratio`,
   `mean_rssi` (signal strength), `rssi_std` (signal variation) and `unique_targets`.
2. **Model**: a Random Forest (100 decision trees voting) trained on 75% of the data.
3. **Evaluation**: tested on the 25% the model never saw. Accuracy and the confusion
   matrix are printed and saved as a PNG.
4. **Detection**: unseen rows are replayed one at a time like a live sniffer feed.
   Each is classified; an attack raises an `[ALERT]`.
5. **Prevention (WIPS)**: the attacker's MAC is appended to `blocklist.txt` and logged
   to `alerts.log`. Later traffic from a blocked MAC is dropped without classifying.

## Important limitations 

- The data is **synthetic**, so the ~99.8% accuracy is optimistic. Real traffic is
  messier, so expect lower numbers on AWID3.
- "Blocking" only writes the MAC to a file. A real WIPS would enforce it at the access point.
- It classifies each device-second independently and does not track behaviour over time.

## Next step: real data (AWID3)

Replace `traffic.csv` with features extracted from AWID3. `wips.py` only needs these
columns: `src_mac`, the six feature columns, and `label` (0 normal, 1 attack).
If AWID3 column names differ, edit the `FEATURES` list in `wips.py`.

