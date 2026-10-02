import json
import glob
import os

# Find the latest file automatically
files = glob.glob("metrics_competition_*.json")
latest_file = max(files, key=os.path.getmtime)

print(f"Inspecting: {latest_file}")

with open(latest_file, 'r') as f:
    data = json.load(f)
    
    print("\n--- ROOT KEYS ---")
    print(list(data.keys()))
    
    print("\n--- METRICS KEYS ---")
    # Check what's inside the first company's metrics
    first_id = list(data["company_metrics"].keys())[0]
    print(list(data["company_metrics"][first_id].keys()))