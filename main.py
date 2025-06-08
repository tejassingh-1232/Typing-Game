import pygame
import nltk
import random
import sys
import math
import json
import os

# Download words corpus only once
nltk.download('words', quiet=True)
from nltk.corpus import words

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Memory Typing Game")

# Fonts
font = pygame.font.Font(None, 64)
input_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 32)

# Clock
clock = pygame.time.Clock()

# Load word list and filter for increasing difficulty
word_list = [w for w in words.words() if w.isalpha() and len(w) <= 7]

# Sound setup
pygame.mixer.init()
def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except:
        return None

sound_correct = load_sound("correct.wav")
sound_wrong = load_sound("wrong.wav")
sound_key = load_sound("key.wav")
sound_fade = load_sound("fade.wav")

# Background music
try:
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
except:
    print("Background music file not found!")

# Game mode
MODE = None  # "ranked" or "freestyle"
MAX_ROUNDS = 100  # default for ranked

# Leaderboard file
LEADERBOARD_FILE = "leaderboard.json"

# Game variables
score = 0
rounds = 0
input_text = ""
feedback = ""
input_enabled = False
submitted = False
game_over = False
show_title_screen = True
fade_alpha = 0
fading = False
fade_direction = 1
transition_to = None
start_time = None
last_cycle = -1
random_word = None

# Animation vars
title_anim_time = 0
press_key_blink_time = 0
press_key_visible = True
gameover_slide_y = -100
gameover_score_alpha = 0
feedback_alpha = 255
score_pulse_time = 0

# Background gradient animation colors
bg_color_1 = (30, 0, 60)
bg_color_2 = (10, 50, 100)
bg_anim_time = 0

# Menu
menu_index = 0
menu_options = ["Ranked Mode", "Freestyle Mode"]

def draw_centered_text(text, font, color, y, scale=1.0, alpha=255):
    surf = font.render(text, True, color)
    if scale != 1.0:
        size = surf.get_size()
        surf = pygame.transform.smoothscale(surf, (int(size[0]*scale), int(size[1]*scale)))
    surf.set_alpha(alpha)
    rect = surf.get_rect(center=(640, y))
    screen.blit(surf, rect)

def start_fade(direction, next_screen):
    global fading, fade_direction, transition_to, fade_alpha
    fading = True
    fade_direction = direction
    transition_to = next_screen
    fade_alpha = 0 if direction == 1 else 255
    if sound_fade:
        sound_fade.play()

def update_fade():
    global fade_alpha, fading, show_title_screen, game_over, rounds, score, input_text, feedback, submitted, input_enabled, start_time, last_cycle, random_word, transition_to, fade_direction, MODE
    if fading:
        fade_alpha += fade_direction * 15
        fade_alpha = max(0, min(255, fade_alpha))
        if fade_alpha >= 255 and fade_direction == 1:
            if transition_to == "game":
                reset_game()
                show_title_screen = False
                game_over = False
                pygame.mixer.music.play(-1)
            elif transition_to == "title":
                show_title_screen = True
                game_over = False
                pygame.mixer.music.stop()
            elif transition_to == "gameover":
                game_over = True
                show_title_screen = False
            transition_to = None
            fade_direction = -1
        elif fade_alpha <= 0 and fade_direction == -1:
            fading = False

def reset_game():
    global score, rounds, input_text, feedback, submitted, input_enabled, start_time, last_cycle, random_word
    score = 0
    rounds = 0
    input_text = ""
    feedback = ""
    submitted = False
    input_enabled = False
    start_time = pygame.time.get_ticks()
    last_cycle = -1
    random_word = random.choice(word_list)

def play_sound(sound):
    if sound:
        sound.play()

def save_leaderboard(score):
    if MODE != "ranked":
        return []
    data = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    name = input("Enter your name: ")[:12]
    data.append({"name": name, "score": score})
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f)
    return data

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            try:
                data = json.load(f)
                return sorted(data, key=lambda x: x["score"], reverse=True)[:5]
            except:
                return []
    return []

def get_dynamic_word():
    length = 3 + rounds // 10
    length = min(length, 7)
    filtered = [w for w in word_list if len(w) == length]
    return random.choice(filtered) if filtered else random.choice(word_list)

