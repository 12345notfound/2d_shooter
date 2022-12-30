import pygame
import random
from math import sin, radians, cos, asin, pi, degrees

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


class Weapon:
    def __init__(self, speed, damage, frequency, clip_size, ammo, reload_time):
        self.speed = speed
        self.damage = damage
        self.frequency = frequency
        self.frequency_now = 0
        self.spread = [1, -3, -1, 3, 2, -2, 0]
        self.spread_now = 0

        self.interface_image = sniper_rifle_image
        self.clip_size = clip_size  # размер магазина
        self.clip = 5  # кол-во патронов в магазине
        self.ammo = ammo  # кол-во патронов вне магазина
        self.reload_time = reload_time  # время перезарядки (в мс)
        self.reload_progress = self.reload_time

    def update(self):
        if self.reload_progress < self.reload_time:
            self.reload_progress += 1
            if self.reload_progress == self.reload_time:
                prev_ammo = self.clip
                self.clip = min(self.clip_size, self.ammo + self.clip)
                self.ammo -= self.clip - prev_ammo
        else:
            if self.frequency_now > 0:
                self.frequency_now -= 1
            if pygame.mouse.get_pressed()[0] and self.frequency_now == 0:
                # стрельба
                self.spread_now = (self.spread_now + 1) % len(self.spread)
                turn = player.direction + self.spread[self.spread_now]
                Bullet(player.rect.centerx - sin(radians(turn)) * self.speed * 3,
                       player.rect.centery - cos(radians(turn)) * self.speed * 3,
                       -sin(radians(turn)) * self.speed,
                       -cos(radians(turn)) * self.speed, damage=self.damage)
                self.frequency_now = self.frequency
                self.clip -= 1
                # перезарядка если пуль не осталось
                if self.clip == 0:
                    self.reload_progress = 0
            # перезарядка по кнопке R
            if pygame.key.get_pressed()[pygame.K_r] and self.reload_progress == self.reload_time and self.clip != self.clip_size:
                self.reload_progress = 0

    def draw_interface(self):
        """Отрисовка интерфейса оружия"""
        self.font = pygame.font.Font(None, 30)
        self.ammo_str = self.font.render(str(self.clip) + ' / ' + str(self.ammo), True, (255, 0, 0))
        screen.blit(self.ammo_str, (int(width * 0.90), int(height * 0.80)))
        pygame.draw.rect(screen, width=1, rect=(int(width * 0.90), int(height * 0.85),
                                                52, 12), color='grey')
        pygame.draw.rect(screen, width=0, rect=(int(width * 0.90) + 1, int(height * 0.85) + 1,
                                                int(50 * self.reload_progress / self.reload_time), 10), color=(255, 0, 0))
        screen.blit(self.interface_image, (int(width * 0.6), int(height * 0.7)))


class SniperRifle(Weapon):
    def __init__(self):
        super().__init__(speed=50, damage=10, frequency=50,
                         clip_size=5, ammo=15, reload_time=3 * FPS)
        self.interface_image = sniper_rifle_image


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
    """Класс пули"""

    def __init__(self, x, y, speed_x, speed_y, damage):
        super().__init__(all_sprites)
        self.image = pygame.surface.Surface((10, 10))
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
        self.float_x = self.rect.centerx + self.speedx + self.float_x - int(self.float_x)
        self.float_y = self.rect.centery + self.speedy + self.float_y - int(self.float_y)
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        if pygame.sprite.spritecollide(self, walls, False):
            self.kill()


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = im1
        # self.image.fill('red')
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        # self.mask = pygame.mask.from_surface(self.image)

        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.direction = 0

    def move_entity(self, x, y):
        """Переместить сущность на координаты х, y"""
        start_x, start_y = self.rect.centerx, self.rect.centery
        self.rect = self.image.get_rect(size=(50, 50), center=self.rect.center)
        self.rect.centerx = start_x + x
        self.rect.centery = start_y + y
        x_move, y_move, xy_move = True, True, True
        xshift = 0
        yshift = 0
        for wall in walls:
            if pygame.sprite.collide_rect(self, wall):
                xy_move = False
                break
        self.rect.centerx = start_x + x
        self.rect.centery = start_y
        for wall in walls:
            if pygame.sprite.collide_rect(self, wall):
                x_move = False
                break
        self.rect.centerx = start_x
        self.rect.centery = start_y + y
        for wall in walls:
            if pygame.sprite.collide_rect(self, wall):
                y_move = False
                break
        if xy_move:
            self.rect.centerx = start_x + x
            self.rect.centery = start_y + y
        elif x_move:
            self.rect.centerx = start_x + x
            self.rect.centery = start_y
        elif y_move:
            self.rect.centerx = start_x
            self.rect.centery = start_y + y
        else:
            self.rect.centerx = start_x
            self.rect.centery = start_y

    def draw_health_bar(self, health_color, health):
        pygame.draw.rect(screen, width=1, rect=(self.rect.centerx - 26, self.rect.centery - 50, 52, 12), color='black')
        pygame.draw.rect(screen, width=0,
                         rect=(self.rect.centerx - 25, self.rect.centery - 49, int(50 * health / self.max_health), 10),
                         color=health_color)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self):
        xshift = 0
        yshift = 0

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_w]:
            yshift -= 5
        if keystate[pygame.K_s]:
            yshift += 5
        if keystate[pygame.K_a]:
            xshift -= 5
        if keystate[pygame.K_d]:
            xshift += 5

        # поворот персонажа к курсору
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        if self.rect.centery != mouse_y or self.rect.centerx != mouse_x:
            self.turn = pi / 2 - asin(((self.rect.centery - mouse_y) / (
                    (self.rect.centerx - mouse_x) ** 2 + (self.rect.centery - mouse_y) ** 2) ** 0.5))
            if self.rect.centerx > mouse_x:
                self.turn = degrees(self.turn)
            else:
                self.turn = -degrees(self.turn)
            self.direction = self.turn
        self.move_entity(xshift, yshift)
        self.image = pygame.transform.rotate(im1, self.direction)
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


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


if __name__ == '__main__':

    FPS = 60
    pygame.init()
    size = width, height = 1400, 700
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    walls = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    sniper_rifle_image = pygame.image.load('sniper_rifle.png').convert()
    sniper_rifle_image.set_colorkey((255, 255, 255))
    im1 = pygame.image.load('circle.png').convert()
    im1.set_colorkey((255, 255, 255))

    weapon = SniperRifle()  # снайперская винтовка
    running = True
    # test1
    Bullet(10, 10, 1.4, 3.8, damage=10)
    LootBox(30, 30)
    camera = Camera()

    player = Player(550, 550)
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
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        weapon.update()
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill('black')
        all_sprites.draw(screen)
        player.draw_health_bar('green', player.health)

        weapon.draw_interface()

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
