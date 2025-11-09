def compute_risk(grid, enemies, decay, risk_max):
    """Return 2D list of risk values for each cell."""
    R, C = grid.rows, grid.cols
    risk = [[0.0 for _ in range(C)] for _ in range(R)]
    for (er, ec, rng) in enemies:
        for r in range(R):
            for c in range(C):
                d = abs(r - er) + abs(c - ec)  # Manhattan distance
                if d <= rng:
                    contrib = risk_max
                else:
                    # exponential decay outside range
                    contrib = risk_max * (decay ** (d - rng))
                risk[r][c] += contrib
    return risk

