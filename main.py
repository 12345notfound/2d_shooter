import pygame
import random
from math import sin, radians, cos, asin, pi, degrees

from PIL import Image


def pic_to_map(filename):
    im = Image.open(filename)
    pixels = im.load()
    x, y = im.size
    result = [[False for _ in range(y)] for _ in range(x)]
    for i in range(x):
        for j in range(y):
            if pixels[i, j] == (237, 28, 36, 255):  # 237,28,36 / 0,0,0
                Wall(i * 100, j * 100)
                result[i][j] = True
            elif pixels[i, j] == (34, 177, 76, 255):
                Door(i * 100, j * 100, 0)
                result[i][j] = [True, 0]
            elif pixels[i, j] == (136, 177, 77, 255):
                Door(i * 100, j * 100, 1)
                result[i][j] = [True, 1]
    return result


def translation_coordinates(x, y):
    '''переводит координату относительно расположения пикселя на карте'''
    return (x + player.real_posx - player.rect.centerx + 37, y + player.real_posy - player.rect.centery + 37)


def data_translation(pixelx, pixely):
    if type(wall_layout[pixelx // 100][pixely // 100]) == list:
        if wall_layout[pixelx // 100][pixely // 100][1] == 1:
            if abs(pixely / 100 - int(pixely / 100) - 0.5) <= 0.1:
                return wall_layout[pixelx // 100][pixely // 100][0]
            else:
                return False
        else:
            if abs(pixelx / 100 - int(pixelx / 100) - 0.5) <= 0.1:
                return wall_layout[pixelx // 100][pixely // 100][0]
            else:
                return False
    return wall_layout[pixelx // 100][pixely // 100]


def defining_intersection(coord, size_x, size_y):
    '''проверяет на принадлежность к стене'''
    # try:
    x_real, y_real = coord[0], coord[1]
    # print(x_real, y_real)
    if size_x == 1 and size_y == 1:
        # if type(wall_layout[x_real // 100][y_real // 100])==list:
        #     return wall_layout[x_real // 100][y_real // 100][0]
        # return wall_layout[x_real // 100][y_real // 100]ц
        return data_translation(x_real, y_real)
    else:
        # return wall_layout[x_real // 100][y_real // 100] or wall_layout[(x_real + size_x - 1) // 100][
        #     (y_real + size_y - 1) // 100] or \
        #        wall_layout[(x_real + size_x - 1) // 100][y_real // 100] or wall_layout[x_real // 100][
        #            (y_real + size_y - 1) // 100]
        return data_translation(x_real, y_real) or data_translation((x_real + size_x - 1),
                                                                    (y_real + size_y - 1)) or \
               data_translation((x_real + size_x - 1), y_real) or data_translation(x_real,
                                                                                   (y_real + size_y - 1))
    # except IndexError:
    #     return True1

def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)

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
                    # print(self.spread_now)
                    # стрельба
                    turn = self.who.direction + random.randint(-self.spread_now, self.spread_now)
                    Bullet(self.who.rect.centerx - sin(radians(turn)) * 55,
                           self.who.rect.centery - cos(radians(turn)) * 55,
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
        self.ammo_str = self.font.render(str(self.clip) + ' / ' + str(self.ammo), True, (255, 255, 255))
        screen.blit(self.ammo_str, (int(width * 0.79), int(height * 0.8)))
        pygame.draw.rect(screen, width=1, rect=(int(width * 0.808), int(height * 0.85),
                                                52, 12), color='grey')
        pygame.draw.rect(screen, width=0, rect=(int(width * 0.808) + 1, int(height * 0.85) + 1,
                                                int(50 * self.reload_progress / self.reload_time), 10),
                         color=(255, 255, 255))
        screen.blit(self.interface_image, (int(width * 0.67), int(height * 0.785)))


class SniperRifle(Weapon):
    def __init__(self, whose):
        super().__init__(speed=100, damage=100, frequency=60,
                         clip_size=5, ammo=20, reload_time=3 * FPS, who=whose)
        self.interface_image = sniper_rifle_image


class Ak_47(Weapon):
    def __init__(self, whose):
        super().__init__(speed=50, damage=10, frequency=5,
                         clip_size=1000, ammo=100, who=whose, reload_time=3 * FPS, queue=15)
        self.interface_image = ak_47_image


class Knife:
    def __init__(self, whose):
        self.damage = 20
        self.frequency = 1
        self.frequency_now = 0
        self.range_squared = 4900
        self.interface_image = knife_image

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            min_dist = 1000000000000  # очень большая константа
            nearest_enemy = None  # ближайший враг
            for enemy in enemies:
                if (player.rect.centerx - enemy.rect.centerx) ** 2 + (
                        player.rect.centery - enemy.rect.centery) ** 2 < min_dist:
                    min_dist = (player.rect.centerx - enemy.rect.centerx) ** 2 + (
                            player.rect.centery - enemy.rect.centery) ** 2
                    nearest_enemy = enemy
            if nearest_enemy is not None and (player.rect.centerx - nearest_enemy.rect.centerx) ** 2 \
                    + (player.rect.centerx - nearest_enemy.rect.centerx) ** 2 <= self.range_squared:
                nearest_enemy.take_damage(self.damage)

    def draw_interface(self):
        """Отрисовка интерфейса оружия"""
        screen.blit(self.interface_image, (int(width * 0.67), int(height * 0.785)))


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
                self.rect.centerx - 25, self.rect.centery - 75, 52, 12), color='red')
            pygame.draw.rect(screen, width=0,
                             rect=(self.rect.centerx - 26, self.rect.centery - 74,
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
        self.float_x = self.rect.centerx + self.speedx / 50 + self.float_x - int(self.float_x)
        self.float_y = self.rect.centery + self.speedy / 50 + self.float_y - int(self.float_y)
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        for _ in range(49):
            self.float_x += self.speedx / 50
            self.float_y += self.speedy / 50
            self.rect.centerx = int(self.float_x)
            self.rect.centery = int(self.float_y)
            # pygame.sprite.spritecollide(self, walls, False)
            if defining_intersection(translation_coordinates(self.rect.centerx - 5, self.rect.centery - 5), 10,
                                     10) or pygame.sprite.spritecollide(self, characters,
                                                                        False):
                self.kill()


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, characters)
        self.image = im1
        # self.image.fill('red')
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.real_posx = x
        self.real_posy = y
        # self.mask = pygame.mask.from_surface(self.image)

        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.direction = 0

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def move_entity(self, x, y):
        """Переместить сущность на координаты х, y"""
        # start_x, start_y = self.rect.centerx, self.rect.centery
        start_x, start_y = self.real_posx, self.real_posy
        self.rect = self.image.get_rect(size=(64, 64), center=self.rect.center)
        # self.rect.centerx = start_x + x
        # self.rect.centery = start_y + y
        self.real_posx = start_x + x
        self.real_posy = start_y + y
        x_move, y_move, xy_move = True, True, True
        xshift = 0
        yshift = 0
        # for wall in walls:
        #     if pygame.sprite.collide_rect(self, wall):
        if defining_intersection((self.real_posx - 32 + 37, self.real_posy - 32 + 37), 64, 64):
            xy_move = False
            # breaks
        # self.rect.centerx = start_x + x
        # self.rect.centery = start_y
        self.real_posx = start_x + x
        self.real_posy = start_y
        # for wall in walls:
        #     if pygame.sprite.collide_rect(self, wall):
        if defining_intersection((self.real_posx - 32 + 37, self.real_posy - 32 + 37), 64, 64):
            x_move = False

            # break
        # self.rect.centerx = start_x
        # self.rect.centery = start_y + y
        self.real_posx = start_x
        self.real_posy = start_y + y
        # for wall in walls:
        #     if pygame.sprite.collide_rect(self, wall):
        if defining_intersection((self.real_posx - 32 + 37, self.real_posy - 32 + 37), 64, 64):
            y_move = False
            # break
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
        pygame.draw.rect(screen, width=1, rect=(self.rect.centerx - 26, self.rect.centery - 50, 52, 12), color='black')
        pygame.draw.rect(screen, width=0,
                         rect=(self.rect.centerx - 25, self.rect.centery - 49, int(50 * health / self.max_health), 10),
                         color=health_color)

    def determining_angle(self, x_pos, y_pos, x, y):
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

    def beam(self, x_start, y_start, x_end=False, y_end=False, turn=0, long=500, nesting=1):
        '''рисует луч'''
        accuracy = 40  # точность
        if x_end and y_end:
            x_speed = (x_end - x_start) / accuracy
            y_speed = (y_end - y_start) / accuracy
        else:
            x_speed = -sin(radians(turn)) * long / accuracy
            y_speed = -cos(radians(turn)) * long / accuracy
        dist = accuracy
        for i in range(0, accuracy + 1):
            x, y = int(x_start + x_speed * i), int(y_start + y_speed * i)
            if defining_intersection(translation_coordinates(x, y), 1,
                                     1):
                dist = i
                if nesting==1:
                    return (False, self.beam(x-x_speed, y-y_speed,x_end=x,y_end=y,nesting=2)[1])
                else:
                    return (False, (x, y))
        # pygame.draw.line(screen, pygame.Color('red'), (x_start, y_start),
        #                  (x, y))
        # if dist == accuracy:
        #     return (True, (x, y))
        return (True, (x, y))


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.weapon_list = [SniperRifle(self), Ak_47(self), Knife(self)]
        self.current_weapon = 1
        self.medkits = 0
        self.range = 15000
        self.wall_hitbox = self.rect
        self.wall_hitbox.h = self.wall_hitbox.w = 54
        # self.wall_hitbox.move(1, 1)

    def get_current_weapon(self):
        """Возвращает текущее оружие игрока"""
        return self.weapon_list[self.current_weapon]

    def heal(self):
        """Использование игроком аптечки"""
        self.health = min(self.max_health, self.health + int(self.max_health * 0.2))

    def draw_interface(self):
        """Отрисовка интерфейса игрока"""
        self.font = pygame.font.Font(None, 30)
        self.ammo_str = self.font.render(str(self.medkits), True, (255, 255, 255))
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
        self.viewing_angle = 50
        coord = [(700,350)]
        #coord_end = self.beam(700, 350, turn=self.direction - self.viewing_angle / 2, long=500)[1]
        for i in range(self.viewing_angle):
            coord.append(  self.beam(700, 350, turn=self.direction - self.viewing_angle / 2 + i, long=500)[1])
            #draw_polygon_alpha(screen, (252,251,177,100),(coord_end,coord_now,(700,350)))
            #pygame.draw.polygon(screen, (252,251,177,100), (coord_end,coord_now,(700,350)))
            #coord_end=coord_now
        coord.append((700,350))
        draw_polygon_alpha(screen, (252, 251, 177, 51), coord)

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
        self.direction = self.determining_angle(self.rect.centerx, self.rect.centery, pygame.mouse.get_pos()[0],
                                                pygame.mouse.get_pos()[1])
        # self.tracing()

        self.movement = False
        self.move_entity(xshift, yshift)
        self.wall_hitbox.x += xshift
        self.wall_hitbox.y += yshift
        self.image = pygame.transform.rotate(im1, self.direction)
        self.rect = self.image.get_rect(center=self.rect.center)
        # проверка, есть ли рядом ящики
        # for lootbox in lootboxes:
        #     if pygame.sprite.collide_rect(self, lootbox) and keystate[pygame.K_f]:
        #         lootbox.add_timer()
        #     else:
        #         lootbox.reset_timer()

        # проверка на смену оружия
        if keystate[pygame.K_1]:
            if self.current_weapon != 0 and (
                    type(
                        self.get_current_weapon()) == Knife or self.get_current_weapon().reload_progress != self.get_current_weapon().reload_time):
                self.get_current_weapon().reload_progress = 0
            self.current_weapon = 0
        elif keystate[pygame.K_2]:
            if self.current_weapon != 1 and (
                    type(
                        self.get_current_weapon()) == Knife or self.get_current_weapon().reload_progress != self.get_current_weapon().reload_time):
                self.get_current_weapon().reload_progress = 0
            self.current_weapon = 1
        elif keystate[pygame.K_3]:
            if self.current_weapon != 2 and self.get_current_weapon().reload_progress != self.get_current_weapon().reload_time:
                self.get_current_weapon().reload_progress = 0
            self.current_weapon = 2

        # проверка на аптечку
        if keystate[pygame.K_4] and self.medkits != 0:
            self.medkits -= 1
            self.heal()

        if keystate[pygame.K_f]:
            nearest_door = self.get_nearest_door()
            nearest_lootbox = self.get_nearest_lootbox()
            door_dist_sq = (player.rect.centerx - nearest_door.rect.centerx) ** 2 + (
                    player.rect.centery - nearest_door.rect.centery) ** 2 if nearest_door is not None else 1000000000
            lootbox_dist_sq = (player.rect.centerx - nearest_lootbox.rect.centerx) ** 2 + (
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


class Enemy(Entity):
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

    def detection_player(self):
        if abs(self.direction - self.determining_angle(self.rect.centerx, self.rect.centery, player.rect.centerx,
                                                       player.rect.centery)) <= 30 or abs(
            self.direction - self.determining_angle(self.rect.centerx, self.rect.centery, player.rect.centerx,
                                                    player.rect.centery)) >= 330:
            if (self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2 <= 90000:
                if self.beam(self.rect.centerx, self.rect.centery, x_end=player.rect.centerx,
                             y_end=player.rect.centery)[0]:
                    self.reset_target = 0
                    self.detection = True
        if self.detection:
            self.reset_target += 1
        if self.reset_target >= 300:
            self.detection = False

    def update(self):
        self.detection_player()
        if self.detection:
            self.direction = self.determining_angle(self.rect.centerx, self.rect.centery, player.rect.centerx,
                                                    player.rect.centery)
            # self.move_entity(xshift, yshift)
            self.image = pygame.transform.rotate(im1, self.direction)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            if len(self.trajectory) != 1 and self.stop == 0:
                if (int(self.real_posx) - self.trajectory[self.trajectory_pos + 1][1]) ** 2 + (
                        int(self.real_posy) - self.trajectory[self.trajectory_pos + 1][2]) ** 2 >= self.speed ** 2:
                    self.direction = self.determining_angle(int(self.real_posx), int(self.real_posy),
                                                            self.trajectory[self.trajectory_pos + 1][1],
                                                            self.trajectory[self.trajectory_pos + 1][2])
                    self.image = pygame.transform.rotate(im1, self.direction)
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
    def __init__(self, x, y):
        super().__init__(all_sprites, walls)
        self.image = pygame.surface.Surface((100, 100))
        self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pass


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__(all_sprites, doors, doors_wall, walls)
        if direction == 0:
            self.image = pygame.Surface((20, 100))
        elif direction == 1:
            self.image = pygame.Surface((100, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.constx = x
        self.consty = y
        self.image.fill((128, 0, 0))
        self.is_open = False
        self.max_delay = FPS
        self.delay = self.max_delay

    def use(self):
        if self.delay == 0:
            if self.is_open:
                wall_layout[self.constx // 100][self.consty // 100][0] = True
                self.is_open = False
                walls.add(self)
                doors_wall.add(self)
            else:
                wall_layout[self.constx // 100][self.consty // 100][0] = False
                self.is_open = True
                walls.remove(self)
                doors_wall.remove(self)
            self.change_image()
            self.delay = self.max_delay

    def change_image(self):
        if self.is_open:
            self.image.fill((0, 128, 0))
        else:
            self.image.fill((128, 0, 0))

    def update(self):
        if self.delay != 0:
            self.delay -= 1


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


if __name__ == '__main__':

    FPS = 60
    pygame.init()
    size = width, height = 1400, 700
    screen = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)  # False на релизе

    walls = pygame.sprite.Group()  # стены
    characters = pygame.sprite.Group()  # персонажи
    other_sprites = pygame.sprite.Group()  # все остальное
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    lootboxes = pygame.sprite.Group()  # ящики
    enemies = pygame.sprite.Group()
    doors = pygame.sprite.Group()
    wall_boundaries = pygame.sprite.Group()
    doors_wall = pygame.sprite.Group()

    sniper_rifle_image = pygame.image.load('sniper_rifle2.png').convert()
    sniper_rifle_image.set_colorkey((255, 255, 255))
    ak_47_image = pygame.image.load('ak_47_image2.png').convert()
    ak_47_image.set_colorkey((255, 255, 255))
    im1 = pygame.image.load('Игрок_2.png').convert()
    im1.set_colorkey((255, 255, 255))
    knife_image = pygame.image.load('knife_image.png').convert()
    knife_image.set_colorkey((255, 255, 255))

    running = True
    Bullet(10, 10, 1.4, 3.8, damage=10)
    # LootBox(200, 200)
    MedkitLootbox(500, 500)
    MedkitLootbox(500, 700)
    Door(400, 200, 0)
    camera = Camera()
    enemy1 = Enemy([['go', 4500, 4200], ['go', 4400, 4150], ['go', 250, 100], ['go', 500, 100],
                    ['stop', 100], ['go', 100, 100]])

    player = Player(4500, 4200)  # 550, 550

    wall_layout = pic_to_map('map50.png')  # массив из пикселей картинки, где находится стена
    # for wall in walls:
    #     print(wall.rect.center)
    # tr = pygame.Surface((1400, 750))
    while running:
        #tr.fill((0,0,0,0))
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
        player.rect = player.image.get_rect(size=(64, 64), center=player.rect.center)
        player.update()
        for i in characters:
            if i != player:
                i.update()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill('black')
        other_sprites.draw(screen)
        walls.draw(screen)
        characters.draw(screen)
        other_sprites.draw(screen)
        walls.draw(screen)
        doors.draw(screen)
        doors.update()
        for i in characters:
            i.rect = i.image.get_rect(size=(64, 64), center=i.rect.center)
        # print(player.real_posx, player.real_posy)
        bullets.update()
        # print(clock.get_fps())
        bullets.draw(screen)
        player.draw_health_bar('green', player.health)
        for lootbox in lootboxes:
            lootbox.draw_open_progress()
        enemy1.beam(enemy1.rect.centerx, enemy1.rect.centery, player.rect.centerx,
                    player.rect.centery)
        player.tracing()
        pygame.draw.rect(screen, 'red', player.rect, width=1)
        pygame.draw.rect(screen, 'green', player.wall_hitbox, width=1)
        # print(player.wall_hitbox.center, '/', player.rect.center)
        # print(player.rect.size, player.wall_hitbox.size)
        screen.blit(pygame.font.Font(None, 40).render(str(int(clock.get_fps())), True, 'red'), (100, 100))
        player.draw_interface()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
