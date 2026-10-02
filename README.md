# Autonomous Trading Agent

An autonomous cargo-trading agent for the **MABLE** maritime shipping competition, built for the University of Southampton **COMP6203 – Intelligent Agents** coursework (Group 6).

The agent runs a shipping company. Each auction round it is offered cargo trades (origin port, destination port, cargo type and amount, time windows). It has to decide which trades to bid on and at what price. It also has to schedule its vessels so that the contracts it wins are delivered on time. Profit is revenue minus fuel cost minus penalties for missed contracts.

## Strategy: feasibility first

The agent (`Company6` in [`group6.py`](group6.py)) has three stages:

1. **Schedule proposal.** A greedy insertion heuristic tries every valid pickup and drop-off position in every vessel's schedule for each offered trade. It keeps only insertions that pass `verify_schedule()` (time windows and capacity), then picks the cheapest.
2. **Bidding.** Cost-plus pricing. The estimated cost of a trade is its loading and unloading fuel plus the laden-leg fuel, multiplied by a **1.5× robustness buffer**. This buffer stands in for ballast repositioning and timing uncertainty. The bid is that cost multiplied by a further **1.10 profit factor**.
3. **Execution.** For the trades it actually wins, the agent re-runs the scheduler and applies the schedules to its fleet.

The agent only bids on trades it can already fit into a feasible schedule, so it takes on very few commitments it can't deliver.

## Results

Findings from the metrics logs:

- **Reliable.** Contracts are executed with few or no penalties, which avoids the large fines that sank the more aggressive opponents.
- **Not yet profitable.** Average net income across runs is negative. The marginal-cost estimate misses ballast repositioning and schedule coupling, and the agent doesn't enforce a minimum margin or price in opportunity cost.
- **Planned improvements:** route-aware marginal costing, opportunity-cost and knapsack-style trade selection, adaptive mark-ups driven by fleet slack, local-search refinement (swap/relocate), and explicit pricing of uncertainty.

## Repository layout

```
.
├── group6.py                         # The agent (Company6) plus a standalone single-company run
├── run_tournament.py                 # Plays N matches against a fixed-price dummy opponent
├── main_competition_playground.py    # 3-company playground (vs. MyArchEnemy and TheScheduler)
├── analyze_results.py                # Prints a profit/revenue/penalty report from the latest metrics JSON
├── debug_keys.py                     # Prints the structure of a metrics JSON
└── results/
    └── metrics/                      # Sample metrics_competition_*.json logs from simulation runs
```

## Setup

You need Python 3 and the **MABLE** framework (`mable`) as provided by the course. The simulator also needs the course resource pack. It is not in this repo because the routing pickles are over 100 MB. Unpack it so these files sit next to the scripts:

```
ports.csv
port_cargo_weight_distribution.csv
port_trade_frequency_distribution.csv
time_transition_distribution.csv
precomputed_routes.pickle
routing_graph_world_mask.pkl
```

The scripts pass `environment_files_path="."`, so these files must be in the directory you run from.

## Usage

```bash
# Run the agent alone in the default environment
python group6.py

# Play 3 matches against a dummy opponent that bids a flat 5000 on every trade
python run_tournament.py

# Run the 12-auction, 3-company playground
python main_competition_playground.py

# Summarise the most recent metrics_competition_*.json in the current directory
python analyze_results.py
```

Each simulation writes a `metrics_competition_<id>_<timestamp>.json` file. `analyze_results.py` reads the newest one, so to analyse the bundled samples run it from `results/metrics/` (the script looks for the company name "Group 6" and falls back to the first company).

## Tuning

The two main parameters are in `group6.py`:

| Parameter | Where | Current value | Effect |
|---|---|---|---|
| `_profit_factor` | `Company6.__init__` | `1.10` | Mark-up applied on top of the estimated cost when bidding |
| Cost buffer | `_calculate_robust_cost` | `1.50` | Safety multiplier on base fuel cost, covering ballast legs and timing noise |

Raising either makes the agent safer but less competitive. Lowering them wins more contracts, but more of them lose money.

## Notes

- The sample metrics logs from the dummy-opponent tournament label the agent "Group 6 (Hero)".
- `run_tournament.py` and `main_competition_playground.py` originally imported `grp6` and the template placeholder `groupn`. They now import `group6.Company6`.
