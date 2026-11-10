"""Quick smoke test for v2.0 model improvements."""
import pandas as pd
import numpy as np
from data.mock_generator import BovineSyntheticDataGenerator
from models.strategy import BovineQuantitativeStrategy

print("Generating mock data...")
gen = BovineSyntheticDataGenerator(seed=42)
mdata = gen.generate_full_market_history()
print(f"Market data symbols: {list(mdata.keys())}")

strat = BovineQuantitativeStrategy(enable_ml=False)
sig = strat.generate_signals(mdata, "LE=F")
print(f"Signals shape: {sig.shape}")
print(f"Columns: {list(sig.columns)}")
print(f"Target weight sample: {sig['target_weight'].tail(5).values}")
print(f"Kelly fraction sample: {sig['kelly_fraction'].tail(5).values}")
print(f"Corn velocity factor present: {'corn_velocity' in sig.columns}")
print("SMOKE TEST PASSED")
