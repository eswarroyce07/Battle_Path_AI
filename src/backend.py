from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from grid import Grid
from threat import compute_risk
from astar import astar, manhattan
import config

app = Flask(__name__, static_folder=str(Path(__file__).resolve().parents[1] / 'web'))


def load_map():
    grid = Grid.from_json(str(config.DEFAULT_MAP))
    meta = grid.meta
    return grid, meta


def randomize_enemies_on_grid(grid, k=3):
    import random
    enemies = []
    for _ in range(k):
        r = random.randrange(grid.rows)
        c = random.randrange(grid.cols)
        rng = random.randint(3, 6)
        enemies.append((r, c, rng))
    return enemies


def grid_to_dict(grid):
    # return minimal grid representation
    cells = [[grid.cells[r][c].terrain for c in range(grid.cols)] for r in range(grid.rows)]
    costs = [[grid.cells[r][c].cost for c in range(grid.cols)] for r in range(grid.rows)]
    return {
        'rows': grid.rows,
        'cols': grid.cols,
        'cells': cells,
        'costs': costs,
        'meta': getattr(grid, 'meta', {})
    }


@app.route('/')
def index():
    # Serve the frontend index.html from web/
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/api/map', methods=['GET'])
def api_map():
    grid, meta = load_map()
    return jsonify(grid_to_dict(grid))


@app.route('/api/path', methods=['POST'])
def api_path():
    data = request.get_json() or {}
    enemies = data.get('enemies')
    mode = data.get('mode', 'SAFEST')
    # allow client to override start/goal
    start_override = data.get('start')
    goal_override = data.get('goal')
    if enemies is None:
        # default to meta enemies or empty
        grid, meta = load_map()
        enemies = [tuple(e) for e in meta.get('enemies', [])]
    else:
        # sanitize various shapes clients may send
        sanitized = []
        for e in enemies:
            try:
                # allow [r,c,range] or [r,c]
                if len(e) >= 3:
                    sanitized.append((int(e[0]), int(e[1]), int(e[2])))
                elif len(e) == 2:
                    sanitized.append((int(e[0]), int(e[1]), 4))
            except Exception:
                # skip malformed entries
                continue
        enemies = sanitized

    grid, meta = load_map()
    # compute risk and run astar
    risk = compute_risk(grid, enemies, config.RISK_DECAY, config.RISK_MAX)

    def passable(r, c):
        return grid.cells[r][c].terrain != 'BLOCKED'

    def neighbors(r, c):
        return grid.neighbors4(r, c)

    def move_cost(a, b):
        r, c = b
        weight = config.RISK_WEIGHT_SAFE if mode == 'SAFEST' else config.RISK_WEIGHT_FAST
        return grid.cells[r][c].cost + weight * risk[r][c]

    start = tuple(start_override) if start_override else tuple(meta.get('start', [grid.rows-1, 0]))
    goal = tuple(goal_override) if goal_override else tuple(meta.get('goal', [0, grid.cols-1]))
    path, total = astar(start, goal, passable, neighbors, move_cost, manhattan)

    # include full risk grid (rounded) so frontend can render heatmap
    risk_rounded = [[round(v, 4) for v in row] for row in risk]

    return jsonify({
        'path': path,
        'total': total,
        'start': start,
        'goal': goal,
        'risk_sample': {
            'start': round(risk[start[0]][start[1]], 4),
            'goal': round(risk[goal[0]][goal[1]], 4)
        },
        'risk': risk_rounded
    })


@app.route('/api/randomize', methods=['GET'])
def api_randomize():
    grid, meta = load_map()
    enemies = randomize_enemies_on_grid(grid, k=3)
    return jsonify({'enemies': enemies})


if __name__ == '__main__':
    print('Starting backend on http://127.0.0.1:5000')
    app.run(debug=True)
