import heapq
from typing import Tuple, Dict, List

def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def reconstruct(came_from: Dict[Tuple[int,int], Tuple[int,int]], current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def astar(start: Tuple[int,int], goal: Tuple[int,int], 
          passable, neighbors, move_cost, heuristic):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Tuple[int,int], Tuple[int,int]] = {}
    g = {start: 0.0}
    f = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct(came_from, current), g[current]
        for nxt in neighbors(*current):
            if not passable(*nxt):
                continue
            tentative = g[current] + move_cost(current, nxt)
            if tentative < g.get(nxt, float('inf')):
                came_from[nxt] = current
                g[nxt] = tentative
                f[nxt] = tentative + heuristic(nxt, goal)
                heapq.heappush(open_set, (f[nxt], nxt))
    return None, float('inf')
