import pygame
import nltk
nltk.download('words')
from nltk.corpus import words
import random
import sys

# Setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Memory Typing Game")
font = pygame.font.Font(None, 64)
input_font = pygame.font.Font(None, 48)
clock = pygame.time.Clock()

# Word list
word_list = words.words()

# Timing
cycle_duration = 10000  # 10 seconds total
visible_duration = 5000  # first 5s: show word, next 5s: type

# Game state variables
input_text = ""
score = 0
feedback = ""
input_enabled = False
submitted = False
rounds = 0
MAX_ROUNDS = 100
game_over = False
start_time = None
last_cycle = -1
random_word = None

def draw_centered_text(text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(640, y))
    screen.blit(surface, rect)

# Title screen flag
show_title_screen = True

while True:
    screen.fill((30, 0, 60))  # dark purple-blue background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if show_title_screen:
            if event.type == pygame.KEYDOWN:
                # Start the game on any key press
                show_title_screen = False
                game_over = False
                rounds = 0
                score = 0
                input_text = ""
                feedback = ""
                submitted = False
                input_enabled = False
                start_time = pygame.time.get_ticks()
                last_cycle = -1
                random_word = random.choice(word_list)
        else:
            if not game_over:
                if input_enabled and not submitted:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            submitted = True
                            if input_text.lower() == random_word.lower():
                                feedback = "✅ Correct!"
                                score += 1
                            elif input_text.strip() == "":
                                feedback = f"You entered nothing! It was: {random_word}"
                                score -= 0.5
                            else:
                                feedback = f"❌ Wrong! It was: {random_word}"
                                score -= 0.5
                        else:
                            input_text += event.unicode

            else:
                # After game over, allow restart on key press
                if event.type == pygame.KEYDOWN:
                    show_title_screen = True

    if show_title_screen:
        draw_centered_text("Memory Typing Game", font, (255, 255, 255), 250)
        draw_centered_text("Press any key to start", input_font, (200, 200, 200), 350)

    else:
        if not game_over:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - start_time
            cycle = elapsed // cycle_duration
            time_in_cycle = elapsed % cycle_duration

            # New round starts
            if cycle != last_cycle:
                # If player didn't submit last round
                if input_enabled and not submitted:
                    feedback = f"⌛ Time up! You entered nothing. It was: {random_word}"
                    score -= 0.5

                rounds += 1
                if rounds > MAX_ROUNDS:
                    game_over = True
                else:
                    # Setup for next round
                    random_word = random.choice(word_list)
                    input_text = ""
                    feedback = ""
                    submitted = False
                    input_enabled = False
                    last_cycle = cycle

            if not game_over:
                if time_in_cycle < visible_duration:
                    # Show the word to memorize
                    word_surface = font.render(random_word, True, (255, 255, 255))
                    word_rect = word_surface.get_rect(center=(640, 200))
                    screen.blit(word_surface, word_rect)
                    # Clear input on screen to avoid confusion
                    draw_centered_text("Get ready...", input_font, (180, 180, 180), 350)
                else:
                    # Enable typing
                    input_enabled = True

                    input_label = input_font.render("Type the word:", True, (255, 255, 255))
                    input_rect = input_label.get_rect(center=(640, 180))
                    screen.blit(input_label, input_rect)

                    typed_surface = input_font.render(input_text, True, (255, 255, 0))
                    typed_rect = typed_surface.get_rect(center=(640, 250))
                    screen.blit(typed_surface, typed_rect)

                    if submitted or time_in_cycle > (visible_duration + 3000):  # Show feedback for 3s
                        feedback_surface = input_font.render(feedback, True, (255, 255, 255))
                        feedback_rect = feedback_surface.get_rect(center=(640, 330))
                        screen.blit(feedback_surface, feedback_rect)

            # Score and round display
            score_surface = input_font.render(f"Score: {score:.1f}", True, (255, 255, 255))
            screen.blit(score_surface, (30, 30))
            rounds_surface = input_font.render(f"Round: {rounds}/{MAX_ROUNDS}", True, (255, 255, 255))
            screen.blit(rounds_surface, (30, 80))

        else:
            # Game Over screen
            draw_centered_text("🎉 Game Over! 🎉", font, (255, 255, 255), 250)
            draw_centered_text(f"Your final score: {score:.1f}", input_font, (255, 215, 0), 320)
            draw_centered_text("Press any key to return to title", input_font, (200, 200, 200), 400)

    pygame.display.flip()
    clock.tick(60)
