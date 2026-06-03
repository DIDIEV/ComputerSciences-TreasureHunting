"""
DISTRITAL FRANCISCO JOSÉ DE CALDAS UNIVERSITY
COURSE: COMPUTER SCIENCES I (2026-I)

PROJECT: TREASURE HUNT
COMPONENT: INTERACTIVE PYGAME USER INTERFACE
"""

def calculate_manhattan_distance(point_a, point_b):
    """
    Computes the Manhattan distance between two coordinates on a 2D grid.
    This metric represents the absolute minimum path distance on an orthogonal layout.
    
    Parameters:
    - point_a (tuple/list): The origin coordinates (x1, y1).
    - point_b (tuple/list): The target coordinates (x2, y2).
    
    Returns:
    - int: The total grid step distance between both nodes.
    """
    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])


def find_best_treasure_greedy(player_pos, treasure_list):
    """
    Evaluates all active grid entities using a local optimization heuristic rule.
    It selects the node that maximizes item value relative to its proximity cost.
    
    Parameters:
    - player_pos (tuple/list): Current (x, y) grid coordinates of the player agent.
    - treasure_list (list): Collection of active item dictionaries:
                            [{'x': int, 'y': int, 'value': int, 'name': str}]
                            
    Returns:
    - dict: The optimal target treasure structure chosen by the greedy heuristic.
            Returns None if no items remain on the board.
    """
    # Guard clause: Return None immediately if there are no items to process
    if not treasure_list:
        return None
        
    best_target = None
    max_priority_ratio = -1.0
    
    # Iterate through each entity to evaluate local weight parameters
    for treasure in treasure_list:
        # Compute structural step distance from the agent
        item_pos = (treasure['x'], treasure['y'])
        grid_distance = calculate_manhattan_distance(player_pos, item_pos)
        
        # Prevent division by zero if the agent is already standing on the entity coordinate
        if grid_distance == 0:
            continue
            
        # Greedy Heuristic Formula: Prioritizes higher payouts over shorter distances
        priority_ratio = treasure['value'] / grid_distance
        
        # Local choice optimization step
        if priority_ratio > max_priority_ratio:
            max_priority_ratio = priority_ratio
            best_target = treasure
            
    return best_target