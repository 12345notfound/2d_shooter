import pygame
from interface import text_output, InputBox, Button_rect
import sqlite3
import hashlib

def button_end(numder):
    if numder==1:
        pass
    else:
        pass
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('2d_shooter')
    size = width, height = 1400, 700
    screen = pygame.display.set_mode(size)

    background = pygame.image.load('Все для дизайна/Проигрыш.jpg').convert()
    background = pygame.transform.smoothscale(background, screen.get_size())

    buttons = []
    buttons.append(Button_rect(screen, 243, 350, 910, 110, lambda:button_end(1)))
    buttons.append(Button_rect(screen, 243,502, 910, 110, lambda:button_end(2)))

    fps = 60
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(background, (0, 0))
        for button in buttons:
            button.update()
        pygame.display.flip()
        clock.tick(fps)