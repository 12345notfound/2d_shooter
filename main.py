import pygame
import random
from math import sin, radians, cos
from PIL import Image


def pic_to_map(filename):
    im = Image.open(filename)
    pixels = im.load()
    x, y = im.size
    result = [[None for _ in range(y)] for _ in range(x)]
    for i in range(x):
        for j in range(y):
            if pixels[i, j] == (0, 0, 0):
                result[i][j] = Wall(i * 100, j * 100)
    return result




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


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = im1
        # self.image.fill('red')
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.mask = pygame.mask.from_surface(self.image)

        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.direction = 0

    def move_entity(self, x, y):
        self.rect.centerx += x
        self.rect.centery += y
        for wall in walls:
            if pygame.sprite.collide_mask(self, wall):
                self.rect.centerx -= x
                self.rect.centery -= y
                break

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self):
        xshift = 0
        yshift = 0
        turn = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_w]:
            yshift -= 5
        if keystate[pygame.K_s]:
            yshift += 5
        if keystate[pygame.K_a]:
            xshift -= 5
        if keystate[pygame.K_d]:
            xshift += 5
        if keystate[pygame.K_LEFT]:
            turn -= 3
        if keystate[pygame.K_RIGHT]:
            turn += 3
        self.move_entity(xshift, yshift)
        self.direction += turn
        self.image = pygame.transform.rotate(im1, self.direction)
        self.mask = pygame.mask.from_surface(self.image)
        for wall in walls:
            if pygame.sprite.collide_mask(self, wall):
                self.direction -= turn
                self.image = pygame.transform.rotate(im1, self.direction)
                self.mask = pygame.mask.from_surface(self.image)
                break
        self.rect = self.image.get_rect(center=self.rect.center)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, walls)
        self.image = pygame.surface.Surface((100, 100))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.mask = pygame.mask.from_surface(self.image)


if __name__ == '__main__':
    FPS = 60
    pygame.init()
    size = width, height = 1600, 900
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    walls = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    running = True
    # test
    Bullet(10, 10, 1.4, 3.8, damage=10)
    LootBox(30, 30)
    im1 = pygame.image.load('circle.png').convert()
    im1.set_colorkey((255, 255, 255))
    e = Player(550, 550)
    # w1 = Wall(300, 300)
    # Wall(300, 400)
    pic_to_map('lvl1.png')

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