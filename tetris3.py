import pygame
import random
import sys
import os

# Optional MySQL connector — allow the game to run without it
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except Exception:
    MYSQL_AVAILABLE = False

# Tetris Game Code
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
# Initialize Pygame early so subsystems (display, font, mixer) are ready
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    # Audio device might be unavailable; continue without sound
    pass

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Default music path (can be changed). If file missing, music is skipped.
MUSIC_PATH = r'C:\Users\SUMEDHA BASU\Videos\Tetris\Tetris (Game Boy) - 02. A-Type.mp3'

# Database enabled flag (set by init_database)
DB_ENABLED = False

# Colors for drawing the grid and pieces
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
COLORS = [(0, 255, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (128, 0, 128), (255, 165, 0), (0, 0, 255)]

# Tetromino shapes for Tetris game
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],
    [[2, 2], [2, 2]],
    [[3, 3, 0], [0, 3, 3]],
    [[0, 4, 4], [4, 4, 0]],
    [[5, 5, 5, 5]],
    [[6, 6, 6], [6, 0, 0]],
    [[7, 7, 7], [0, 0, 7]],
]

# Pygame already initialized above

# Initialize MySQL Database
def init_database():
    """Creates database and table if they don't exist."""
    global DB_ENABLED
    DB_ENABLED = False
    if not MYSQL_AVAILABLE:
        print("mysql.connector not available; database saves disabled.")
        return
    try:
        # Connecting to MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Replace with your MySQL password
        )
        cursor = conn.cursor()

        # Create database and use it
        cursor.execute("CREATE DATABASE IF NOT EXISTS Tetris")
        cursor.execute("USE Tetris")

        # Create table for storing player names and scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                player_name VARCHAR(255),
                score INT
            )
        """)
        conn.close()
        DB_ENABLED = True
    except mysql.connector.Error as err:
        print(f"Could not initialize database (scores disabled): {err}")
        DB_ENABLED = False

# Function to save the player's name and score to the database
def save_score(player_name, score):
    """Saves the player's name and score to the database."""
    if not DB_ENABLED or not MYSQL_AVAILABLE:
        # DB not available; skip saving silently
        return
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Replace with your MySQL password
            database="Tetris",
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Scores (player_name, score) VALUES (%s, %s)", (player_name, score))
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error saving score: {err}")

