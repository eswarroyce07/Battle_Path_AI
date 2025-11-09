from pathlib import Path

# Rendering
CELL_SIZE = 28
MARGIN = 2
FPS = 60

# Model
RISK_WEIGHT_SAFE = 4.0   # used in 'Safest' mode
RISK_WEIGHT_FAST = 0.8   # used in 'Fastest' mode
RISK_DECAY = 0.9         # exponential decay base for risk falloff
RISK_MAX = 10.0          # max risk inside enemy range
DIAGONAL_MOVES = False   # keep grid-4 connectivity (Manhattan)
DEFAULT_MAP = Path(__file__).resolve().parent.parent / "data" / "map1.json"
SEED = 42
