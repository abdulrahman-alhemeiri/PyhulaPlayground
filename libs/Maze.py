class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Store walls as sets of blocked edges
        # Each wall is represented as a frozenset of two adjacent cells
        self.walls = set()

    def add_wall(self, cell1, cell2):
        """Add a wall between two adjacent cells"""
        self.walls.add(frozenset([cell1, cell2]))

    def is_passable(self, from_cell, to_cell):
        """Check if we can move from one cell to another"""
        return frozenset([from_cell, to_cell]) not in self.walls

    def get_neighbors(self, cell):
        """Get all valid neighboring cells"""
        x, y = cell
        neighbors = []
        # Check all 4 directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            # Check bounds
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Check if there's no wall
                if self.is_passable(cell, (nx, ny)):
                    neighbors.append((nx, ny))
        return neighbors