# Function to get the player's name via GUI input
def get_player_name():
    """Displays a GUI for the player to input their name."""
    input_box = pygame.Rect(WIDTH // 4, HEIGHT // 2 - 20, WIDTH // 2, 40)
    color_inactive = GRAY
    color_active = WHITE
    color = color_inactive
    # Make the input active by default so the user can type right away
    active = True
    name = ""
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    
    # Name input loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle the active state of the input box
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return name if name.strip() else "Player"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]  # Remove the last character
                    else:
                        name += event.unicode  # Add the typed character

        # Draw the input box
        screen.fill(BLACK)
        txt_surface = font.render(name, True, WHITE)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width

        # Center the input box horizontally
        input_box.x = (WIDTH - input_box.w) // 2

        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        
        # Render prompt and center it
        prompt_surface = font.render("Enter your name:", True, WHITE)
        prompt_width = prompt_surface.get_width()
        screen.blit(prompt_surface, ((WIDTH - prompt_width) // 2, HEIGHT // 2 - 60))

        pygame.display.flip()
        clock.tick(30)

# Initialize ambient music function
def play_ambient_music():
    try:
        if not MUSIC_PATH or not os.path.exists(MUSIC_PATH):
            print(f"Ambient music file not found at: {MUSIC_PATH}")
            return
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0)
    except Exception as e:
        print(f"Could not play ambient music: {e}")
# filepath: c:\Users\SUMEDHA BASU\Desktop\PYTHON CODING\tetris3.py

# Tetris game class
class Tetris:
    def __init__(self):
        # Initialize the grid and pieces
        self.grid = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.game_over = False

    # Function to generate new pieces
    def get_new_piece(self):
        shape = random.choice(SHAPES)
        return {"shape": shape, "x": WIDTH // (2 * BLOCK_SIZE) - len(shape[0]) // 2, "y": 0}

    # Function to draw the game grid
    def draw_grid(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                color = COLORS[self.grid[y][x] - 1] if self.grid[y][x] else GRAY
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    # Function to draw a piece on the screen
    def draw_piece(self, piece):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, COLORS[cell - 1], (
                        (piece["x"] + x) * BLOCK_SIZE, (piece["y"] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # Function to check if a piece can move in the given direction
    def valid_move(self, piece, dx, dy):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + dx
                    new_y = piece["y"] + y + dy
                    if new_x < 0 or new_x >= WIDTH // BLOCK_SIZE or new_y >= HEIGHT // BLOCK_SIZE or (
                            new_y >= 0 and self.grid[new_y][new_x]):
                        return False
        return True

    # Lock the piece in place and clear lines
    def lock_piece(self, piece):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = piece["y"] + y
                    grid_x = piece["x"] + x
                    if 0 <= grid_y < len(self.grid) and 0 <= grid_x < len(self.grid[0]):
                        self.grid[grid_y][grid_x] = cell
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        if not self.valid_move(self.current_piece, 0, 0):
            self.game_over = True

    # Function to clear filled lines
    def clear_lines(self):
        lines = 0
        for i in range(len(self.grid) - 1, -1, -1):
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0] * (WIDTH // BLOCK_SIZE))
                lines += 1
        self.score += lines * 10

    # Function to update the game (move pieces down)
    def update(self):
        if self.valid_move(self.current_piece, 0, 1):
            self.current_piece["y"] += 1
        else:
            self.lock_piece(self.current_piece)

    # Function to draw the game state on the screen
    def draw(self):
        screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece(self.current_piece)
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(text, (10, 10))

    # Function to display the Game Over screen
    def show_game_over(self):
        font = pygame.font.Font(None, 48)
        game_over_text = font.render("Game Over!", True, WHITE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        
        screen.fill(BLACK)
        
        # Centering the texts
        game_over_width = game_over_text.get_width()
        score_width = score_text.get_width()

        screen.blit(game_over_text, ((WIDTH - game_over_width) // 2, HEIGHT // 3))
        screen.blit(score_text, ((WIDTH - score_width) // 2, HEIGHT // 2))
        
        pygame.display.flip()
        pygame.time.wait(2000)  # Wait for 2 seconds before exiting


# Main game loop
def main():
    # Initialize the database and fetch the player's name
    init_database()
    player_name = get_player_name()
    
    # Play the ambient music after the name is entered
    play_ambient_music()
    
    tetris = Tetris()
    clock = pygame.time.Clock()

    # Game loop
    while not tetris.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and tetris.valid_move(tetris.current_piece, -1, 0):
                    tetris.current_piece["x"] -= 1
                elif event.key == pygame.K_RIGHT and tetris.valid_move(tetris.current_piece, 1, 0):
                    tetris.current_piece["x"] += 1
                elif event.key == pygame.K_DOWN and tetris.valid_move(tetris.current_piece, 0, 1):
                    tetris.current_piece["y"] += 1
                elif event.key == pygame.K_UP:
                    rotated_shape = [list(row) for row in zip(*tetris.current_piece["shape"][::-1])]
                    if tetris.valid_move({"shape": rotated_shape, "x": tetris.current_piece["x"], "y": tetris.current_piece["y"]}, 0, 0):
                        tetris.current_piece["shape"] = rotated_shape

        tetris.update()
        tetris.draw()
        pygame.display.flip()
        clock.tick(6)  # Slower speed (6 FPS instead of 10)
    
    # Save score to database and show the game over screen
    save_score(player_name, tetris.score)
    tetris.show_game_over()
    
    # Clean up and exit
    pygame.quit()
    sys.exit()


# Run the game
if __name__ == "__main__":
    main()