#!/usr/bin/env python3
"""Generate sample datasets for BattlePath AI training and testing."""

import json
import random
from pathlib import Path

def generate_random_map(rows=15, cols=20, enemy_count=3, seed=None):
    """Generate a random battlefield map."""
    if seed:
        random.seed(seed)
    
    terrain_types = ["OPEN", "FOREST", "URBAN", "WATER", "MOUNTAIN", "BLOCKED"]
    weights = [0.4, 0.2, 0.15, 0.1, 0.1, 0.05]  # Probability weights
    
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            terrain = random.choices(terrain_types, weights=weights)[0]
            row.append(terrain)
        grid.append(row)
    
    # Ensure start and goal are accessible
    start = [rows-1, random.randint(0, 2)]
    goal = [random.randint(0, 2), cols-1]
    grid[start[0]][start[1]] = "OPEN"
    grid[goal[0]][goal[1]] = "OPEN"
    
    # Generate enemies
    enemies = []
    for _ in range(enemy_count):
        r = random.randint(2, rows-3)
        c = random.randint(2, cols-3)
        rng = random.randint(3, 7)
        enemies.append([r, c, rng])
    
    return {
        "rows": rows,
        "cols": cols,
        "start": start,
        "goal": goal,
        "terrain": {
            "OPEN": 1.0,
            "FOREST": 2.0,
            "URBAN": 1.5,
            "WATER": 7.0,
            "MOUNTAIN": 5.0,
            "BLOCKED": 9999.0
        },
        "grid": grid,
        "enemies": enemies
    }

def create_sample_datasets():
    """Create multiple sample datasets."""
    data_dir = Path(__file__).parent
    
    # Generate 5 random maps for testing
    for i in range(1, 6):
        map_data = generate_random_map(
            rows=random.randint(10, 20),
            cols=random.randint(15, 25),
            enemy_count=random.randint(2, 5),
            seed=42 + i
        )
        
        filename = f"random_map_{i}.json"
        with open(data_dir / filename, 'w') as f:
            json.dump(map_data, f, indent=2)
        print(f"Generated {filename}")

if __name__ == "__main__":
    create_sample_datasets()