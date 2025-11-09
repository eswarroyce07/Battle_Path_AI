# BattlePath AI – Tactical Pathfinding Simulator

A simple, resume-ready AI project simulating a battlefield and computing the **safest path** using A* with a risk-aware cost.

## Quick Start

1. (Optional) Create & activate virtual environment:
   - `python -m venv .venv`
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

2. Install:
   - `pip install -r requirements.txt`

3. Run:
   - `python src/main.py`

## Controls
- `R` : Randomize enemy positions & recompute
- `T` : Toggle mode (Safest <-> Fastest)
- `N` : Regenerate simple terrain
- `SPACE` : Animate troop movement along current path
- `ESC` / `Q` : Quit

## Project idea
- Grid/graph battlefield with terrain costs and enemy threat zones
- A* pathfinding with risk-weighted cost
- Optional: Q-Learning/DQN extension (stub provided)
