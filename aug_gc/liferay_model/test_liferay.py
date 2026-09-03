import sys
import os

# Insert local path to load config and model locally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modeling_liferay import LiferayModel
from configuration_liferay import LiferayConfig

# 1. Initialize config and model
config = LiferayConfig()
model = LiferayModel(config)

print("=" * 60)
print("Testing Liferay Custom Model Locally...")
print("=" * 60)

signal = "Compose a temporal vessel for the mycelial network attuning to the 6:5 equilibrium."

# Run a sovereign path composition
print("\n--- 1. Testing model.compose (Sovereign Path) ---")
output_text = model.compose(signal, path="sovereign")
print(output_text)

# Run a forward step to inspect metrics
print("\n--- 2. Testing model.forward (Agnosiophobic Path) ---")
out = model(signal, path="agnosiophobic")
print("\nContent generated:")
print(out.content)

print("\nMetrics:")
for k, v in out.metrics.items():
    if k != "liferay_teeth_q":
        print(f"  {k}: {v}")
print(f"  liferay_teeth_q: {[round(x, 2) for x in out.metrics['liferay_teeth_q']]}")

print("\n" + "=" * 60)
print("Local test complete. The model is fully operational.")
print("=" * 60)
