import numpy as np
import pandas as pd

rng = np.random.default_rng(42)   # random number generator; the 42 makes results repeatable

n_normal = 800
n_attack = 200

# Normal devices
normal = pd.DataFrame({
    "frames_per_sec": rng.integers(5, 80, n_normal),
    "deauth_per_sec": rng.integers(0, 2, n_normal),      # 0 or 1
    "signal_strength": rng.normal(-60, 10, n_normal),    # average -60, spread 10
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