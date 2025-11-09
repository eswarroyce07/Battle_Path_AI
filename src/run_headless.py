from grid import Grid
from threat import compute_risk
from astar import astar, manhattan
import config, random


def load_map(path):
    g = Grid.from_json(str(path))
    meta = g.meta
    start = tuple(meta.get("start", [g.rows-1, 0]))
    goal = tuple(meta.get("goal", [0, g.cols-1]))
    enemies = [tuple(e) for e in meta.get("enemies", [])]
    return g, start, goal, enemies


def randomize_enemies(grid: Grid, k=3):
    enemies = []
    for _ in range(k):
        r = random.randrange(grid.rows)
        c = random.randrange(grid.cols)
        rng = random.randint(3, 6)
        enemies.append((r, c, rng))
    return enemies


def risk_weight(mode: str):
    return config.RISK_WEIGHT_SAFE if mode == "SAFEST" else config.RISK_WEIGHT_FAST


seed = getattr(config, "SEED", None)
if seed is not None:
    random.seed(seed)

grid, start, goal, enemies = load_map(config.DEFAULT_MAP)
if not enemies:
    enemies = randomize_enemies(grid, k=3)

mode = "SAFEST"

risk = compute_risk(grid, enemies, config.RISK_DECAY, config.RISK_MAX)

def passable(r, c):
    return grid.cells[r][c].terrain != "BLOCKED"

def neighbors(r, c):
    return grid.neighbors4(r, c)

def move_cost(a, b):
    r, c = b
    return grid.cells[r][c].cost + risk_weight(mode) * risk[r][c]

path, total = astar(start, goal, passable, neighbors, move_cost, manhattan)

print("total:", total)
print("path_len:", len(path) if path else 0)
print("first_20:", path[:20] if path else None)
print("start:", start, "goal:", goal)
print("risk_start:", round(risk[start[0]][start[1]], 3), "risk_goal:", round(risk[goal[0]][goal[1]], 3))
