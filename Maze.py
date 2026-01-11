class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = set()

    def add_wall(self, cell1, cell2):
        self.walls.add(frozenset([cell1, cell2]))

    def is_passable(self, from_cell, to_cell):
        return frozenset([from_cell, to_cell]) not in self.walls

    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.is_passable(cell, (nx, ny)):
                    neighbors.append((nx, ny))
        return neighbors
