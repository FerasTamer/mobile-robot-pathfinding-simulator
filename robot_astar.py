import pygame
import math
from queue import PriorityQueue


WIDTH = 700
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A-Star's Path Finding Algorithm")

# Set up some constants
INITIAL_POSITION = (50, 50)
ROBOT_SIZE = (64, 64)
MAX_WHEEL_SPEED = 10  # You can change this value
# Create a clock
clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

class Robot:
    def __init__(self, x, y, image_path, wheelbase, distance_to_cog):
        self.x = x
        self.y = y
        self.angle = 0
        self.target_x = None
        self.target_y = None
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        # Assuming you have already loaded the image
        original_image = pygame.image.load(image_path)

        # Set the desired width and height (adjust these values as needed)
        new_width = 50
        new_height = 50
        # Resize the image
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        self.d = wheelbase  # Distance between the wheels (d)
        self.a = distance_to_cog  # Distance from CoG to midpoint between wheels (a)

    def set_target(self, x):
        self.target_x = x[0]
        self.target_y = x[1]

    def move_to_target(self):
        if self.target_x is not None and self.target_y is not None:
            # Calculate the angle to the target
            angle_to_target = math.atan2(self.target_y - self.y, self.target_x - self.x)
            
            # Calculate the desired angular velocity
            w = angle_to_target - self.angle
            
            # Limit the turning rate
            MAX_TURNING_RATE = 0.1
            w = max(min(w, MAX_TURNING_RATE), -MAX_TURNING_RATE)
            
            # Calculate the desired linear velocity
            v = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            # Limit the speed
            MAX_SPEED = 1
            v = min(v, MAX_SPEED)
            
            # Calculate the wheel velocities
            self.left_wheel_speed = v - w * self.a / 2
            self.right_wheel_speed = v + w * self.a / 2
            
            # Update the robot's position and angle
            self.x += math.cos(self.angle) * v
            self.y += math.sin(self.angle) * v
            self.angle += w

    def draw(self, screen):
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        pos = (self.x - rotated_image.get_width() // 2, self.y - rotated_image.get_height() // 2)
        screen.blit(rotated_image, pos)


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    path_list = []  # List to store the center of each square in the path
    while current in came_from:
        current = came_from[current]
        current.make_path()
        x, y = current.x, current.y  # Top left corner of the square
        center_x, center_y = x + current.width/2, y + current.width/2  # Center of the square
        path_list.append([center_x, center_y])  # Add the center to the path list as a list
        draw()
    # path_list.append(current[-1])
    path_list = path_list[::-1]  # Reverse the order of the list
    return path_list  # Return the list of centers

def algorithm(draw, grid, start, end):

    count = 0

    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            # Reconstruct the path from end to start
            path_list = reconstruct_path(came_from, end, draw)
            x = end.x + end.width // 2
            y = end.y + end.width // 2
            path_list.append([x,y])  # Add the turquoise square to the path
            end.make_end()
            return path_list

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    # neighbor.make_open()

        # draw()

        # if current != start:
            # current.make_closed()

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

def draw_grid(screen, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(screen, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(screen, GREY, (j * gap, 0), (j * gap, width))

def draw(screen, grid, rows, width, move_robot):
    screen.fill(WHITE)

    for row in grid:
        for spot in row:
            # if spot.is_barrier():  # Always draw obstacles
            # spot.draw(screen)
            # elif not move_robot:  # Only draw other spots if the robot is not moving
            spot.draw(screen)

    pygame.display.update()
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(screen, width):

    # Create a buffer surface
    buffer = pygame.Surface((width, width))
    # Create a robot
    robot = Robot(*INITIAL_POSITION,'./assets/robot.png',42,0)
    targets_list = None
    
    ROWS = 10  # Increase the number of rows to make the grid cells larger
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    init_robot = False
    move_robot = False
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    path_list = algorithm(lambda: draw(screen, grid, ROWS, width,move_robot), grid, start, end)
                    path_list_final_target = path_list[-1]
                    targets_list = path_list
                    targets_list.append(path_list_final_target)

                    init_robot= True
                    robot.target_x = targets_list[0][0]
                    robot.target_y = targets_list[0][1]
                    end.make_path() 
                    
                    robot.x = start.x + start.width // 2
                    robot.y = start.y + start.width // 2
                    # print(path_list,"\n",path_list_final_target)
                if event.key == pygame.K_s and init_robot:
                    move_robot = True
                    # print('robot')
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
        if move_robot:
            # Clear the buffer
            buffer.fill((255,255,255))


            draw(buffer, grid, ROWS, width,move_robot)
            # Update the robot's position and draw the robot
            robot.move_to_target()
            robot.draw(buffer)

            # Draw the buffer to the screen
            screen.blit(buffer, (0, 0))
            
            # If the robot reached its target, set a new target
            if len(targets_list) > 0:
                if int(robot.x) == robot.target_x and int(robot.y) == robot.target_y:
                    robot.set_target(targets_list.pop(0))
                            
            else:
                robot.x = robot.target_x
                robot.y = robot.target_y
                #robot.set_target(random.randint(0, WIDTH), random.randint(0, HEIGHT))

        if not move_robot:
            draw(screen, grid, ROWS, width,move_robot)

        # Flip the display
        
        pygame.display.flip()

        clock.tick(FPS)
    pygame.quit()

main(screen, WIDTH)




