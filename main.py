# Memory Typing Game with Name Input and Leaderboard
import pygame
import nltk
import random
import sys
import math
import json
import os

nltk.download('words', quiet=True)
from nltk.corpus import words

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Memory Typing Game")

font = pygame.font.Font(None, 64)
input_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 32)

clock = pygame.time.Clock()

word_list = [w for w in words.words() if w.isalpha() and len(w) <= 7]

# Sound
sound_correct = None
sound_wrong = None
sound_key = None
sound_fade = None

def play_sound(sound):
    if sound:
        sound.play()

# Game constants
MAX_ROUNDS = 100
cycle_duration = 10000
visible_duration_base = 5000
LEADERBOARD_FILE = "leaderboard.json"

# Game variables
score = 0
rounds = 0
input_text = ""
feedback = ""
input_enabled = False
submitted = False
show_title_screen = True
game_over = False
fade_alpha = 0
fading = False
fade_direction = 1
transition_to = None
start_time = None
last_cycle = -1
random_word = None

# Animation
title_anim_time = 0
press_key_blink_time = 0
press_key_visible = True
gameover_slide_y = -100
gameover_score_alpha = 0
feedback_alpha = 255
score_pulse_time = 0

# Background
bg_color_1 = (30, 0, 60)
bg_color_2 = (10, 50, 100)
bg_anim_time = 0

# New vars for name input
entering_name = False
player_name = ""
name_input_done = False

# Leaderboard helpers
def save_leaderboard(name, score):
    data = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    data.append({"name": name, "score": score})
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def draw_centered_text(text, font, color, y, scale=1.0, alpha=255):
    surf = font.render(text, True, color)
    if scale != 1.0:
        size = surf.get_size()
        surf = pygame.transform.smoothscale(surf, (int(size[0]*scale), int(size[1]*scale)))
    surf.set_alpha(alpha)
    rect = surf.get_rect(center=(640, y))
    screen.blit(surf, rect)

def reset_game():
    global score, rounds, input_text, feedback, submitted, input_enabled, start_time, last_cycle, random_word, visible_duration_base, entering_name, name_input_done, player_name
    score = 0
    rounds = 0
    input_text = ""
    feedback = ""
    submitted = False
    input_enabled = False
    start_time = pygame.time.get_ticks()
    last_cycle = -1
    visible_duration_base = 5000
    random_word = random.choice(word_list)
    entering_name = False
    name_input_done = False
    player_name = ""

def get_dynamic_word():
    length = 3 + rounds // 10
    length = min(length, 7)
    filtered = [w for w in word_list if len(w) == length]
    return random.choice(filtered) if filtered else random.choice(word_list)

