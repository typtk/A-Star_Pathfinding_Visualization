import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node():
    def __init__(self, row, col, width, total_rows) -> None:
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_start(self):
        return self.color == ORANGE

    def is_goal(self):
        return self.color == TURQUOISE
    
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK

    def make_start(self):
        self.color = ORANGE

    def make_goal(self):
        self.color = TURQUOISE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = PURPLE

    def reset(self):
        self.color = WHITE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():                    # UP
            self.neighbors.append(grid[self.row-1][self.col])

        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():    # DOWN
            self.neighbors.append(grid[self.row+1][self.col])

        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():                    # LEFT
            self.neighbors.append(grid[self.row][self.col-1])

        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():    # RIGHT
            self.neighbors.append(grid[self.row][self.col+1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def algorithm(draw, grid, start, goal):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = g_score[start] + h(start.get_pos(), goal.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == goal:
            reconstruct_path(came_from, goal, draw)
            goal.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), goal.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()
    
    return False

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def make_grid(rows, window_width):
    grid = []
    grid_width = window_width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, grid_width, rows)
            grid[i].append(node)
    return grid
    
def draw_grid(win, rows, window_width):
    grid_width = window_width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*grid_width), (window_width, i*grid_width))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*grid_width, 0), (j*grid_width, window_width))
    
def draw(win, grid, rows, window_width):
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, window_width)
    pygame.display.update()

def get_clicked_pos(pos, rows, window_width):
    grid_width = window_width // rows
    x, y = pos
    row = y // grid_width
    col = x // grid_width
    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    draw(win, grid, ROWS, width)

    start = None
    goal = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if pygame.mouse.get_pressed()[0]:   #left click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != goal:
                    start = node
                    start.make_start()

                elif not goal and node != start:
                    goal = node
                    goal.make_goal()

                elif node != start and node != goal:
                    node.make_barrier()    

            elif pygame.mouse.get_pressed()[2]: #right click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == goal:
                    goal = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and goal:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, goal)

                if event.key == pygame.K_c:
                    start = None
                    goal = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)
