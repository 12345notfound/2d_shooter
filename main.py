import os

import pygame
import random
from math import sin, radians, cos, asin, pi, degrees

from PIL import Image


def pic_to_map(filename):
    """Переводит картинку в карту"""

    im = Image.open(filename)
    pixels = im.load()
    x, y = im.size
    result = [[False for _ in range(y)] for _ in range(x)]
    for i in range(x):
        for j in range(y):
            if pixels[i, j] == (237, 28, 36):  # 237,28,36 / 0,0,0
                Wall(i * 50, j * 50)
                result[i][j] = True
            elif pixels[i, j] == (34, 177, 76):
                if pixels[i + 1, j] == (255, 242, 0):
                    Door(i * 50 + 25, j * 50, 1)
                    result[i][j] = [True, 1]
                    result[i + 1][j] = [True, 1]
                else:
                    Door(i * 50, j * 50 + 25, 0)
                    result[i][j + 1] = [True, 0]
                    result[i][j] = [True, 0]
            elif pixels[i, j] == (195, 195, 195):
                result[i][j] = 3

    # возвращает массив с расположнием стен и дверей
    return result


const = 0
constx = 25
consty = 25


def translation_coordinates(x, y):
    '''переводит аюсолютную координату относительно расположения пикселя на карте'''
    return (x + player.real_posx - player.rect.centerx + constx,
            y + player.real_posy - player.rect.centery + consty)


