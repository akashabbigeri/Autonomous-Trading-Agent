import logging
import traceback
from mable.cargo_bidding import TradingCompany
from mable.transport_operation import Bid, ScheduleProposal
from mable.examples import environment, fleets

# Set up logging to see exactly what the agent is doing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Company6(TradingCompany):
    def __init__(self, fleet, name):
        super().__init__(fleet, name)
        # STRATEGY ADJUSTMENT:
        # We were losing money because our bids were too low.
        # We now set a 10% profit margin to ensure a safety cushion.
        self._profit_factor = 1.10 

    def pre_inform(self, trades, time):
        pass

    def inform(self, trades, *args, **kwargs):
        """
        The Bidding Phase.
        """
        try:
            # Calculate feasible schedules
            proposal = self.propose_schedules(trades)
            
            bids = []
            for trade in proposal.scheduled_trades:
                if trade in proposal.costs:
                    estimated_cost = proposal.costs[trade]
                    
                    # BIDDING STRATEGY:
                    # Bid = High Estimated Cost * Profit Margin
                    bid_amount = estimated_cost * self._profit_factor
                    
                    bids.append(Bid(amount=bid_amount, trade=trade))
            
            if len(bids) > 0:
                logger.info(f"Company6 placing {len(bids)} bids. (Example Bid: {bids[0].amount:.2f})")
            else:
                logger.warning("Company6 found NO feasible trades to bid on this round.")
                
            return bids
            
        except Exception as e:
            logger.error(f"CRITICAL ERROR IN INFORM: {e}")
            # Return empty list to keep simulation alive instead of crashing
            return []

    def receive(self, contracts, auction_ledger=None, *args, **kwargs):
        """
        The Execution Phase.
        """
        try:
            won_trades = [c.trade for c in contracts]
            
            if won_trades:
                logger.info(f"VICTORY: Won {len(won_trades)} contracts! Scheduling now...")
                
                # Re-run the scheduler for the trades we actually won
                proposal = self.propose_schedules(won_trades)
                
                # CRITICAL: Apply the schedules to the fleet
                rejected = self.apply_schedules(proposal.schedules)
                
                if rejected:
                    logger.error(f"CRITICAL: Failed to schedule {len(rejected)} won trades!")
                    
        except Exception as e:
            logger.error(f"CRITICAL ERROR IN RECEIVE: {e}")
            traceback.print_exc()

    def propose_schedules(self, trades):
        """
        The Scheduling Brain (Insertion Heuristic)
        """
        schedules = {}
        scheduled_trades = []
        costs = {}

        # Loop through every trade opportunity
        for trade in trades:
            best_schedule = None
            best_vessel = None
            lowest_cost = float('inf')

            for vessel in self.fleet:
                # Use current schedule or the one we are building
                current_schedule = schedules.get(vessel, vessel.schedule)
                
                insertion_points = current_schedule.get_insertion_points()
                
                for pickup_idx in insertion_points:
                    # Valid dropoff must be after pickup
                    valid_dropoffs = [x for x in insertion_points if x >= pickup_idx]
                    
                    for dropoff_idx in valid_dropoffs:
                        # Create candidate schedule
                        candidate = current_schedule.copy()
                        candidate.add_transportation(trade, pickup_idx, dropoff_idx)
                        
                        # Verify feasibility (Time & Capacity)
                        if candidate.verify_schedule():
                            cost = self._calculate_robust_cost(vessel, trade)
                            
                            if cost < lowest_cost:
                                lowest_cost = cost
                                best_schedule = candidate
                                best_vessel = vessel

            if best_schedule:
                schedules[best_vessel] = best_schedule
                scheduled_trades.append(trade)
                costs[trade] = lowest_cost

        return ScheduleProposal(schedules, scheduled_trades, costs)

    def _calculate_robust_cost(self, vessel, trade):
        """
        Calculates cost with a MASSIVE safety buffer.
        Previous runs showed we underestimated costs by ~20-30%.
        """
        # 1. Basic Fuel Costs (Loading/Unloading)
        loading_time = vessel.get_loading_time(trade.cargo_type, trade.amount)
        unloading_time = vessel.get_loading_time(trade.cargo_type, trade.amount) 
        
        load_cost = vessel.get_loading_consumption(loading_time)
        unload_cost = vessel.get_unloading_consumption(unloading_time)

        # 2. Laden Travel Cost (Pickup -> Dropoff)Q
        # This is accurate because we know the exact ports
        dist = self.headquarters.get_network_distance(trade.origin_port, trade.destination_port)
        travel_time = vessel.get_travel_time(dist)
        travel_cost = vessel.get_laden_consumption(travel_time, vessel.speed)

        base_cost = load_cost + unload_cost + travel_cost
        
        # 3. The "Hammer" Buffer
        # We multiply by 1.5 (50% markup) to cover the cost of getting the ship
        # to the pickup point (Ballast). This is aggressive but safe.
        total_cost = base_cost * 1.50
        
        return total_cost

if __name__ == '__main__':
    # Setup Simulation
    specifications_builder = environment.get_specification_builder(environment_files_path=".")
    fleet = fleets.example_fleet_1()
    
    # Add Agent
    specifications_builder.add_company(Company6.Data(Company6, fleet, "Company 6 Shipping"))
    
    print("Initializing Simulation...")
    sim = environment.generate_simulation(specifications_builder)
    
    print("Running Simulation...")
    sim.run()
    print("--- Simulation Finished ---")