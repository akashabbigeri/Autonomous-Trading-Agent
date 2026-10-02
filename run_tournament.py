import logging
from mable.examples import environment, fleets
from mable.cargo_bidding import TradingCompany
from mable.transport_operation import Bid

# 1. Import 'Company6' from 'group6'
try:
    from group6 import Company6
except ImportError:
    print("Error: Could not find 'group6.py'. Make sure both files are in the same folder!")
    exit()

# 2. Define a 'Safe' Dummy Opponent
class DummyOpponent(TradingCompany):
    def inform(self, trades, *args, **kwargs):
        bids = []
        for trade in trades:
            # Bids a flat 5000 on everything
            bids.append(Bid(amount=5000, trade=trade))
        return bids
    
    def receive(self, contracts, auction_ledger=None, *args, **kwargs):
        pass 

def run_tournament():
    NUM_MATCHES = 3
    print(f" INITIALIZING TOURNAMENT ({NUM_MATCHES} Matches) ")
    print("-" * 40)

    for i in range(NUM_MATCHES):
        print(f"\n--- MATCH {i+1} ---")
        
        builder = environment.get_specification_builder(environment_files_path=".")
        
        # TEAM A: Your Agent (Fixed Class Name)
        fleet_1 = fleets.example_fleet_1() 
        # We use Company6 here because that is what you named it in group6.py
        builder.add_company(Company6.Data(Company6, fleet_1, "Group 6 (Hero)"))
        
        # TEAM B: The Dummy Opponent
        fleet_2 = fleets.example_fleet_2()
        builder.add_company(DummyOpponent.Data(DummyOpponent, fleet_2, "Dummy Corp"))
        
        try:
            sim = environment.generate_simulation(builder)
            sim.run()
        except Exception as e:
            print(f"Match crashed: {e}")
        
    print("\n" + "="*40)
    print("🏆 TOURNAMENT FINISHED")

if __name__ == '__main__':
    run_tournament()