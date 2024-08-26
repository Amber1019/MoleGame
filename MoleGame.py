import pygame
import random
import math
from dataclasses import dataclass
import time
import csv
from datetime import datetime

pygame.init()

bg_image = pygame.image.load("/Users/amberzhang/Documents/background.jpeg")
bg_image = pygame.transform.scale(bg_image, (bg_image.get_width() // 1.5, bg_image.get_height() // 1.5))
screen = pygame.display.set_mode((bg_image.get_width(), bg_image.get_height()))

enemy_image = pygame.image.load("/Users/amberzhang/Documents/mole_with_backgroud.png")
enemy_image = pygame.transform.scale(enemy_image, (enemy_image.get_width() // 3.75, enemy_image.get_height() // 3.75))

bomb_image = pygame.image.load("/Users/amberzhang/Documents/bomb.png")
bomb_image = pygame.transform.scale(bomb_image, (bomb_image.get_width() // 1.25, bomb_image.get_height() // 1.25))

rules_image = pygame.image.load("/Users/amberzhang/Documents/rules.png")  # 规则图片
rules_image = pygame.transform.scale(rules_image, (bg_image.get_width(), bg_image.get_height()))

score_value = 0
mole_hits = 0
bomb_hits = 0
font = pygame.font.Font('freesansbold.ttf', 32)
countdown_font = pygame.font.Font('freesansbold.ttf', 64)  # Larger font for countdown

textX = 10
textY = 10

enemies = []

ENEMY_LIFE_SPAN = 4 * 1000

@dataclass
class Enemy:
    x: int
    y: int
    is_bomb: bool = False
    life: int = ENEMY_LIFE_SPAN

ENEMY_RADIUS = min(enemy_image.get_width(), enemy_image.get_height()) // 2.5
ENEMY_COLOR = (255, 0, 0)

TOTAL_TIME = 30  # 30 seconds
start_time = None

# Schedule the appearance of 25 moles and 15 bombs over 30 seconds
appearances = [False] * 8 + [True] * 15  # False = bomb, True = mole
random.shuffle(appearances)

GENERATE_ENEMY, APPEAR_INTERVAL = pygame.USEREVENT + 1, TOTAL_TIME * 1000 // len(appearances)
AGE_ENEMY, AGE_INTERVAL = pygame.USEREVENT + 2, 1 * 1000

# Page states
PAGE_MAIN = 'main'
PAGE_RULES = 'rules'
PAGE_RESULT = 'result'
current_page = PAGE_MAIN

def generate_random_position():
    x = random.randint(0, bg_image.get_width() - enemy_image.get_width())
    y = random.randint(0, bg_image.get_height() - enemy_image.get_height())
    return x, y

def draw_enemies():
    for enemy in enemies:
        if enemy.is_bomb:
            screen.blit(bomb_image, (enemy.x, enemy.y))
        else:
            screen.blit(enemy_image, (enemy.x, enemy.y))

def show_score(x, y):
    global score_value
    score = font.render("Score: " + str(score_value), True, (0, 0, 0))  # 黑色字體
    screen.blit(score, (x, y))

def show_timer(x, y, time_left):
    timer = font.render("Time Left: " + str(time_left) + "s", True, (0, 0, 0))  # 黑色字體
    screen.blit(timer, (x, y))

def check_enemy_collision(clickX, clickY, enemyX, enemyY):
    enemyX, enemyY = enemyX + ENEMY_RADIUS, enemyY + ENEMY_RADIUS
    distance = math.sqrt(math.pow(enemyX - clickX, 2) + (math.pow(enemyY - clickY, 2)))
    return distance < ENEMY_RADIUS

def check_enemies_collision(click_pos, enemies):
    global score_value, mole_hits, bomb_hits
    for enemy in enemies:
        if check_enemy_collision(click_pos[0], click_pos[1], enemy.x, enemy.y):
            if enemy.is_bomb:
                bomb_hits += 1
                score_value -= 1
            else:
                mole_hits += 1
                score_value += 1
            enemies.remove(enemy)

def age_enemies():
    for enemy in enemies:
        enemy.life -= 1000

def remove_died_enemies():
    for enemy in enemies:
        if enemy.life <= 0:
            enemies.remove(enemy)

def draw_button(text, x, y, width, height, color, text_color=(0, 0, 0)):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, button_rect, border_radius=20)  # 圓框按鈕
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))
    return button_rect

def countdown():
    global start_time
    for i in range(5, 0, -1):
        screen.blit(bg_image, (0, 0))
        countdown_text = countdown_font.render(f"Game starts in {i}", True, (0, 0, 0))  # 黑色倒數文字
        screen.blit(countdown_text, (bg_image.get_width() // 4, bg_image.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(1000)  # 等待一秒
    start_time = time.time()  # 設定遊戲開始時間

# 初始化保存标志位
score_saved = False

def display_result():
    global current_page, start_time, score_value, mole_hits, bomb_hits, score_saved

    screen.blit(bg_image, (0, 0))  # Ensure the background is drawn
    final_message = font.render(f"Time's up! Final Score: {score_value}", True, (0, 0, 0))  # Black text
    screen.blit(final_message, (bg_image.get_width() // 4, bg_image.get_height() // 2 - 60))

    restart_button_rect = draw_button("Restart Game", bg_image.get_width() // 3, bg_image.get_height() // 2 + 20, bg_image.get_width() // 3, 100, (173, 216, 230))
    result_back_button_rect = draw_button("Back to Main Menu", bg_image.get_width() // 3, bg_image.get_height() // 2 + 140, bg_image.get_width() // 3, 100, (173, 216, 230))

    pygame.display.update()

    # 只在成绩未保存时保存成绩
    if not score_saved:
        completion_time = time.time() - start_time if start_time else 0
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
        csv_file_path = '/Users/amberzhang/Documents/final_score.csv'

        with open(csv_file_path, mode='a', newline='') as file:  # Append mode
            writer = csv.writer(file)
            writer.writerow(["Final Score", "Mole Hits", "Bomb Hits", "Completion Time (s)", "Date and Time"])
            writer.writerow([score_value, mole_hits, bomb_hits, round(completion_time, 2), current_time])

        score_saved = True  # 设置标志位，表示成绩已保存

    return restart_button_rect, result_back_button_rect

def reset_game():
    global score_value, mole_hits, bomb_hits, start_time, enemies, appearances, game_started, score_saved
    score_value = 0
    mole_hits = 0
    bomb_hits = 0
    start_time = None
    enemies = []
    appearances = [False] * 8 + [True] * 15 # False = bomb, True = mole
    random.shuffle(appearances)
    game_started = False
    score_saved = False  # 重置标志位，允许下一次保存成绩


running = True
game_started = False
start_button_rect = None
rules_button_rect = None
back_button_rect = None
restart_button_rect = None
result_back_button_rect = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            click_pos = pygame.mouse.get_pos()

            if current_page == PAGE_MAIN:
                if not game_started:
                    if start_button_rect and start_button_rect.collidepoint(click_pos):
                        countdown()  # 倒數五秒
                        game_started = True
                        pygame.time.set_timer(GENERATE_ENEMY, APPEAR_INTERVAL)
                        pygame.time.set_timer(AGE_ENEMY, AGE_INTERVAL)
                    elif rules_button_rect and rules_button_rect.collidepoint(click_pos):
                        current_page = PAGE_RULES
                else:
                    check_enemies_collision(click_pos, enemies)

            elif current_page == PAGE_RULES:
                if back_button_rect and back_button_rect.collidepoint(click_pos):
                    current_page = PAGE_MAIN

            elif current_page == PAGE_RESULT:
                if restart_button_rect and restart_button_rect.collidepoint(click_pos):
                    reset_game()
                    countdown()  # Start countdown again
                    game_started = True
                    pygame.time.set_timer(GENERATE_ENEMY, APPEAR_INTERVAL)
                    pygame.time.set_timer(AGE_ENEMY, AGE_INTERVAL)
                    current_page = PAGE_MAIN
                elif result_back_button_rect and result_back_button_rect.collidepoint(click_pos):
                    reset_game()  # Reset game state before going back to the main menu
                    current_page = PAGE_MAIN

        if event.type == AGE_ENEMY and game_started and current_page == PAGE_MAIN:
            age_enemies()
            remove_died_enemies()

        if event.type == GENERATE_ENEMY and game_started and appearances and current_page == PAGE_MAIN:
            if len(enemies) < 10:  # Limiting to a maximum of 10 enemies on screen at once
                new_pos = generate_random_position()
                is_bomb = appearances.pop(0)
                enemies.append(Enemy(new_pos[0], new_pos[1], not is_bomb))

    if current_page == PAGE_MAIN:
        screen.blit(bg_image, (0, 0))
        if not game_started:
            start_button_rect = draw_button("Start Game", bg_image.get_width() // 3, bg_image.get_height() // 2 - 100, bg_image.get_width() // 3, 100, (173, 216, 230))
            rules_button_rect = draw_button("Rules", bg_image.get_width() // 3, bg_image.get_height() // 2 + 50, bg_image.get_width() // 3, 100, (173, 216, 230))
        
        if game_started and start_time:
            elapsed_time = time.time() - start_time
            time_left = max(0, TOTAL_TIME - int(elapsed_time))
            if time_left <= 0:
                current_page = PAGE_RESULT
            else:
                draw_enemies()
                show_score(textX, textY)
                show_timer(textX, textY + 40, time_left)
        
        pygame.display.update()

    elif current_page == PAGE_RULES:
        screen.blit(rules_image, (0, 0))
        back_button_rect = draw_button("Back", bg_image.get_width() - 150, bg_image.get_height() - 80, 100, 50, (173, 216, 230))
        pygame.display.update()

    elif current_page == PAGE_RESULT:
        restart_button_rect, result_back_button_rect = display_result()

# After the loop ends, save the score to a CSV file with date and time
# completion_time = time.time() - start_time if start_time else 0
# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
# csv_file_path = '/Users/amberzhang/Documents/final_score.csv'

# with open(csv_file_path, mode='a', newline='') as file:  # Append mode
#     writer = csv.writer(file)
#     writer.writerow(["Final Score", "Mole Hits", "Bomb Hits", "Completion Time (s)", "Date and Time"])
#     writer.writerow([score_value, mole_hits, bomb_hits, round(completion_time, 2), current_time])

# pygame.quit()
