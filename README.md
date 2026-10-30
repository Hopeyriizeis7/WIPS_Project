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
