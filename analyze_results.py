import json
import glob
import os

def load_latest_metrics():
    # Find all files matching the pattern
    files = glob.glob("metrics_competition_*.json")
    
    if not files:
        print("❌ No metrics files found! Run the simulation first.")
        return None
    
    # Sort by modification time (newest first)
    latest_file = max(files, key=os.path.getmtime)
    print(f"📂 Loading report: {latest_file}\n")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def generate_report():
    data = load_latest_metrics()
    if not data:
        return

    # 1. Identify our Company ID (usually "0")
    my_id = None
    my_name = "Group 6" # The name defined in your agent
    
    for cid, name in data.get("company_names", {}).items():
        if my_name in name:
            my_id = cid
            break
    
    if my_id is None:
        # Fallback: Just take the first company found
        my_id = list(data["company_names"].keys())[0]
        my_name = data["company_names"][my_id]

    # 2. Extract Financials
    metrics = data["company_metrics"][my_id]
    fuel_cost = metrics["fuel_cost"]
    
    # Penalties are often stored separately
    penalty = 0
    if "penalty" in data and my_id in data["penalty"]:
        penalty = data["penalty"][my_id]
    
    total_cost = fuel_cost + penalty

    # 3. Calculate Revenue from Won Auctions
    revenue = 0
    contracts_won = 0
    
    # auction_outcomes is a list of auction rounds
    for round_idx, auction_round in enumerate(data["auction_outcomes"]):
        if my_id in auction_round:
            # We won something in this round
            won_contracts = auction_round[my_id]
            for contract in won_contracts:
                revenue += contract["payment"]
                contracts_won += 1

    # 4. Final Calculations
    net_profit = revenue - total_cost
    margin = (net_profit / revenue * 100) if revenue > 0 else 0
    
    # --- PRINT THE DASHBOARD ---
    print("="*40)
    print(f"  🚢 PERFORMANCE REPORT: {my_name.upper()}  ")
    print("="*40)
    
    print(f"{'Metric':<25} | {'Value':>10}")
    print("-" * 40)
    print(f"{'Contracts Won':<25} | {contracts_won:>10}")
    print(f"{'Total Revenue':<25} | ${revenue:,.2f}")
    print(f"{'Fuel Costs':<25} | ${fuel_cost:,.2f}")
    print(f"{'Penalties':<25} | ${penalty:,.2f}")
    print("-" * 40)
    
    # Color-coded output for Profit
    profit_str = f"${net_profit:,.2f}"
    if net_profit > 0:
        print(f"{'NET PROFIT':<25} | \033[92m{profit_str}\033[0m") # Green
    else:
        print(f"{'NET PROFIT':<25} | \033[91m{profit_str}\033[0m") # Red
        
    print(f"{'Profit Margin':<25} | {margin:>9.2f}%")
    print("="*40)

    # 5. Strategy Insight
    if contracts_won == 0:
        print("\n⚠️  STRATEGY ALERT: You didn't win any contracts.")
        print("   - Check your Profit Factor (is it too high?).")
        print("   - Check your scheduling logic (are ships too busy?).")
    elif net_profit < 0:
        print("\n⚠️  STRATEGY ALERT: You are losing money.")
        print("   - You might be bidding below your actual cost.")
        print("   - Penalties might be eating your profits.")
    else:
        print("\n✅ STATUS: Operational and Profitable.")

if __name__ == "__main__":
    generate_report()