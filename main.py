import pygame
import random
import sys
import mysql.connector

# Constants
PLAYER_COLOR = (120, 24, 74)
OBSTACLE_GREEN_COLOR = (0, 255, 0)
OBSTACLE_RED_COLOR = (255, 0, 0)
BG_COLOR = (193, 154, 107)
TEXT_COLOR = (78, 22, 9)
HIGHLIGHT_COLOR = (255, 255, 0)
FONT_SIZE = 36
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT = 300, 50
INPUT_BOX_COLOR = (255, 255, 255)

# Database Setup
def connect_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="npt20",
        database="new_survival_game_db")
    cursor = db.cursor()
    cursor.execute(‘CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE)’)
    Cursor.execute(‘CREATE TABLE IF NOT EXISTS leaderboard (
            id INT PRIMARY KEY,
            username VARCHAR(255),
            best_score INT DEFAULT 0,
            FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE)’)
    db.commit()
    return db, cursor


# Pygame Setup
def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Survival")
    return screen
 
def get_username_input(screen):
    font = pygame.font.Font(None, FONT_SIZE)
    input_text = ''
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - INPUT_BOX_WIDTH // 2, SCREEN_HEIGHT // 2 - INPUT_BOX_HEIGHT // 2, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
 
    active = True
    while active:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, INPUT_BOX_COLOR, input_box, 2)
        prompt_text = font.render("Enter your username:", True, TEXT_COLOR)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - INPUT_BOX_HEIGHT - 50))
        text_surface = font.render(input_text, True, TEXT_COLOR)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
 
        pygame.display.flip()
 
def spawn_obstacle(obstacles, screen_width):
    if random.randint(1, 100) < 5:
        obstacle = pygame.Rect(random.randint(0, screen_width - 30), 0, 30, 30)
        obstacles.append((obstacle, 'green'))
 
    if random.randint(1, 100) < 5:
        obstacle = pygame.Rect(random.randint(0, screen_width - 30), 0, 30, 30)
        obstacles.append((obstacle, 'red'))
 
def update_leaderboard(cursor, db, username, score):
    cursor.execute("SELECT id, username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        return
    user_id, username = user
 
    cursor.execute("SELECT best_score FROM leaderboard WHERE id = %s", (user_id,))
    result = cursor.fetchone()
 
    if result:
        best_score = result[0]
        if score > best_score:
            cursor.execute("UPDATE leaderboard SET best_score = %s, username = %s WHERE id = %s",
                (score, username, user_id))
    else:
        cursor.execute("INSERT INTO leaderboard (id, username, best_score) VALUES (%s, %s, %s)",
            (user_id, username, score))
    db.commit()
 
def game_loop(screen, cursor, db, username):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)
 
    screen_width, screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
    player = pygame.Rect(screen_width // 2 - 25, screen_height - 100, 50, 50)
    score = 0
    obstacle_speed = 5
    player_speed = 10
 
    obstacles = []
    run = True
 
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
 
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, PLAYER_COLOR, player)
 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.move_ip(-player_speed, 0)
        if keys[pygame.K_RIGHT] and player.right < screen_width:
            player.move_ip(player_speed, 0)
 
        spawn_obstacle(obstacles, screen_width)
        for obstacle, obstacle_type in obstacles:
            obstacle.y += int(obstacle_speed)
 
            if player.colliderect(obstacle):
                obstacles.remove((obstacle, obstacle_type))
                if obstacle_type == 'green':
                    score += 1
                elif obstacle_type == 'red':
                    update_leaderboard(cursor, db, username, score)
                    game_over_screen(score, screen, cursor, db, username)
 
        obstacles = [ob for ob in obstacles if ob[0].y < screen_height]
        for obstacle, obstacle_type in obstacles:
            color = OBSTACLE_GREEN_COLOR if obstacle_type == 'green' else OBSTACLE_RED_COLOR
            pygame.draw.rect(screen, color, obstacle)
 
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        pygame.display.update()
        clock.tick(30)
 
def game_over_screen(score, screen, cursor, db, username):
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, FONT_SIZE)
 
    game_over_text = font.render(f"Oh no! Your score: {score}", True, TEXT_COLOR)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
 
    options = ["1. Play Again", "2. Exit"]
    for i, text in enumerate(options):
        option_surface = font.render(text, True, HIGHLIGHT_COLOR)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50 + i * 50))
        screen.blit(option_surface, option_rect)
 
    pygame.display.flip()
 




    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_loop(screen, cursor, db, username)  # Start game loop again
                elif event.key == pygame.K_2:
                    print("Exiting the game. Thank you for playing!")
                    pygame.quit()
                    sys.exit()
 
def main_menu(screen, cursor, db):
    font = pygame.font.Font(None, FONT_SIZE)
    username = get_username_input(screen)
 
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        db.commit()
        print(f"New user '{username}' added to the database.")
 
    while True:
        screen.fill(BG_COLOR)
        title_text = font.render("MAIN MENU", True, HIGHLIGHT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        pygame.draw.rect(screen, TEXT_COLOR, title_rect.inflate(20, 20), 0)
        screen.blit(title_text, title_rect)
 
        main_menu_texts = [
            "1. Play Game",
            "2. Exit",
        ]
        for i, text in enumerate(main_menu_texts):
            text_surface = font.render(text, True, HIGHLIGHT_COLOR)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 50))
            screen.blit(text_surface, text_rect)
 
        pygame.display.flip()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    score = game_loop(screen, cursor, db, username)
                    print(f"Game Over! Your Score: {score}")
                elif event.key == pygame.K_2:
                    print("Exiting the game. Thank you for playing!")
                    pygame.quit()
                    sys.exit()
 
if __name__ == "__main__":
    db, cursor = connect_database()
    screen = initialize_game()
    main_menu(screen, cursor, db)
