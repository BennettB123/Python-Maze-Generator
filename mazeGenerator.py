import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import random
import statistics
import time

# Character encodings for various assets
WALL = u'\N{FULL BLOCK}'
PLAYER = u'\N{WHITE SMILING FACE}'


# Function to setup the screen
def setup():
    strscr = curses.initscr()
    strscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    # Setting up colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Wall color
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Player color
    return strscr

# Function to de-setup the screen so the console can return to normal
def end_window(strscr):
    curses.nocbreak()
    curses.echo()
    strscr.keypad(False)
    curses.endwin()



class Maze:

    # Sets up the maze data-structure and generates a random maze
    def __init__(self, rows, cols, screen):
        self.rows = rows
        self.cols = cols
        # Need to check if rows and cols are good sizes for the maze
        if (rows - 2) % 2 == 0:
            self.rows -= 1
        if (cols - 2) % 2 == 0:
            self.cols -= 1


        # Placing the starting location about halfway down the first column
        self.start_col = 1
        self.start_row = 1
        #self.start_row = int(self.rows/2)
        #if self.start_row % 2 == 0:  # Make sure its not in a place a wall is going to be
            #self.start_row -= 1
        
        self.player_col = self.start_col
        self.player_row = self.start_row
        self.goal_col = self.cols - 2
        self.goal_row = self.rows - 2
        self.screen = screen

        # Creating maze and filling it will spaces
        self.maze = [[' ' for i in range(self.cols)] for j in range(self.rows)]
    
    
    # Helper function for generate_maze
    # Finds a random neighbor of (cur_row, cur_col) that is un-visited
    def random_neighbor(self, cur_row, cur_col, visited):
        # TODO: FIX THIS! IT DOES NOT LOOK CLEAN AT ALL
        while True:
            dir = random.randint(1, 4)
            if dir == 1:  # Try to go up
                if cur_row - 2 >= 1:
                    if (cur_row - 2, cur_col) not in visited:
                        return cur_row - 2, cur_col
            elif dir == 2:  # Try to go right
                if cur_col + 2 < self.cols:
                    if (cur_row, cur_col + 2) not in visited:
                        return cur_row, cur_col + 2
            elif dir == 3:  # Try to go down
                if cur_row + 2 < self.rows:
                    if (cur_row + 2, cur_col) not in visited:
                        return cur_row + 2, cur_col
            elif dir == 4:  # Try to go left
                if cur_col - 2 >= 1:
                    if (cur_row, cur_col - 2) not in visited:
                        return cur_row, cur_col - 2
    
    
    # Helper function for generate_maze
    # Checks if there are any unvisited neighbors of (cur_row, cur_col)
    # Returns True if there is, False otherwise
    def neighbor_exists(self, cur_row, cur_col, visited):
    # TODO: FIX THIS! IT DOES NOT LOOK CLEAN AT ALL
        # Try to go up
        if cur_row - 2 >= 1:
            if (cur_row - 2, cur_col) not in visited:
                return True
        # Try to go right
        if cur_col + 2 < self.cols:
            if (cur_row, cur_col + 2) not in visited:
                return True
        # Try to go down
        if cur_row + 2 < self.rows:
            if (cur_row + 2, cur_col) not in visited:
                return True
        # Try to go left
        if cur_col - 2 >= 1:
            if (cur_row, cur_col - 2) not in visited:
                return True
        return False
    
    
    # Uses a depth-first search method to generate the maze
    # See  https://en.wikipedia.org/wiki/Maze_generation_algorithm
    # This is a simple algorithm to implement, but does not produce complex mazes.
    # TODO: IMPLEMENT MORE MAZE GENERATION ALGORITHMS TO GET MORE COMPLEX MAZES
    def generate_maze(self):
        # Adding in every wall to begin the maze generation algorithm
        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                if i%2 == 0 or j%2 == 0:
                    self.maze[i][j] = WALL
                # Borders of maze
                if i == 0 or i == self.rows-1 or j == 0 or j == self.cols-1:
                    self.maze[i][j] = WALL
                    
        visited = {(self.start_row, self.start_col)}  # set representing cells that have been visited so we don't loop
        stack = [(self.start_row, self.start_col)]  # stack of visited cells to make back-tracking easier
        cur_row = self.start_row
        cur_col = self.start_col
        
        while len(stack) != 0:
            # If an un-visited neighbor exists, pick one, remove the wall to it, and continue
            if self.neighbor_exists(cur_row, cur_col, visited):
                new_row, new_col = self.random_neighbor(cur_row, cur_col, visited)
                self.maze[statistics.mean((new_row, cur_row))][statistics.mean((new_col, cur_col))] = ' '  # Removing wall
                cur_row = new_row
                cur_col = new_col
                visited.add((cur_row, cur_col))
                stack.append((cur_row, cur_col))
            # If there are no un-visited neighbors, pop the stack until one is found
            else:
                while not self.neighbor_exists(cur_row, cur_col, visited):
                    if len(stack) != 0:
                        cur = stack.pop()
                        cur_row = cur[0]
                        cur_col = cur[1]
                    else:
                        break
        
        # Removing all walls from starting block, to make maze appear more difficult
        # Upper wall
        if self.start_row - 2 >= 1:
            self.maze[self.start_row - 1][self.start_col] = ' '
        # Right wall
        if self.start_col + 2 < self.cols:
            self.maze[self.start_row][self.start_col + 1] = ' '
        # Lower wall
        if self.start_row + 2 < self.rows:
            self.maze[self.start_row + 1][self.start_col] = ' '
        # Left wall
        if self.start_col - 2 >= 1:
            self.maze[self.start_row][self.start_col - 1] = ' '    
    

    def print_maze(self):
        # Displaying the maze to the screen
        row = col = 0
        for s in self.maze:
            col = 0
            for ss in s:
                # in a try/catch because addch() wont let you draw in bottom right cell without raising an exception
                try:
                    self.screen.addch(row, col, ss)
                except curses.error as e:
                    pass
                col += 1
            row += 1

        # Adding in the start and goal cells
        self.screen.addch(self.start_row, self.start_col, 'S')
        self.screen.addch(self.goal_row, self.goal_col, 'G')
        # Adding in the player
        self.screen.addch(self.player_row, self.player_col, PLAYER)
        self.screen.refresh()


    # Functions to move player
    # Each one moves the player then checks if the player is in a wall
    # If in a wall, move back
    def move_player_left(self):
        self.player_col -= 1
        if self.maze[self.player_row][self.player_col] == WALL:
            self.player_col += 1

    def move_player_right(self):
        self.player_col += 1
        if self.maze[self.player_row][self.player_col] == WALL:
            self.player_col -= 1

    def move_player_up(self):
        self.player_row -= 1
        if self.maze[self.player_row][self.player_col] == WALL:
            self.player_row += 1

    def move_player_down(self):
        self.player_row += 1
        if self.maze[self.player_row][self.player_col] == WALL:
            self.player_row -= 1
            
    def win(self):
        if (self.player_col, self.player_row) == (self.goal_col, self.goal_row):
            return True
        else:
            return False




def main(stdscr):
    strscr = setup()
    m = Maze(int(curses.LINES), int(curses.COLS), strscr)
    m.generate_maze()


    while True:
        strscr.erase()
        m.print_maze()

        event = strscr.getch()
        key = key if event == -1 else event

        if key in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 'p']:
            if key == KEY_LEFT:
                m.move_player_left()
            elif key == KEY_RIGHT:
                m.move_player_right()
            elif key == KEY_UP:
                m.move_player_up()
            elif key == KEY_DOWN:
                m.move_player_down()

        if m.win():
            # strscr.erase()
            # m.print_maze()
            # time.sleep(0.5)
            # strscr.erase()
            # strscr.addstr(0, 0, "CONGRATULATIONS!\nPress any button to continue", curses.A_BLINK)
            # time.sleep(1)
            # strscr.getch()
            exit()


    end_window(strscr)


curses.wrapper(main)



