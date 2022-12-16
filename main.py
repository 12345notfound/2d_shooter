import pygame
import random


class LootBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surface = pygame.surface.Surface((50, 50), masks=(10, 10, 10))


running = True

while running:
    # внутри игрового цикла ещё один цикл
    # приёма и обработки сообщений
    for event in pygame.event.get():
        # при закрытии окна
        if event.type == pygame.QUIT:
            running = False
        # РЕАКЦИЯ НА ОСТАЛЬНЫЕ СОБЫТИЯ
        # ...
    # отрисовка и изменение свойств объектов
    # ...
    pygame.display.flip()