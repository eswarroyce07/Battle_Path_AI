import json, random, math
import pygame
from pathlib import Path
from grid import Grid
from threat import compute_risk
from astar import astar, manhattan
import config
from utils import seed_all

def load_map(path: Path):
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

def compute_path(grid: Grid, start, goal, enemies, mode):
    risk = compute_risk(grid, enemies, config.RISK_DECAY, config.RISK_MAX)
    def passable(r, c):
        return grid.cells[r][c].terrain != "BLOCKED"
    def neighbors(r, c):
        return grid.neighbors4(r, c)
    def move_cost(a, b):
        r, c = b
        return grid.cells[r][c].cost + risk_weight(mode) * risk[r][c]
    path, total = astar(start, goal, passable, neighbors, move_cost, manhattan)
    return path, total, risk

def draw_grid(screen, grid: Grid, risk, cell_size, margin, path=None, start=None, goal=None, enemies=None):
    for r in range(grid.rows):
        for c in range(grid.cols):
            x = c*(cell_size+margin) + margin
            y = r*(cell_size+margin) + margin
            base = grid.terrain_color(r, c)
            # blend risk into red intensity (simple)
            rv = min(255, int(255 * min(1.0, (risk[r][c] / (10.0)))))
            color = (max(base[0], rv), max(base[1]-rv//3, 0), max(base[2]-rv//3, 0))
            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

    # path
    if path:
        for (r, c) in path:
            x = c*(cell_size+margin) + margin
            y = r*(cell_size+margin) + margin
            pygame.draw.rect(screen, (0,0,0), (x+4, y+4, cell_size-8, cell_size-8), 2)

    # start & goal
    if start:
        r,c = start
        x = c*(cell_size+margin)+margin
        y = r*(cell_size+margin)+margin
        pygame.draw.rect(screen, (50,120,255), (x+6, y+6, cell_size-12, cell_size-12), 0)
    if goal:
        r,c = goal
        x = c*(cell_size+margin)+margin
        y = r*(cell_size+margin)+margin
        pygame.draw.rect(screen, (255,80,80), (x+6, y+6, cell_size-12, cell_size-12), 0)

    # enemies
    if enemies:
        for (er, ec, rng) in enemies:
            x = ec*(cell_size+margin)+margin + cell_size//2
            y = er*(cell_size+margin)+margin + cell_size//2
            pygame.draw.circle(screen, (120,0,0), (x,y), cell_size//3)
            # visual ring (may be big) - draw single point for range radial (thin)
            pygame.draw.circle(screen, (120,0,0), (x,y), max(1, int(rng*(cell_size+margin))), 1)

def animate(screen, path, speed=30, cell_size=28, margin=2):
    clock = pygame.time.Clock()
    for (r,c) in path:
        clock.tick(speed)
        x = c*(cell_size+margin)+margin + cell_size//2
        y = r*(cell_size+margin)+margin + cell_size//2
        pygame.draw.circle(screen, (0,0,0), (x,y), cell_size//6)
        pygame.display.flip()

def main():
    seed_all(config.SEED)
    grid, start, goal, enemies = load_map(config.DEFAULT_MAP)
    if not enemies:
        enemies = randomize_enemies(grid, k=3)

    mode = "SAFEST"
    path, total, risk = compute_path(grid, start, goal, enemies, mode)

    pygame.init()
    W = grid.cols*(config.CELL_SIZE+config.MARGIN)+config.MARGIN
    H = grid.rows*(config.CELL_SIZE+config.MARGIN)+config.MARGIN
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("BattlePath AI – Tactical Pathfinding ({} mode)".format(mode))
    clock = pygame.time.Clock()

    running = True
    dirty = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r:
                    enemies = randomize_enemies(grid, k=3)
                    dirty = True
                elif event.key == pygame.K_t:
                    mode = "FASTEST" if mode == "SAFEST" else "SAFEST"
                    dirty = True
                elif event.key == pygame.K_n:
                    grid = Grid.from_json(str(config.DEFAULT_MAP))
                    dirty = True
                elif event.key == pygame.K_SPACE and path:
                    animate(screen, path, speed=45, cell_size=config.CELL_SIZE, margin=config.MARGIN)

        if dirty:
            path, total, risk = compute_path(grid, start, goal, enemies, mode)
            pygame.display.set_caption("BattlePath AI – {} (cost={:.1f})".format(mode, total))
            screen.fill((20,20,20))
            draw_grid(screen, grid, risk, config.CELL_SIZE, config.MARGIN, path, start, goal, enemies)
            pygame.display.flip()
            dirty = False

        clock.tick(config.FPS)
    pygame.quit()

if __name__ == "__main__":
    main()




