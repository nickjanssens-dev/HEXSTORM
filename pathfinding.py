import heapq
from settings import TILE_SIZE
from map import is_wall

class Node:
    def __init__(self, x, y, g=0, h=0, parent=None):
        self.x = x
        self.y = y
        self.g = g  # Cost from start
        self.h = h  # Heuristic cost to goal
        self.f = g + h  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

def heuristic(x1, y1, x2, y2):
    """Manhattan distance heuristic"""
    return abs(x1 - x2) + abs(y1 - y2)

def get_neighbors(x, y):
    """Get valid walkable neighbors for a tile"""
    neighbors = []
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
    
    for dx, dy in directions:
        new_x = x + dx
        new_y = y + dy
        
        # Convert to world coordinates for wall checking
        world_x = new_x * TILE_SIZE + TILE_SIZE // 2
        world_y = new_y * TILE_SIZE + TILE_SIZE // 2
        
        if not is_wall(world_x, world_y):
            neighbors.append((new_x, new_y))
    
    return neighbors

def find_path(start_x, start_y, goal_x, goal_y):
    """
    A* pathfinding algorithm
    Returns path as list of (x, y) tile coordinates
    """
    # Convert world coordinates to tile coordinates
    start_tile_x = int(start_x // TILE_SIZE)
    start_tile_y = int(start_y // TILE_SIZE)
    goal_tile_x = int(goal_x // TILE_SIZE)
    goal_tile_y = int(goal_y // TILE_SIZE)
    
    # Check if start or goal is in wall
    start_world_x = start_tile_x * TILE_SIZE + TILE_SIZE // 2
    start_world_y = start_tile_y * TILE_SIZE + TILE_SIZE // 2
    goal_world_x = goal_tile_x * TILE_SIZE + TILE_SIZE // 2
    goal_world_y = goal_tile_y * TILE_SIZE + TILE_SIZE // 2
    
    if is_wall(start_world_x, start_world_y) or is_wall(goal_world_x, goal_world_y):
        return []
    
    # Initialize open and closed lists
    open_list = []
    closed_set = set()
    
    # Create start node
    start_node = Node(start_tile_x, start_tile_y, 0, 
                      heuristic(start_tile_x, start_tile_y, goal_tile_x, goal_tile_y))
    heapq.heappush(open_list, start_node)
    
    while open_list:
        current = heapq.heappop(open_list)
        
        # Check if we reached the goal
        if current.x == goal_tile_x and current.y == goal_tile_y:
            # Reconstruct path
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]  # Reverse to get start to goal
        
        closed_set.add((current.x, current.y))
        
        # Check neighbors
        for neighbor_x, neighbor_y in get_neighbors(current.x, current.y):
            if (neighbor_x, neighbor_y) in closed_set:
                continue
            
            g = current.g + 1  # Cost to move to neighbor
            h = heuristic(neighbor_x, neighbor_y, goal_tile_x, goal_tile_y)
            neighbor_node = Node(neighbor_x, neighbor_y, g, h, current)
            
            # Check if neighbor is already in open list with lower cost
            in_open = False
            for i, node in enumerate(open_list):
                if node.x == neighbor_x and node.y == neighbor_y:
                    if neighbor_node.g < node.g:
                        open_list[i] = neighbor_node
                        heapq.heapify(open_list)
                    in_open = True
                    break
            
            if not in_open:
                heapq.heappush(open_list, neighbor_node)
    
    return []  # No path found

def get_next_waypoint(start_x, start_y, goal_x, goal_y, look_ahead=2):
    """
    Get the next waypoint along the path
    Returns world coordinates of the next position to move towards
    """
    path = find_path(start_x, start_y, goal_x, goal_y)
    
    if not path:
        return None
    
    # Look ahead a few waypoints for smoother movement
    target_index = min(look_ahead, len(path) - 1)
    target_tile_x, target_tile_y = path[target_index]
    
    # Convert back to world coordinates
    world_x = target_tile_x * TILE_SIZE + TILE_SIZE // 2
    world_y = target_tile_y * TILE_SIZE + TILE_SIZE // 2
    
    return world_x, world_y

def can_reach_directly(start_x, start_y, goal_x, goal_y):
    """Check if enemy can reach goal directly without pathfinding"""
    # Import here to avoid circular import
    from enemy import check_line_of_sight
    return check_line_of_sight(start_x, start_y, goal_x, goal_y)
