import pygame
import sqlite3
from entry_menu import entry_menu
if __name__ == '__main__':
    pygame.init()
    entry_menu()
#     pygame.display.set_caption('2d_shooter')
#     size = width, height = 1400, 700
#     screen = pygame.display.set_mode(size)
#
#     fps = 90
#     clock = pygame.time.Clock()
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#         pygame.display.flip()
#         clock.tick(fps)