def get_visible_duration():
    return max(2000, visible_duration_base - (rounds // 10) * 500)

def start_fade(direction, next_screen):
    global fading, fade_direction, transition_to, fade_alpha
    fading = True
    fade_direction = direction
    transition_to = next_screen
    fade_alpha = 0 if direction == 1 else 255

def update_fade():
    global fade_alpha, fading, show_title_screen, game_over, transition_to, fade_direction
    if fading:
        fade_alpha += fade_direction * 15
        fade_alpha = max(0, min(255, fade_alpha))
        if fade_alpha >= 255 and fade_direction == 1:
            if transition_to == "game":
                reset_game()
                show_title_screen = False
            elif transition_to == "title":
                show_title_screen = True
            elif transition_to == "gameover":
                game_over = True
            fade_direction = -1
        elif fade_alpha <= 0 and fade_direction == -1:
            fading = False

# Game loop
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

        if entering_name:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN and player_name.strip():
                    name_input_done = True
                    entering_name = False
                    save_leaderboard(player_name, score)
                    start_fade(1, "gameover")
                elif len(player_name) < 12 and event.unicode.isprintable():
                    player_name += event.unicode

        elif show_title_screen and event.type == pygame.KEYDOWN and not fading:
            start_fade(1, "game")

        elif game_over and event.type == pygame.KEYDOWN and not fading:
            start_fade(1, "title")

        elif input_enabled and not submitted and not fading:
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
                    else:
                        feedback = f"❌ Wrong! It was: {random_word}"
                        score -= 0.5
                        play_sound(sound_wrong)
                    feedback_alpha = 255
                elif event.unicode.isalpha():
                    input_text += event.unicode
                    play_sound(sound_key)

    update_fade()

    if show_title_screen:
        title_anim_time += dt
        pulse = 1 + 0.1 * math.sin(title_anim_time * 3)
        draw_centered_text("Memory Typing Game", font, (255, 255, 255), 250, scale=pulse)
        press_key_blink_time += dt
        if press_key_blink_time > 0.7:
            press_key_visible = not press_key_visible
            press_key_blink_time = 0
        if press_key_visible:
            draw_centered_text("Press any key to start", input_font, (200, 200, 200), 350)

    elif entering_name:
        draw_centered_text("Enter Your Name:", font, (255, 255, 255), 220)
        draw_centered_text(player_name + "_", input_font, (255, 255, 0), 300)
        draw_centered_text("Press Enter to continue", small_font, (200, 200, 200), 380)

    elif game_over:
        if gameover_slide_y < 250:
            gameover_slide_y += 300 * dt
        draw_centered_text("🎉 Game Over! 🎉", font, (255, 255, 255), gameover_slide_y)
        if gameover_slide_y >= 250 and gameover_score_alpha < 255:
            gameover_score_alpha += 300 * dt
        score_surf = input_font.render(f"Your final score: {score:.1f}", True, (255, 215, 0))
        score_surf.set_alpha(gameover_score_alpha)
        screen.blit(score_surf, score_surf.get_rect(center=(640, 320)))
        leaderboard = load_leaderboard()
        draw_centered_text("🏆 Leaderboard (Top 5):", small_font, (255, 255, 255), 380, alpha=gameover_score_alpha)
        for i, entry in enumerate(leaderboard):
            text = f"{i+1}. {entry['name']} — {entry['score']:.1f}"
            draw_centered_text(text, small_font, (255, 215, 0), 410 + i*30, alpha=gameover_score_alpha)
        if gameover_score_alpha >= 255:
            draw_centered_text("Press any key to return to title", input_font, (200, 200, 200), 550)

    else:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        cycle = elapsed // cycle_duration
        time_in_cycle = elapsed % cycle_duration

        if cycle != last_cycle:
            if input_enabled and not submitted:
                feedback = f"⌛ Time up! It was: {random_word}"
                score -= 0.5
                play_sound(sound_wrong)
            rounds += 1
            if rounds > MAX_ROUNDS:
                if not entering_name and not name_input_done:
                    entering_name = True
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
                screen.blit(word_surface, word_surface.get_rect(center=(x_pos, 200)))
                draw_centered_text("Get ready...", input_font, (180, 180, 180), 350)
            else:
                input_enabled = True
                alpha = min(255, int(255 * (time_in_cycle - visible_duration) / 1000))
                input_label = input_font.render("Type the word:", True, (255, 255, 255))
                input_label.set_alpha(alpha)
                screen.blit(input_label, input_label.get_rect(center=(640, 180)))
                typed_surface = input_font.render(input_text, True, (255, 255, 0))
                screen.blit(typed_surface, typed_surface.get_rect(center=(640, 250)))
                if feedback:
                    feedback_alpha = max(0, feedback_alpha - 200 * dt)
                    fb = input_font.render(feedback, True, (255, 255, 255))
                    fb.set_alpha(int(feedback_alpha))
                    screen.blit(fb, fb.get_rect(center=(640, 330)))

        score_pulse_time += dt * 5
        scale = 1 + 0.1 * math.sin(score_pulse_time)
        score_surface = input_font.render(f"Score: {score:.1f}", True, (255, 215, 0))
        sz = score_surface.get_size()
        score_surface = pygame.transform.smoothscale(score_surface, (int(sz[0]*scale), int(sz[1]*scale)))
        screen.blit(score_surface, (30, 30))
        rounds_surface = input_font.render(f"Round: {rounds}/{MAX_ROUNDS}", True, (255, 255, 255))
        screen.blit(rounds_surface, (30, 80))

    if fading or fade_alpha > 0:
        fade_surface = pygame.Surface((1280, 720))
        fade_surface.set_alpha(int(fade_alpha))
        fade_surface.fill((0, 0, 0))
        screen.blit(fade_surface, (0, 0))

    pygame.display.flip()
