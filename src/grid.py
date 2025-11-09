from dataclasses import dataclass
from typing import List, Dict
import json, random

Terrain = str

COLORS = {
    "OPEN": (230, 230, 220),
    "FOREST": (120, 170, 120),
    "URBAN": (190, 190, 190),
    "WATER": (120, 160, 200),
    "MOUNTAIN": (180, 150, 100),
    "BLOCKED": (40, 40, 40),
}

@dataclass
class Cell:
    r: int
    c: int
    terrain: Terrain = "OPEN"
    cost: float = 1.0

class Grid:
    def __init__(self, rows: int, cols: int, terrain_costs: Dict[Terrain, float]):
        self.rows, self.cols = rows, cols
        self.terrain_costs = terrain_costs
        self.cells: List[List[Cell]] = [
            [Cell(r, c, "OPEN", terrain_costs["OPEN"]) for c in range(cols)]
            for r in range(rows)
        ]

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r") as f:
            data = json.load(f)
        grid = cls(data["rows"], data["cols"], data["terrain"])
        # Create some example patches for terrain variety
        random.seed(123)
        for _ in range(int(grid.rows * grid.cols * 0.08)):
            r = random.randrange(grid.rows)
            c = random.randrange(grid.cols)
            t = random.choice(["FOREST", "URBAN", "MOUNTAIN"])
            grid.set_terrain(r, c, t)
        # carve a river
        rr = grid.rows // 2
        for c in range(grid.cols // 3, grid.cols // 3 + 5):
            if 0 <= rr < grid.rows:
                grid.set_terrain(rr, c, "WATER")
                if rr+1 < grid.rows:
                    grid.set_terrain(rr+1, c, "WATER")
        grid.meta = data
        return grid

    def set_terrain(self, r: int, c: int, t: Terrain):
        cell = self.cells[r][c]
        cell.terrain = t
        cell.cost = self.terrain_costs[t]

    def neighbors4(self, r: int, c: int):
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                yield nr, nc

    def terrain_color(self, r: int, c: int):
        return COLORS[self.cells[r][c].terrain]
