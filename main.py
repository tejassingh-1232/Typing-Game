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
random_word = random.choice(word_list)

# Timing
cycle_duration = 10000  # 10 seconds total
visible_duration = 5000  # first 5s: show word, next 5s: type
start_time = pygame.time.get_ticks()
last_cycle = -1

# Game state
input_text = ""
score = 0
feedback = ""
input_enabled = False
submitted = False

running = True
while running:
    screen.fill("purple")
    current_time = pygame.time.get_ticks()
    elapsed = current_time - start_time
    cycle = elapsed // cycle_duration
    time_in_cycle = elapsed % cycle_duration

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Typing input when enabled and not submitted yet
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

    # When a new cycle starts
    if cycle != last_cycle:
        # Check if user never submitted input in last cycle
        if input_enabled and not submitted:
            feedback = f"⌛ Time up! You entered nothing. It was: {random_word}"
            score -= 0.5

        # Prepare new cycle
        random_word = random.choice(word_list)
        input_text = ""
        feedback = ""
        submitted = False
        input_enabled = False
        last_cycle = cycle

    # First 5 seconds: show word
    if time_in_cycle < visible_duration:
        word_surface = font.render(random_word, True, (255, 255, 255))
        word_rect = word_surface.get_rect(center=(640, 200))
        screen.blit(word_surface, word_rect)
    else:
        # Enable typing during second half
        input_enabled = True

        input_label = input_font.render("Type the word:", True, (255, 255, 255))
        input_rect = input_label.get_rect(center=(640, 180))
        screen.blit(input_label, input_rect)

        typed_surface = input_font.render(input_text, True, (255, 255, 0))
        typed_rect = typed_surface.get_rect(center=(640, 250))
        screen.blit(typed_surface, typed_rect)

        if submitted or time_in_cycle > (visible_duration + 3000):  # Show feedback for a few seconds
            feedback_surface = input_font.render(feedback, True, (255, 255, 255))
            feedback_rect = feedback_surface.get_rect(center=(640, 330))
            screen.blit(feedback_surface, feedback_rect)

    # Score Display
    score_surface = input_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (30, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
