import pygame
import random

# hello
class LootBox(pygame.sprite.Sprite):
    """Класс ящика с улучшениями"""
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = pygame.surface.Surface((50, 50))
        self.image.fill((192, 0, 192))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

class Bullet(pygame.sprite.Sprite):
    """Класс стены"""
    def __init__(self, x, y, speed_x, speed_y, damage):
        super().__init__(all_sprites)
        self.image = pygame.surface.Surface((20, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        # float coords for better (?) movement
        self.float_x = x
        self.float_y = y
        self.speedx = speed_x  # скорость по х и у
        self.speedy = speed_y
        self.damage = damage  # урон

    def update(self):
        self.float_x += self.speedx
        self.float_y += self.speedy
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        # print(self.float_x, self.float_y)
        # print()


# class Wall(pygame.sprite.Sprite):
#     """Класс стены"""
#     def __init__(self, x, y, ):


if __name__ == '__main__':
    FPS = 30
    pygame.init()
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    walls = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    running = True
    # test
    Bullet(10, 10, 1.4, 3.8, damage=10)
    LootBox(30, 30)

    while running:
        # внутри игрового цикла ещё один цикл
        # приёма и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            # РЕАКЦИЯ НА ОСТАЛЬНЫЕ СОБЫТИЯ
        # отрисовка и изменение свойств объектов
        all_sprites.update()
        screen.fill('black')
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()