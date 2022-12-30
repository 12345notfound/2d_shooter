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
    def __init__(self, speed, damage, frequency, clip_size, ammo, reload_time, who, queue=-1):
        self.speed = speed
        self.damage = damage
        self.frequency = frequency
        self.frequency_now = 0
        self.queue = queue
        self.queue_counter = 0
        self.who = who

        self.interface_image = sniper_rifle_image
        self.clip_size = clip_size  # размер магазина
        self.clip = clip_size  # кол-во патронов в магазине
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
            if self.clip > 0:
                if pygame.mouse.get_pressed()[0] and self.frequency_now <= 0:
                    self.spread_now = 1
                    self.queue_counter += 1
                    if self.queue_counter >= self.queue and self.queue >= 0:
                        self.spread_now += 1
                    if player.movement:
                        self.spread_now += 2
                    print(self.spread_now)
                    # стрельба
                    turn = self.who.direction + random.randint(-self.spread_now, self.spread_now)
                    Bullet(self.who.rect.centerx - sin(radians(turn)) * 50,
                           self.who.rect.centery - cos(radians(turn)) * 50,
                           -sin(radians(turn)) * self.speed,
                           -cos(radians(turn)) * self.speed, damage=self.damage)
                    self.frequency_now = self.frequency
                    self.clip -= 1
                    # перезарядка если пуль не осталось
                    if self.clip == 0 and self.ammo > 0:
                        self.reload_progress = 0
                self.frequency_now -= 1
                if self.frequency_now <= -2:
                    self.frequency_now = 0
                    self.queue_counter = 0
                # перезарядка по кнопке R
                if pygame.key.get_pressed()[
                    pygame.K_r] and self.reload_progress == self.reload_time and self.clip != self.clip_size:
                    self.reload_progress = 0

    def draw_interface(self):
        """Отрисовка интерфейса оружия"""
        self.font = pygame.font.Font(None, 30)
        self.ammo_str = self.font.render(str(self.clip) + ' / ' + str(self.ammo), True, (255, 0, 0))
        screen.blit(self.ammo_str, (int(width * 0.90), int(height * 0.80)))
        pygame.draw.rect(screen, width=1, rect=(int(width * 0.90), int(height * 0.85),
                                                52, 12), color='grey')
        pygame.draw.rect(screen, width=0, rect=(int(width * 0.90) + 1, int(height * 0.85) + 1,
                                                int(50 * self.reload_progress / self.reload_time), 10),
                         color=(255, 0, 0))
        screen.blit(self.interface_image, (int(width * 0.6), int(height * 0.7)))


class SniperRifle(Weapon):
    def __init__(self, whose):
        super().__init__(speed=100, damage=100, frequency=60,
                         clip_size=5, ammo=20, reload_time=3 * FPS, who=whose)
        self.interface_image = sniper_rifle_image


class Ak_47(Weapon):
    def __init__(self, whose):
        super().__init__(speed=50, damage=10, frequency=5,
                         clip_size=1000, ammo=100, who=whose, reload_time=3 * FPS, queue=15)
        self.interface_image = sniper_rifle_image


class LootBox(pygame.sprite.Sprite):
    """Класс ящика с улучшениями"""

    def __init__(self, x, y):
        super().__init__(all_sprites, other_sprites)
        self.image = pygame.surface.Surface((50, 50))
        self.image.fill((192, 0, 192))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        pass


class Bullet(pygame.sprite.Sprite):
    """Класс пули"""

    def __init__(self, x, y, speed_x, speed_y, damage):
        super().__init__(all_sprites, bullets)
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
        self.float_x = self.rect.centerx + self.speedx / 30 + self.float_x - int(self.float_x)
        self.float_y = self.rect.centery + self.speedy / 30 + self.float_y - int(self.float_y)
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        for _ in range(29):
            self.float_x += self.speedx / 30
            self.float_y += self.speedy / 30
            self.rect.centerx = int(self.float_x)
            self.rect.centery = int(self.float_y)
            if pygame.sprite.spritecollide(self, walls, False) or pygame.sprite.spritecollide(self, characters, False):
                self.kill()


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, characters)
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
        self.rect = self.image.get_rect(size=(65, 65), center=self.rect.center)
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
            self.movement = True
            self.rect.centerx = start_x + x
            self.rect.centery = start_y + y
        elif x_move:
            self.movement = True
            self.rect.centerx = start_x + x
            self.rect.centery = start_y
        elif y_move:
            self.movement = True
            self.rect.centerx = start_x
            self.rect.centery = start_y + y
        else:
            self.movement = True
            self.rect.centerx = start_x
            self.rect.centery = start_y
        if x == 0 and y == 0:
            self.movement = False

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
        self.movement = False
        self.move_entity(xshift, yshift)
        self.image = pygame.transform.rotate(im1, self.direction)
        self.rect = self.image.get_rect(center=self.rect.center)


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self):
        xshift = 0
        yshift = 0

        mouse_x = player.rect.centerx
        mouse_y = player.rect.centery
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

    def update(self):
        pass


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
    walls = pygame.sprite.Group()  # стены
    characters = pygame.sprite.Group()  # персонажи
    other_sprites = pygame.sprite.Group()  # все остальное
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    sniper_rifle_image = pygame.image.load('sniper_rifle.png').convert()
    sniper_rifle_image.set_colorkey((255, 255, 255))
    im1 = pygame.image.load('Игрок_2.png').convert()
    im1.set_colorkey((255, 255, 255))

    running = True
    # test1
    Bullet(10, 10, 1.4, 3.8, damage=10)
    LootBox(30, 30)
    camera = Camera()

    player = Player(550, 550)
    weapon = Ak_47(player)  # снайперская винтовка
    enemy1 = Enemy(90, 90)
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
        # characters.update()
        weapon.update()
        characters.update()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill('black')
        other_sprites.draw(screen)
        walls.draw(screen)
        characters.draw(screen)
        other_sprites.draw(screen)
        walls.draw(screen)
        for i in characters:
            i.rect = i.image.get_rect(size=(65, 65), center=i.rect.center)
        bullets.update()
        bullets.draw(screen)

        # all_sprites.update()
        # player.rect =player.image.get_rect(size=(80, 80), center=player.rect.center)       # изменяем ракурс камеры
        # camera.update(player)
        # обновляем положение всех спрайтов
        # for sprite in all_sprites:
        # camera.apply(sprite)
        # all_sprites.draw(screen)
        # characters.draw(screen)
        player.draw_health_bar('green', player.health)

        weapon.draw_interface()

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
