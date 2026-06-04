"""
DISTRITAL FRANCISCO JOSÉ DE CALDAS UNIVERSITY
COURSE: COMPUTER SCIENCES I (2026-I)

PROJECT: TREASURE HUNT
COMPONENT: INTERACTIVE PYGAME USER INTERFACE
"""

import itertools

# --- Backtracking planner API ---
def plan_path_backtracking(start_pos, step_limit, item_list):
    """
    Simple backtracking planner that selects an ordered subset of treasures to visit
    within `step_limit` steps maximizing total collected value. Returns a dict with
    keys: `calculated_path` (list of (x,y) tuples including start) and `total_yield`.
    """
    # Normalize items
    items = [dict(x=i.get('x'), y=i.get('y'), value=i.get('value', 0), name=i.get('name')) for i in item_list]

    def manhattan(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best_yield = 0
    best_route = [tuple(start_pos)]

    # Try all permutations of up to len(items) (prune by distance limit)
    for r in range(1, len(items)+1):
        for perm in itertools.permutations(items, r):
            dist = 0
            pos = tuple(start_pos)
            total = 0
            feasible = True
            for it in perm:
                target = (it['x'], it['y'])
                dist += manhattan(pos, target)
                pos = target
                if dist > step_limit:
                    feasible = False
                    break
                total += it['value']
            if feasible and total > best_yield:
                best_yield = total
                # build path as straight-line moves between points
                path = [tuple(start_pos)]
                cur = tuple(start_pos)
                for it in perm:
                    tx, ty = it['x'], it['y']
                    # move horizontally then vertically
                    while cur[0] != tx:
                        cur = (cur[0] + (1 if tx > cur[0] else -1), cur[1])
                        path.append(cur)
                    while cur[1] != ty:
                        cur = (cur[0], cur[1] + (1 if ty > cur[1] else -1))
                        path.append(cur)
                best_route = path

    return {"calculated_path": best_route, "total_yield": best_yield}

if __name__ == "__main__":
    import json

    start = (0, 0)
    treasures = [
        {"x": 1, "y": 2, "value": 10, "name": "Test Coin"},
        {"x": 3, "y": 1, "value": 50, "name": "Test Silver"}
    ]
    result = plan_path_backtracking(start, 10, treasures)
    print(json.dumps(result, indent=4))
