"""
Offline & Online Training script for Demand Prediction.
Calculates empirical demand weights from historical order CSV logs.
"""

import os
import json
import pandas as pd
from typing import Dict

def train_demand_model(dataset_path: str = None, output_model_path: str = None) -> Dict[int, float]:
    current_dir = os.path.dirname(os.path.dirname(__file__))
    if dataset_path is None:
        dataset_path = os.path.join(current_dir, "datasets", "historical_orders.csv")
    if output_model_path is None:
        output_model_path = os.path.join(current_dir, "models", "sample_models.json")
        
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    
    weights = {}
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        item_counts = df.groupby("item_id")["quantity"].sum().to_dict()
        total_items = len(item_counts)
        avg_count = sum(item_counts.values()) / max(1, total_items)
        
        for item_id, count in item_counts.items():
            # Normalized weight centered around 1.0
            ratio = count / max(1.0, avg_count)
            weights[int(item_id)] = round(max(0.5, min(2.0, ratio)), 3)
    else:
        # Fallback default weights
        for i in range(1, 21):
            weights[i] = round(1.0 + ((i % 5) - 2) * 0.1, 2)
            
    # Save to model registry
    model_data = {}
    if os.path.exists(output_model_path):
        try:
            with open(output_model_path, "r") as f:
                model_data = json.load(f)
        except Exception:
            model_data = {}
            
    model_data["demand_weights"] = weights
    with open(output_model_path, "w") as f:
        json.dump(model_data, f, indent=2)
        
    return weights

if __name__ == "__main__":
    trained_weights = train_demand_model()
    print(f"Demand model trained successfully with {len(trained_weights)} items.")