def data_translation(pixelx, pixely, who):
    """для правильного считывания информации из массива"""

    if type(wall_layout[pixelx // 50][pixely // 50]) == list:
        if wall_layout[pixelx // 50][pixely // 50][1] == 1:
            if abs(pixely / 50 - int(pixely / 50) - 0.5) <= 0.2:
                return wall_layout[pixelx // 50][pixely // 50][0]
            else:
                return False
        else:
            if abs(pixelx / 50 - int(pixelx / 50) - 0.5) <= 0.2:
                return wall_layout[pixelx // 50][pixely // 50][0]
            else:
                return False
    elif wall_layout[pixelx // 50][pixely // 50] == 3:
        if who == 'entity':
            return True
        else:
            return False
    return wall_layout[pixelx // 50][pixely // 50]


def defining_intersection(coord, size_x, size_y, who):
    '''проверяет на принадлежность к стене или двери'''

    x_real, y_real = int(coord[0]), int(coord[1])
    if size_x == 1 and size_y == 1:
        return data_translation(x_real, y_real, who)
    else:
        return data_translation(x_real, y_real, who) or data_translation((x_real + size_x - 1), (y_real + size_y - 1), who) or \
               data_translation((x_real + size_x - 1), y_real, who) or data_translation(x_real, (y_real + size_y - 1), who) or \
               data_translation((x_real + size_x // 2), y_real, who) or data_translation(x_real, (y_real + size_y // 2), who) or \
               data_translation((x_real + size_x // 2), (y_real + size_y - 1), who) or \
               data_translation((x_real + size_x - 1), (y_real + size_y // 2), who)


# def draw_polygon_alpha(surface, color, points):
#     lx, ly = zip(*points)
#     min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
#     target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
#     shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
#     pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
#     surface.blit(shape_surf, target_rect)


def draw_flashlight(points, color):
    """отрисовывает фонаря"""

    # отрисовка видимости игрока
    surface1 = pygame.Surface(size)
    surface1.set_alpha(150)
    pygame.draw.polygon(surface1, color, points)
    pygame.draw.polygon(surface1, (255, 255, 255), points, width=2)
    screen.blit(surface1, (0, 0))

    # затемнение экрана
    # surface2 = pygame.Surface(size)
    # surface2.set_alpha(100)
    # screen.blit(surface2, (0, 0))


class Weapon:
    """Общий класс оружия"""

    def __init__(self, speed, damage, frequency, clip_size, ammo, reload_time,
                 who, queue=-1):
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
        self.reload_anim_frames = 0
        self.reload_anim_multiplier = 1
        self.attack_anim_frames = 3

    def is_reloading(self):
        return self.reload_progress != self.reload_time

    def spawn_bullet(self, damage, turn):
        turn = self.who.direction + random.randint(-self.spread_now,
                                                   self.spread_now)
        Bullet(self.who.rect.centerx - sin(
            radians(turn)) * 55, self.who.rect.centery - cos(
            radians(turn)) * 55,
               -sin(radians(turn)) * self.speed,
               -cos(radians(turn)) * self.speed, damage=damage)
        self.who.is_attacking = True

    def reload_update(self):
        self.reload_progress += 1
        if self.reload_progress == self.reload_time:
            prev_ammo = self.clip
            self.clip = min(self.clip_size, self.ammo + self.clip)
            self.ammo -= self.clip - prev_ammo

    def check_reload_start(self):
        if pygame.key.get_pressed()[
            pygame.K_r] and self.reload_progress == self.reload_time and self.clip != self.clip_size:
            self.reload_progress = 0
            self.who.is_reloading = True

    def update(self):
        if self.reload_progress < self.reload_time:
            self.reload_update()
        else:
            if self.clip > 0:
                if pygame.mouse.get_pressed()[0] and self.frequency_now <= 0:
                    self.spread_now = 1
                    self.queue_counter += 1
                    if self.queue_counter >= self.queue and self.queue >= 0:
                        self.spread_now += 1
                    if player.movement:
                        self.spread_now += 2
                    # print(self.spread_now)
                    # стрельба
                    turn = self.who.direction + random.randint(-self.spread_now,
                                                               self.spread_now)
                    # Bullet(self.who.rect.centerx - sin(radians(turn)) * 55,
                    #        self.who.rect.centery - cos(radians(turn)) * 55,
                    #        -sin(radians(turn)) * self.speed,
                    #        -cos(radians(turn)) * self.speed, damage=self.damage)
                    self.spawn_bullet(damage=self.damage,
                                      turn=self.who.direction)
                    self.frequency_now = self.frequency
                    self.clip -= 1
                    # перезарядка если пуль не осталось
                    if self.clip == 0 and self.ammo > 0:
                        self.reload_progress = 0
                        self.who.is_reloading = True
                self.frequency_now -= 1
                if self.frequency_now <= -2:
                    self.frequency_now = 0
                    self.queue_counter = 0
                # перезарядка по кнопке R
                self.check_reload_start()

    def draw_interface(self):
        """Отрисовка интерфейса оружия"""
        self.font = pygame.font.Font(None, 30)
        self.ammo_str = self.font.render(
            str(self.clip) + ' / ' + str(self.ammo), True, (255, 255, 255))
        screen.blit(self.ammo_str, (int(width * 0.79), int(height * 0.8)))
        pygame.draw.rect(screen, width=1,
                         rect=(int(width * 0.808), int(height * 0.85),
                               52, 12), color='grey')
        pygame.draw.rect(screen, width=0,
                         rect=(int(width * 0.808) + 1, int(height * 0.85) + 1,
                               int(50 * self.reload_progress / self.reload_time),
                               10),
                         color=(255, 255, 255))
        screen.blit(self.interface_image,
                    (int(width * 0.67), int(height * 0.785)))


class SniperRifle(Weapon):
    def __init__(self, whose):
        super().__init__(speed=100, damage=100, frequency=60,
                         clip_size=5, ammo=20, reload_time=3 * FPS, who=whose)
        self.interface_image = sniper_rifle_image


class Ak_47(Weapon):
    def __init__(self, whose):
        super().__init__(speed=60, damage=10, frequency=5,
                         clip_size=30, ammo=100, who=whose, reload_time=100,
                         queue=15)
        self.interface_image = ak_47_image
        self.reload_anim_frames = 20
        self.reload_anim_multiplier = 5


class Glock(Weapon):
    def __init__(self, whose):
        super().__init__(speed=50, damage=10, frequency=15, clip_size=17,
                         ammo=85, reload_time=45, who=whose)
        self.interface_image = glock_image
        self.reload_anim_frames = 15
        self.reload_anim_multiplier = 3


class Shotgun(Weapon):
    def __init__(self, whose):
        super().__init__(speed=40, damage=7, frequency=50, clip_size=8, ammo=40,
                         who=whose, reload_time=320)
        self.interface_image = shotgun_image
        self.reload_anim_frames = 20
        self.reload_anim_multiplier = 2

    def spawn_bullet(self, turn, damage):
        for _ in range(9):
            pellet_spread = random.randint(-9, 9)
            turn += pellet_spread
            ShotgunBullet(self.who.rect.centerx - sin(
                radians(turn)) * 55, self.who.rect.centery - cos(
                radians(turn)) * 55,
                          -sin(radians(turn)) * self.speed,
                          -cos(radians(turn)) * self.speed, damage=damage)
        self.who.is_attacking = True

    def reload_update(self):
        self.reload_progress += 1
        if self.reload_progress % (
                self.reload_time // self.clip_size) == 0 and self.reload_progress != self.reload_time:
            if self.ammo != 0:
                self.clip += 1
                self.ammo -= 1
                if self.ammo == 0:
                    self.reload_progress = self.reload_time
        if self.reload_progress == self.reload_time or self.clip == self.clip_size:
            self.reload_progress = self.reload_time
            prev_ammo = self.clip
            self.clip = min(self.clip_size, self.ammo + self.clip)
            self.ammo -= self.clip - prev_ammo

    def check_reload_start(self):
        if pygame.key.get_pressed()[
            pygame.K_r] and self.reload_progress == self.reload_time and self.clip != self.clip_size:
            self.reload_progress = self.clip * (
                    self.reload_time // self.clip_size)
            self.who.is_reloading = True


class Knife:
    def __init__(self, whose):
        self.damage = 20
        self.frequency = 1
        self.frequency_now = 0
        self.range_squared = 10000
        self.interface_image = knife_image
        self.attack_anim_frames = 15
        self.who = whose

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            min_dist = 1000000000000  # очень большая константа
            nearest_enemy = None  # ближайший враг
            for enemy in enemies:
                if (player.rect.centerx - enemy.rect.centerx) ** 2 + (
                        player.rect.centery - enemy.rect.centery) ** 2 < min_dist:
                    min_dist = (
                                       player.rect.centerx - enemy.rect.centerx) ** 2 + (
                                       player.rect.centery - enemy.rect.centery) ** 2
                    nearest_enemy = enemy
            if nearest_enemy is not None and (
                    player.rect.centerx - nearest_enemy.rect.centerx) ** 2 \
                    + (
                    player.rect.centerx - nearest_enemy.rect.centerx) ** 2 <= self.range_squared:
                nearest_enemy.take_damage(self.damage)
            self.who.is_attacking = True

    def draw_interface(self):
        """Отрисовка интерфейса оружия"""
        screen.blit(self.interface_image,
                    (int(width * 0.67), int(height * 0.785)))


class LootBox(pygame.sprite.Sprite):
    """Класс ящика с улучшениями"""

    def __init__(self, x, y):
        super().__init__(all_sprites, other_sprites, lootboxes)
        self.image = pygame.surface.Surface((50, 50))
        self.image.fill((192, 0, 192))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.timer = 0
        self.open_time = 60

    def update(self):
        pass

    def use(self):
        player.get_current_weapon().ammo += 50
        self.kill()

    def reset_timer(self):
        self.timer = 0

    def add_timer(self):
        self.timer += 1
        if self.timer == self.open_time:
            self.use()

    def draw_open_progress(self):
        if self.timer != 0:
            pygame.draw.rect(screen, width=1, rect=(
                self.rect.centerx - 25, self.rect.centery - 75, 52, 12),
                             color='red')
            pygame.draw.rect(screen, width=0,
                             rect=(
                                 self.rect.centerx - 26, self.rect.centery - 74,
                                 int(50 * self.timer / self.open_time), 10),
                             color='yellow')


class MedkitLootbox(LootBox):
    def __init__(self, x, y):
        super().__init__(x, y)

    def use(self):
        player.medkits += 1
        self.kill()


class Bullet(pygame.sprite.Sprite):
    """Класс пули"""

    def __init__(self, x, y, speed_x, speed_y, damage):
        super().__init__(all_sprites, bullets)
        self.image = pygame.surface.Surface((5, 5))
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
        self.float_x = self.rect.centerx + self.speedx / 50 + self.float_x - int(
            self.float_x)
        self.float_y = self.rect.centery + self.speedy / 50 + self.float_y - int(
            self.float_y)
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        for _ in range(49):
            self.float_x += self.speedx / 50
            self.float_y += self.speedy / 50
            self.rect.centerx = int(self.float_x)
            self.rect.centery = int(self.float_y)
            # pygame.sprite.spritecollide(self, walls, False)
            if defining_intersection(
                    translation_coordinates(self.rect.centerx - 5,
                                            self.rect.centery - 5), 10,
                    10, 'bullet') or pygame.sprite.spritecollide(self, characters,
                                                       False):
                self.kill()


class ShotgunBullet(Bullet):
    """Класс пули дробовика"""

    def __init__(self, x, y, speed_x, speed_y, damage):
        super().__init__(x, y, speed_x, speed_y, damage)
        self.image = pygame.Surface((3, 3))
        self.image.fill('white')
        self.timer = 0

    def update(self):
        super().update()
        self.timer += 1
        if self.timer > 8:
            self.kill()


class Entity(pygame.sprite.Sprite):
    """Общий класс сущности"""

    def __init__(self, x, y):
        super().__init__(all_sprites, characters)
        self.image = im1
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.real_posx = x
        self.real_posy = y

        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.direction = 0

        # атрибуты, отвечающие за анимации
        self.is_idle = True
        self.anim_idle_cnt = 0
        self.is_moving = False
        self.anim_move_cnt = 0
        self.prev_pos = self.rect.center

        self.is_reloading = False
        self.anim_reload_cnt = 0
        self.is_attacking = False
        self.anim_attack_cnt = 0

    def reset_reload_attack(self):
        self.is_reloading = False
        self.is_attacking = False
        self.anim_attack_cnt = 0
        self.anim_reload_cnt = 0

    def anim_reload_update(self):
        weapon = self.get_current_weapon()
        if type(weapon) == Knife or not weapon.is_reloading():
            self.is_reloading = False
            self.anim_reload_cnt = 0
        # if not weapon.is_reloading():
        #     self.is_reloading = False
        #     self.anim_reload_cnt = 0
        else:
            self.is_reloading = True
            self.anim_reload_cnt += 1
            if self.anim_reload_cnt == weapon.reload_anim_multiplier * weapon.reload_anim_frames:
                self.anim_reload_cnt = 0
                if type(weapon) != Shotgun or not weapon.is_reloading():
                    self.is_reloading = False

    def anim_attack_update(self):
        weapon = self.get_current_weapon()
        if not self.is_attacking:
            self.anim_attack_cnt = 0
        else:
            self.anim_attack_cnt += 1
            if self.anim_attack_cnt == 3 * weapon.attack_anim_frames:
                self.anim_attack_cnt = 0
                self.is_attacking = False

    def anim_is_idle_update(self):
        if self.rect.center != self.prev_pos:
            self.anim_idle_cnt = 0
            self.is_idle = False
            self.is_moving = True
        else:
            self.is_idle = True
            self.is_moving = False
            self.anim_idle_cnt = (self.anim_idle_cnt + 1) % 60

    def anim_is_moving_update(self):
        if self.rect.center == self.prev_pos:
            self.anim_move_cnt = 0
            self.is_moving = False
            self.is_idle = True
        else:
            self.is_moving = True
            self.is_idle = False
            self.anim_move_cnt = (self.anim_move_cnt + 1) % 60

    def all_anims_update(self):
        """Обновляет все счетчики анимаций"""
        self.anim_is_moving_update()
        self.anim_attack_update()
        self.anim_is_idle_update()
        self.anim_reload_update()

    def get_current_state(self):
        """Возвращает текущее состояние сущности:
        перезарядка - 0, атака - 1, движение - 2, безделье - 3
        (состояние с меньшим номером имеет больший приоритет)"""

        if self.is_reloading:
            self.is_attacking = False
            return 0
        elif self.is_attacking:
            self.is_reloading = False
            return 1
        elif self.is_moving:
            self.is_idle = False
            return 2
        elif self.is_idle:
            self.is_moving = False
            return 3

    def get_current_image_info(self):
        """Возвращает кортеж из трех значений: оружия, состояния и номера кадра"""
        state = self.get_current_state()
        weapon = self.get_current_weapon()
        if type(weapon) == Knife:
            weapontype = 'knife'
        elif type(weapon) == Ak_47:
            weapontype = 'rifle'
        elif type(weapon) == Shotgun:
            weapontype = 'shotgun'
        elif type(weapon) == Glock:
            weapontype = 'handgun'
        if state == 1:
            frame_num = self.anim_attack_cnt // 3
        elif state == 0:
            frame_num = self.anim_reload_cnt // weapon.reload_anim_multiplier
        elif state == 2:
            frame_num = self.anim_move_cnt // 3
        elif state == 3:
            frame_num = self.anim_idle_cnt // 3
        states = ['reload', 'shoot', 'move', 'idle']
        return weapontype, states[state], frame_num

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def move_entity(self, x, y):
        """Переместить сущность на координаты х, y"""
        self.prev_pos = self.rect.center  # для анимаций
        start_x, start_y = self.real_posx, self.real_posy
        self.real_posx = start_x + x
        self.real_posy = start_y + y
        x_move, y_move, xy_move = True, True, True
        if defining_intersection(
                (self.real_posx - 32 + constx, self.real_posy - 32 + consty),
                64, 64, 'entity'):
            xy_move = False
        self.real_posx = start_x + x
        self.real_posy = start_y
        if defining_intersection(
                (self.real_posx - 32 + constx, self.real_posy - 32 + consty),
                64, 64, 'entity'):
            x_move = False
        self.real_posx = start_x
        self.real_posy = start_y + y
        if defining_intersection(
                (self.real_posx - 32 + constx, self.real_posy - 32 + consty),
                64, 64, 'entity'):
            y_move = False
        if xy_move:
            self.movement = True
            self.rect.centerx += x
            self.rect.centery += y
            self.real_posx = start_x + x
            self.real_posy = start_y + y
        elif x_move:
            self.movement = True
            self.rect.centerx += x
            self.real_posx = start_x + x
            self.real_posy = start_y
        elif y_move:
            self.movement = True
            self.rect.centery += y
            self.real_posx = start_x
            self.real_posy = start_y + y
        else:
            self.movement = True
            self.real_posx = start_x
            self.real_posy = start_y
        if x == 0 and y == 0:
            self.movement = False
        if type(self) == Player:
            self.wall_hitbox.center = self.rect.center

    def draw_health_bar(self, health_color, health):
        pygame.draw.rect(screen, width=1, rect=(
            self.rect.centerx - 26, self.rect.centery - 50, 52, 12), color='black')
        pygame.draw.rect(screen, width=0,
                         rect=(self.rect.centerx - 25, self.rect.centery - 49,
                               int(50 * health / self.max_health), 10),
                         color=health_color)

    def determining_angle(self, x_pos, y_pos, x, y):
        """считает кгол между двумя пикселями"""

        # расчеты производятся относительно первого пикселя
        if y_pos != y or x_pos != x:
            turn = pi / 2 - asin(((y_pos - y) / (
                    (x_pos - x) ** 2 + (y_pos - y) ** 2) ** 0.5))
            if x_pos > x:
                turn = degrees(turn)
            else:
                turn = -degrees(turn)
        else:
            return 0
        return turn

    def beam(self, x_start, y_start, x_end=False, y_end=False, turn=0, long=500,
             nesting=1, accuracy=0):
        """рисует луч с учетом пересечений со стенами"""
        # вернет кортеж, где первый аргумент - смог ли луч добрать до конечной точки,
        # а второй - точку где он впервые пересек стену или дверь

        # выставляет значение точности
        if accuracy == 0:
            if nesting == 1:
                accuracy = 40
            else:
                accuracy = 15

        # подсчитывае скорость перемещения пикселя "проверки"
        if x_end and y_end:
            x_speed = (x_end - x_start) / accuracy
            y_speed = (y_end - y_start) / accuracy
        else:
            x_speed = -sin(radians(turn)) * long / accuracy
            y_speed = -cos(radians(turn)) * long / accuracy

        # находит первое пересение луча со стеной или дверью
        for i in range(0, accuracy + 1):
            x, y = int(x_start + x_speed * i), int(y_start + y_speed * i)
            if defining_intersection(translation_coordinates(x, y), 1, 1, 'beam'):
                if nesting == 1:
                    return (False, self.beam(x - x_speed, y - y_speed, x_end=x,
                                             y_end=y, nesting=2)[1])
                else:
                    return (False, (x, y))
        return (True, (x, y))


class Player(Entity):
    """Класс игрока"""

    def __init__(self, x, y):
        super().__init__(x, y)
        characters_rendering.add(self)
        self.weapon_list = [Shotgun(self), Ak_47(self), Knife(self)]
        self.current_weapon = 1
        self.medkits = 0
        self.range = 15000
        self.wall_hitbox = self.image.get_rect(center=self.rect.center, width=54, height=54)
        self.wall_hitbox.h = self.wall_hitbox.w = 54

        # self.wall_hitbox.move(1, 1)

    def get_current_weapon(self):
        """Возвращает текущее оружие игрока"""
        return self.weapon_list[self.current_weapon]

    def heal(self):
        """Использование игроком аптечки"""
        self.health = min(self.max_health,
                          self.health + int(self.max_health * 0.2))

    def draw_interface(self):
        """Отрисовка интерфейса игрока"""
        self.font = pygame.font.Font(None, 30)
        self.ammo_str = self.font.render(str(self.medkits), True,
                                         (255, 255, 255))
        screen.blit(self.ammo_str, (int(width * 0.88), int(height * 0.80)))
        self.get_current_weapon().draw_interface()

    def get_nearest_door(self):
        """Возвращает ближайшую к игроку дверь"""
        min_dist = 1000000000000  # очень большая константа
        nearest_door = None  # ближайшая дверь
        for door in doors:
            if (player.rect.centerx - door.rect.centerx) ** 2 + (
                    player.rect.centery - door.rect.centery) ** 2 < min_dist:
                min_dist = (
                                   player.rect.centerx - door.rect.centerx) ** 2 + (
                                   player.rect.centery - door.rect.centery) ** 2
                nearest_door = door
        return nearest_door

    def get_nearest_lootbox(self):
        """Возвращает ближайший к игроку ящик"""
        min_dist = 1000000000000  # очень большая константа
        nearest_lootbox = None  # ближайшая коробка
        for lootbox in lootboxes:
            if (player.rect.centerx - lootbox.rect.centerx) ** 2 + (
                    player.rect.centery - lootbox.rect.centery) ** 2 < min_dist:
                min_dist = (
                                   player.rect.centerx - lootbox.rect.centerx) ** 2 + (
                                   player.rect.centery - lootbox.rect.centery) ** 2
                nearest_lootbox = lootbox
        return nearest_lootbox

    def tracing(self):
        """происходит трассировка лучей для фонарика"""

        self.viewing_angle = 60  # угол обзора
        coord = [(width // 2,
                  height // 2)]  # массив координат многоугольника, для создания фонаря (видимости)
        turn = 1  # частота пускания лучей (угол между соседними лучами)

        # выполняется трассировка
        for i in range(int(self.viewing_angle / turn) + 1):
            coord.append(
                self.beam(width // 2, height // 2,
                          turn=self.direction - self.viewing_angle / 2 + i * turn,
                          long=500)[1])
        coord.append((width // 2, height // 2))

        draw_flashlight(coord, (255, 255, 173, 50))

    def visible_objects(self):
        for enemy in enemies:
            dist = (enemy.real_posx - self.real_posx) ** 2 + (
                    enemy.real_posy - self.real_posy) ** 2
            if dist <= 10000:
                enemy.distance_beam = [True, True]
                if not enemy in characters_rendering:
                    characters_rendering.add(enemy)
            elif dist <= 530 ** 2:
                if self.beam(self.rect.centerx, self.rect.centery,
                             x_end=enemy.rect.centerx, y_end=enemy.rect.centery,
                             accuracy=30, nesting=2)[0]:
                    enemy.distance_beam = [False, True]
                    if abs(self.direction - self.determining_angle(
                            self.rect.centerx, self.rect.centery,
                            enemy.rect.centerx,
                            enemy.rect.centery)) <= 34 or abs(
                        self.direction - self.determining_angle(
                            self.rect.centerx, self.rect.centery,
                            enemy.rect.centerx,
                            enemy.rect.centery)) >= 326:
                        if not enemy in characters_rendering:
                            characters_rendering.add(enemy)
                    else:
                        enemy.distance_beam = [False, False]
                        if enemy in characters_rendering:
                            characters_rendering.remove(enemy)
                else:
                    enemy.distance_beam = [False, False]
                    if enemy in characters_rendering:
                        characters_rendering.remove(enemy)
            else:
                enemy.distance_beam = [False, False]
                if enemy in characters_rendering:
                    characters_rendering.remove(enemy)

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
        self.direction = self.determining_angle(self.rect.centerx,
                                                self.rect.centery,
                                                pygame.mouse.get_pos()[0],
                                                pygame.mouse.get_pos()[1])
        # self.tracing()

        self.movement = False
        self.move_entity(xshift, yshift)
        self.wall_hitbox.x += xshift
        self.wall_hitbox.y += yshift
        # self.image = pygame.transform.rotate(im1, self.direction + 90)
        # self.rect = self.image.get_rect(center=self.rect.center)
        self.visible_objects()

        # проверка на смену оружия
        if keystate[pygame.K_1]:
            if self.current_weapon != 0 and (
                    type(
                        self.get_current_weapon()) == Knife or
                    self.get_current_weapon().reload_progress != self.get_current_weapon().reload_time):
                self.get_current_weapon().reload_progress = 0
            if self.current_weapon != 0:
                self.current_weapon = 0
                self.reset_reload_attack()
        elif keystate[pygame.K_2]:
            if self.current_weapon != 1 and (
                    type(
                        self.get_current_weapon()) == Knife or
                    self.get_current_weapon().reload_progress != self.get_current_weapon().reload_time):
                self.get_current_weapon().reload_progress = 0
            if self.current_weapon != 1:
                self.current_weapon = 1
                self.reset_reload_attack()
        elif keystate[pygame.K_3]:
            if self.current_weapon != 2 and self.get_current_weapon().reload_progress != self.get_current_weapon().reload_time:
                self.get_current_weapon().reload_progress = 0
            self.current_weapon = 2
            self.reset_reload_attack()

        # проверка на аптечку
        if keystate[pygame.K_4] and self.medkits != 0:
            self.medkits -= 1
            self.heal()

        if keystate[pygame.K_f]:
            nearest_door = self.get_nearest_door()
            nearest_lootbox = self.get_nearest_lootbox()
            door_dist_sq = (
                                   player.rect.centerx - nearest_door.rect.centerx) ** 2 + (
                                   player.rect.centery - nearest_door.rect.centery) ** 2 if nearest_door is not None else 1000000000
            lootbox_dist_sq = (
                                      player.rect.centerx - nearest_lootbox.rect.centerx) ** 2 + (
                                      player.rect.centery - nearest_lootbox.rect.centery) ** 2 if nearest_lootbox is not None else 1000000000
            min_dist = min(door_dist_sq, lootbox_dist_sq)
            if min_dist <= self.range:
                if min_dist == door_dist_sq:
                    if not nearest_door.is_open:  # дверь закрыта
                        nearest_door.use()
                    else:
                        if not pygame.Rect.colliderect(self.wall_hitbox,
                                                       nearest_door.rect):  # дверь открыта, но не пересекается с игроком
                            nearest_door.use()
                elif min_dist == lootbox_dist_sq:
                    nearest_lootbox.add_timer()

            for lootbox in lootboxes:
                if lootbox != nearest_lootbox:
                    lootbox.reset_timer()
                elif lootbox_dist_sq > self.range:
                    lootbox.reset_timer()
        else:
            for lootbox in lootboxes:
                lootbox.reset_timer()
        self.all_anims_update()
        current_image = player_anim.get_current_image(
            *self.get_current_image_info())
        self.image = pygame.transform.rotate(current_image, self.direction + 90)
        self.rect = self.image.get_rect(center=self.rect.center)


class Enemy(Entity):
    """Класс врага"""

    def __init__(self, trajectory, speed=2):
        super().__init__(trajectory[0][1], trajectory[0][2])
        enemies.add(self)
        self.trajectory = trajectory  # массив действий
        self.trajectory_pos = 0  # этап выполнения
        self.detection = False  # видит ли игрока
        self.real_posx = trajectory[0][1]
        self.real_posy = trajectory[0][2]
        self.speed = speed
        self.stop = 0
        self.direction = 0
        self.reset_target = 0
        self.distance_beam = [False,
                              False]  # первая означает персонаж находится "вплотную", вторая-луч не пересекат стен и расстояние "небольшое"

    # def is_visible(self):
    #     if (player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2 > 250000:
    #         return False
    #     elif (player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2 < 10000:
    #         return True
    #     elif self.beam(player.rect.x, player.rect.y, self.rect.x, self.rect.y)

    def detection_player(self):
        if self.distance_beam[0]:
            self.reset_target = 0
            self.condition = 'See'
        elif self.distance_beam[1]:
            self.reset_target += 1
            if abs(self.direction - self.determining_angle(self.rect.centerx, self.rect.centery, player.rect.centerx,
                                                           player.rect.centery)) <= 30 or abs(
                self.direction - self.determining_angle(self.rect.centerx, self.rect.centery, player.rect.centerx,
                                                        player.rect.centery)) >= 330:
                self.reset_target = 0
                self.condition = 'See'
        else:
            self.condition = 'Lost'
            self.reset_target += 1
        if self.reset_target > 300:
            self.condition = 'Action'

    def See(self):
        self.direction_player = self.determining_angle(self.rect.centerx, self.rect.centery, player.rect.centerx,
                                                       player.rect.centery)
        if abs(self.direction_player - self.direction) <= 8:
            self.direction = self.direction_player
            # функция стрельбы
        else:
            if 0 <= (self.direction - self.direction_player) <= 180 or (self.direction - self.direction_player) <= -180:
                self.direction -= 8
                if self.direction < -180:
                    self.direction += 360
            else:
                self.direction += 8
                if self.direction > 180:
                    self.direction -= 360
        self.image = pygame.transform.rotate(im1, self.direction + 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def Lost(self):
        if self.reset_target <= 50:
            self.direction += 1
        elif 50 < self.reset_target <= 150:
            self.direction -= 1
        elif 150 < self.reset_target <= 250:
            self.direction += 1
        else:
            self.direction -= 1
        self.image = pygame.transform.rotate(im1, self.direction + 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def run(self):
        pass

    def update(self):
        self.detection_player()
        if self.condition == 'See':
            self.See()
        elif self.condition == 'Lost':
            self.Lost()
        else:
            if len(self.trajectory) != 1 and self.stop == 0:
                if (int(self.real_posx) - self.trajectory[self.trajectory_pos + 1][1]) ** 2 + (
                        int(self.real_posy) - self.trajectory[self.trajectory_pos + 1][2]) ** 2 >= self.speed ** 2:
                    self.direction = self.determining_angle(int(self.real_posx), int(self.real_posy),
                                                            self.trajectory[self.trajectory_pos + 1][1],
                                                            self.trajectory[self.trajectory_pos + 1][2])
                    self.image = pygame.transform.rotate(im1, self.direction + 90)
                    self.move_entity(int(-sin(radians(self.direction)) * self.speed),
                                     int(-cos(radians(self.direction)) * self.speed))
                    # self.real_posx -= sin(radians(self.direction)) * self.speed
                    # self.real_posy -= cos(radians(self.direction)) * self.speed
                else:
                    self.move_entity(int(-sin(radians(self.direction)) * (
                            (int(self.real_posx) - self.trajectory[self.trajectory_pos + 1][1]) ** 2 + (
                            int(self.real_posy) - self.trajectory[self.trajectory_pos + 1][2]) ** 2) ** 0.5),
                                     int(-cos(radians(self.direction)) * ((int(self.real_posx) -
                                                                           self.trajectory[self.trajectory_pos + 1][
                                                                               1]) ** 2 + (
                                                                                  int(self.real_posy) -
                                                                                  self.trajectory[
                                                                                      self.trajectory_pos + 1][
                                                                                      2]) ** 2) ** 0.5))
                    self.real_posx, self.real_posy = self.trajectory[self.trajectory_pos + 1][1:3]
                    self.trajectory_pos += 1
                    self.trajectory_pos %= len(self.trajectory) - 1
                    if self.trajectory[self.trajectory_pos + 1][0] == 'stop':
                        self.stop = self.trajectory[self.trajectory_pos + 1][1]
            elif self.stop != 0:
                self.direction += 2
                self.image = pygame.transform.rotate(im1, self.direction)
                self.stop -= 1
                if self.stop == 0:
                    self.trajectory_pos += 1
                    self.trajectory_pos %= len(self.trajectory) - 1
            self.rect = self.image.get_rect(center=self.rect.center)


class Wall(pygame.sprite.Sprite):
    """Класс стены"""

    def __init__(self, x, y):
        super().__init__(all_sprites, walls, walls_rendering)
        self.image = pygame.surface.Surface((50, 50))
        self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        # self.rendering = True
        # self.being_walls = True

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pass
        # if self.rendering:
        #     walls_rendering.add(self)
        #     self.being_walls = True
        # elif not self.rendering:
        #     walls_rendering.remove(self)
        #     self.being_walls = False


class Door(pygame.sprite.Sprite):
    """Класс двери"""

    def __init__(self, x, y, direction):
        super().__init__(all_sprites, doors, doors_wall, walls)
        self.direction = direction
        if direction == 0:
            self.image = door_textures[(1, 'vert')]
        elif direction == 1:
            self.image = door_textures[(1, 'hor')]
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        # self.rect = self.image.get_rect()
        # self.rect.center = (x, y)
        self.constx = x
        self.consty = y
        # self.image.fill((128, 0, 0))
        self.is_open = False
        self.max_delay = FPS
        self.delay = 0

    def use(self):
        if self.delay == 0:
            if self.is_open:
                if self.direction == 1:
                    wall_layout[(self.constx - 25) // 50][self.consty // 50][0] = True
                    wall_layout[(self.constx + 25) // 50][self.consty // 50][0] = True
                else:
                    wall_layout[self.constx // 50][(self.consty - 25) // 50][0] = True
                    wall_layout[self.constx // 50][(self.consty + 25) // 50][0] = True
                self.is_open = False
                walls.add(self)
                doors_wall.add(self)
            else:
                if self.direction == 1:
                    wall_layout[(self.constx - 25) // 50][self.consty // 50][0] = False
                    wall_layout[(self.constx + 25) // 50][self.consty // 50][0] = False
                else:
                    wall_layout[self.constx // 50][(self.consty - 25) // 50][0] = False
                    wall_layout[self.constx // 50][(self.consty + 25) // 50][0] = False
                self.is_open = True
                walls.remove(self)
                doors_wall.remove(self)
            self.delay = self.max_delay
            self.change_image()


    def change_image(self):
        # if self.is_open:
        #     self.image.fill((0, 128, 0))
        # else:
        #     self.image.fill((128, 0, 0))
        self.image = self.get_current_image()

    def update(self):
        if self.delay != 0:
            self.delay -= 1
            self.change_image()

    def get_current_image(self):
        """Возвращает текущую текстуру двери"""
        orientation = 'hor' if self.direction == 1 else 'vert'
        if self.delay == 0:
            if self.is_open:
                frame = 6
            else:
                frame = 1
        elif self.delay == self.max_delay:
            if self.is_open:
                frame = 1
            else:
                frame = 6
        else:
            if self.is_open:
                frame = (self.max_delay - self.delay + 10) // (FPS // 6)
            else:
                frame = (self.delay + 10) // (FPS // 6)
        return door_textures[(frame, orientation)]



class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if type(obj) == Player:
            obj.wall_hitbox.x += self.dx
            obj.wall_hitbox.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class PlayerAnimation:
    def __init__(self):
        self.animations = \
            {'handgun': {
                'idle': [],
                'move': [],
                'reload': [],
                'shoot': []},
                'knife': {
                    'idle': [],
                    'shoot': [],
                    'move': []},
                'rifle': {
                    'idle': [],
                    'move': [],
                    'reload': [],
                    'shoot': []},
                'shotgun': {
                    'idle': [],
                    'move': [],
                    'reload': [],
                    'shoot': []}}
        for cdir, dirs, files in os.walk('assets/player_sprites'):
            for file in files:
                a1, a2 = cdir.split('\\')[1:]
                self.animations[a1][a2].append(
                    pygame.image.load(f'{cdir}\\{file}'))
        # print(self.animations)

    def get_current_image(self, weapon, state, frame_num):
        return self.animations[weapon][state][frame_num]


# class Tile(pygame.sprite.Sprite):
#     def __init__(self, x, y):
#         super().__init__(all_sprites, tiles)
#         self.image = tile1
#         self.rect = self.image.get_rect()
#         self.rect.center = x, y


# class Furniture(pygame.sprite.Sprite):
#     def __init__(self, x, y, type):
#         super().__init__(all_sprites, furniture, walls)
#         self.image = table8
#         self.rect = self.image.get_rect()
#         self.rect.topleft = x, y


class MapTexture(pygame.sprite.Sprite):
    """Текстуры карты"""

    def __init__(self):
        super().__init__(all_sprites, map_texture)
        self.image = map_image
        self.rect = self.image.get_rect()
        self.rect.topleft = -25, -25


if __name__ == '__main__':

    FPS = 60
    pygame.init()
    size = width, height = 1400, 700
    screen = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)  # False на релизе

    walls = pygame.sprite.Group()  # стены
    walls_rendering = pygame.sprite.Group()
    characters = pygame.sprite.Group()  # персонажи
    other_sprites = pygame.sprite.Group()  # все остальное
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    lootboxes = pygame.sprite.Group()  # ящики
    enemies = pygame.sprite.Group()
    characters_rendering = pygame.sprite.Group()
    doors = pygame.sprite.Group()
    wall_boundaries = pygame.sprite.Group()
    doors_wall = pygame.sprite.Group()

    tiles = pygame.sprite.Group()
    furniture = pygame.sprite.Group()
    map_texture = pygame.sprite.Group()

    sniper_rifle_image = pygame.image.load('assets/sniper_rifle2.png').convert()
    sniper_rifle_image.set_colorkey((255, 255, 255))
    ak_47_image = pygame.image.load('assets/ak_47_image2.png').convert()
    ak_47_image.set_colorkey((255, 255, 255))
    glock_image = pygame.image.load('assets/glock_image.png').convert()
    glock_image.set_colorkey((255, 255, 255))
    im1 = pygame.image.load('assets/Игрок_2.png').convert()
    im1.set_colorkey((255, 255, 255))
    knife_image = pygame.image.load('assets/knife_image.png').convert()
    knife_image.set_colorkey((255, 255, 255))
    shotgun_image = pygame.image.load('assets/shotgun_image.png').convert()
    shotgun_image.set_colorkey((255, 255, 255))

    im1 = pygame.image.load('1.png').convert()
    im1.set_colorkey((0, 0, 0))

    map_image = pygame.image.load('assets/map_100_texture.png')

    door_textures = {}
    for i in range(1, 7):
        for j in {'vert', 'hor'}:
            door_textures[(i, j)] = pygame.image.load(f'assets/door_textures/frame{i}_{j}.png')

    player_anim = PlayerAnimation()
    running = True
    MedkitLootbox(500, 500)
    MedkitLootbox(500, 700)
    camera = Camera()
    # enemy1 = Enemy([['go', 3800, 1500], ['go', 4400, 4150], ['go', 250, 100],
    #                 ['go', 500, 100],
    #                 ['stop', 100], ['go', 100, 100]])

    player = Player(550, 1400)  # 550, 550  # 4500, 4250  # 3800,1500
    MapTexture()
    wall_layout = pic_to_map(
        'assets/map100.png')  # массив из пикселей картинки, где находится стена
    while running:
        # tr.fill((0,0,0,0))
        # внутри игрового цикла ещё один цикл
        # приёма и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            # РЕАКЦИЯ НА ОСТАЛЬНЫЕ СОБЫТИЯ
        # отрисовка и изменение свойств объектов
        # characters.update()
        player.get_current_weapon().update()
        player.rect = player.image.get_rect(size=(64, 64),
                                            center=player.rect.center)
        player.update()
        for i in characters:
            if i != player:
                i.update()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill('black')
        map_texture.draw(screen)
        # tiles.draw(screen)  # exp

        furniture.draw(screen)
        player.tracing()
        other_sprites.draw(screen)
        # walls.draw(screen)
        # wallllll.rendering = True
        # for i in walls:
        #     i.update()
        # walls_rendering.draw(screen)

        characters_rendering.draw(screen)
        other_sprites.draw(screen)
        doors.draw(screen)
        # затемнение экрана
        # surface2 = pygame.Surface(size)
        # surface2.set_alpha(140)
        # screen.blit(surface2, (0, 0))

        doors.update()
        for i in characters:
            i.rect = i.image.get_rect(size=(64, 64), center=i.rect.center)
        bullets.update()
        bullets.draw(screen)
        # player.draw_health_bar('green', player.health)
        for lootbox in lootboxes:
            lootbox.draw_open_progress()
        # enemy1.beam(enemy1.rect.centerx, enemy1.rect.centery,
        #             player.rect.centerx,
        #             player.rect.centery)
        # player.tracing()
        # pygame.draw.rect(screen, 'red', player.rect, width=1)
        # pygame.draw.rect(screen, 'green', player.wall_hitbox, width=1)
        screen.blit(
            pygame.font.Font(None, 40).render(str(int(clock.get_fps())), True,
                                              'red'), (100, 100))

        # anim debug
        screen.blit(
            pygame.font.Font(None, 40).render(str(player.get_current_state()),
                                              True,
                                              'red'), (100, 200))
        screen.blit(pygame.font.Font(None, 40).render(
            f'i{player.anim_idle_cnt}/r{player.anim_reload_cnt}/a{player.anim_attack_cnt}/m{player.anim_move_cnt}',
            True,
            'red'), (100, 300))

        player.draw_interface()
        clock.tick(FPS)
        # screen.blit(tmp_image, (player.rect.x, player.rect.y))
        pygame.display.flip()
    pygame.quit()