def get_visible_duration():
    return max(2000, 5000 - (rounds // 10) * 500)

cycle_duration = 10000
visible_duration_base = 5000

while True:
    dt = clock.tick(60) / 1000
    bg_anim_time += dt
    interp = (math.sin(bg_anim_time) + 1) / 2
    r = int(bg_color_1[0] * (1 - interp) + bg_color_2[0] * interp)
    g = int(bg_color_1[1] * (1 - interp) + bg_color_2[1] * interp)
    b = int(bg_color_1[2] * (1 - interp) + bg_color_2[2] * interp)
    screen.fill((r, g, b))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if show_title_screen:
            if event.type == pygame.KEYDOWN and not fading:
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    MODE = "ranked" if menu_index == 0 else "freestyle"
                    MAX_ROUNDS = 100 if MODE == "ranked" else 999999
                    start_fade(1, "game")

        elif game_over:
            if event.type == pygame.KEYDOWN and not fading:
                start_fade(1, "title")

        else:
            if input_enabled and not submitted and not fading:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        play_sound(sound_key)
                    elif event.key == pygame.K_RETURN:
                        submitted = True
                        if input_text.lower() == random_word.lower():
                            feedback = "✅ Correct!"
                            score += 1
                            play_sound(sound_correct)
                        elif input_text.strip() == "":
                            feedback = f"You entered nothing! It was: {random_word}"
                            score -= 0.5
                            play_sound(sound_wrong)
                        else:
                            feedback = f"❌ Wrong! It was: {random_word}"
                            score -= 0.5
                            play_sound(sound_wrong)
                        feedback_alpha = 255
                    else:
                        if event.unicode.isalpha():
                            input_text += event.unicode
                            play_sound(sound_key)

    update_fade()

    if show_title_screen:
        draw_centered_text("Memory Typing Game", font, (255, 255, 255), 200)
        for i, option in enumerate(menu_options):
            color = (255, 255, 0) if i == menu_index else (200, 200, 200)
            draw_centered_text(option, input_font, color, 300 + i * 60)
        draw_centered_text("Use UP/DOWN and ENTER", small_font, (180, 180, 180), 500)

    elif game_over:
        if gameover_slide_y < 250:
            gameover_slide_y += 300 * dt
            if gameover_slide_y > 250:
                gameover_slide_y = 250
        draw_centered_text("🎉 Game Over! 🎉", font, (255, 255, 255), gameover_slide_y)
        if gameover_slide_y >= 250 and gameover_score_alpha < 255:
            gameover_score_alpha += 300 * dt
        score_surf = input_font.render(f"Your final score: {score:.1f}", True, (255, 215, 0))
        score_surf.set_alpha(int(gameover_score_alpha))
        screen.blit(score_surf, score_surf.get_rect(center=(640, 320)))
        leaderboard = load_leaderboard()
        draw_centered_text("Leaderboard (Top 5):", small_font, (255, 255, 255), 380, alpha=int(gameover_score_alpha))
        for i, s in enumerate(leaderboard):
            text = f"{i+1}. {s['name']}: {s['score']:.1f}"
            draw_centered_text(text, small_font, (255, 215, 0), 410 + i * 30, alpha=int(gameover_score_alpha))
        if gameover_score_alpha >= 255:
            draw_centered_text("Press any key to return to title", input_font, (200, 200, 200), 550)

    else:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        cycle = elapsed // cycle_duration
        time_in_cycle = elapsed % cycle_duration

        if cycle != last_cycle:
            if input_enabled and not submitted:
                feedback = f"⌛ Time up! You entered nothing. It was: {random_word}"
                score -= 0.5
                play_sound(sound_wrong)
                feedback_alpha = 255
            rounds += 1
            if rounds > MAX_ROUNDS:
                save_leaderboard(score)
                start_fade(1, "gameover")
            else:
                random_word = get_dynamic_word()
                input_text = ""
                feedback = ""
                submitted = False
                input_enabled = False
                last_cycle = cycle
                visible_duration_base = get_visible_duration()

        if rounds <= MAX_ROUNDS:
            visible_duration = visible_duration_base
            if time_in_cycle < visible_duration:
                progress = time_in_cycle / visible_duration
                x_pos = int(640 * (0.2 + 0.8 * progress))
                word_surface = font.render(random_word, True, (255, 255, 255))
                word_rect = word_surface.get_rect(center=(x_pos, 200))
                screen.blit(word_surface, word_rect)
                draw_centered_text("Get ready...", input_font, (180, 180, 180), 350)
            else:
                input_enabled = True
                input_prompt_alpha = min(255, int(255 * (time_in_cycle - visible_duration) / 1000))
                input_label = input_font.render("Type the word:", True, (255, 255, 255))
                input_label.set_alpha(input_prompt_alpha)
                screen.blit(input_label, input_label.get_rect(center=(640, 180)))
                typed_surface = input_font.render(input_text, True, (255, 255, 0))
                screen.blit(typed_surface, typed_surface.get_rect(center=(640, 250)))
                if feedback:
                    feedback_alpha = max(0, feedback_alpha - 200 * dt)
                    feedback_surface = input_font.render(feedback, True, (255, 255, 255))
                    feedback_surface.set_alpha(int(feedback_alpha))
                    screen.blit(feedback_surface, feedback_surface.get_rect(center=(640, 330)))
        score_pulse_time += dt * 5
        pulse_scale = 1 + 0.1 * math.sin(score_pulse_time)
        score_color = (255, 215, 0)
        score_surface = input_font.render(f"Score: {score:.1f}", True, score_color)
        size = score_surface.get_size()
        score_surface = pygame.transform.smoothscale(score_surface, (int(size[0]*pulse_scale), int(size[1]*pulse_scale)))
        screen.blit(score_surface, (30, 30))
        rounds_surface = input_font.render(f"Round: {rounds}/{MAX_ROUNDS if MODE == 'ranked' else '∞'}", True, (255, 255, 255))
        screen.blit(rounds_surface, (30, 80))

    if fading or fade_alpha > 0:
        fade_surface = pygame.Surface((1280, 720))
        fade_surface.set_alpha(int(fade_alpha))
        fade_surface.fill((0, 0, 0))
        screen.blit(fade_surface, (0, 0))

    pygame.display.flip()
