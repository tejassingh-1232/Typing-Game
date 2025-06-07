import pygame
import nltk
nltk.download('words')
from nltk.corpus import words
import random

word_list = words.words()
random_word = random.choice(word_list) 
print(random_word)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    screen.fill("purple")


    pygame.display.flip()

    clock.tick(60)

pygame.quit()