import pygame
import sqlite3
from interface import Button_rect

location_objects = {'1': (345, 143), 'замок': (402, 173), 'надписаь': (358, 194), 'звезда': (374, 276)}


def reading(name):
    """считывает нужные данные из БД"""
    con = sqlite3.connect("Базы данных/Данные аккаунтов.db")

    cur = con.cursor()

    result = cur.execute(f"""SELECT * FROM Data
                WHERE name = '{name}'""").fetchall()
    con.close()
    return result[0][3], result[0][4:]


def separation():
    """отрисовывает главное меню игры"""
    screen.blit(
        pygame.font.Font(None, 70).render(str(money), True,
                                          'black'), (780, 24))
    screen.blit(
        pygame.font.Font(None, 50).render(name, True,
                                          'black'), (30, 30))
    screen.blit(
        pygame.font.Font(None, 40).render(f'{sum(lvl)}/9 звезд', True,
                                          'black'), (30, 70))
    for i in range(1, 7):
        if i == 1:
            button.append(Button_rect(screen, location_objects['1'][0], location_objects['1'][1], 200, 187, lambda:
            print(i)))
            screen.blit(lvl_text[0], (0, 0, 1400, 700))
            for j in range(lvl[i - 1]):
                screen.blit(star, (
                    location_objects['звезда'][0] + j * 53 + (i - 1) // 2 * 233,
                    location_objects['звезда'][1] + 213 * ((i - 1) % 2), 1400, 700))

        elif i <= 3:
            if lvl[i - 2] != 0:
                button.append(Button_rect(screen, location_objects['1'][0] + (i - 1) // 2 * 233,
                                          location_objects['1'][1] + 213 * ((i - 1) % 2), 200, 187, lambda:
                                          print(i)))
                screen.blit(lvl_text[i - 1], (0, 0, 100, 100))
                for j in range(lvl[i - 1]):
                    screen.blit(star, (
                        location_objects['звезда'][0] + j * 53 + (i - 1) // 2 * 233,
                        location_objects['звезда'][1] + 213 * ((i - 1) % 2), 1400, 700))
            else:
                screen.blit(lock, (
                    location_objects['замок'][0] + (i - 1) // 2 * 233,
                    location_objects['замок'][1] + 213 * ((i - 1) % 2), 130,
                    130))
        else:
            screen.blit(lock, (
                location_objects['замок'][0] + (i - 1) // 2 * 233, location_objects['замок'][1] + 213 * ((i - 1) % 2),
                130,
                130))


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('2d_shooter')
    size = width, height = 1400, 700
    screen = pygame.display.set_mode(size)

    background = pygame.image.load('Все для дизайна/Главное меню игры.jpg').convert()
    background = pygame.transform.smoothscale(background, screen.get_size())
    screen.blit(background, (0, 0))

    lvl_text = []
    for i in range(6):
        lvl_now = pygame.image.load(f'Все для дизайна/{i + 1} уровень.png')
        lvl_now.set_colorkey((255, 255, 255))
        lvl_text.append(lvl_now)

    lock = pygame.image.load(f'Все для дизайна/Замок.png')
    lock.set_colorkey((255, 255, 255))
    # for i in range(6):
    #     lvl_now = pygame.image.load(f'Все для дизайна/замок {i + 1}.png')
    #     lvl_now.set_colorkey((255, 255, 255))
    #     lvl_lock.append(lvl_now)

    star = pygame.image.load(f'Все для дизайна/звезда.png')
    star.set_colorkey((255, 255, 255))

    button = []
    button.append(Button_rect(screen,1035,24,331,50,lambda:print(1)))
    button.append(Button_rect(screen, 898, 569, 457, 105, lambda: print(1)))

    name = 'Женя'  # самое важное в работе
    money, lvl = reading(name)
    screen.blit(background, (0, 0))
    separation()

    fps = 90
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for i in button:
            i.update()
        pygame.display.flip()
        clock.tick(fps)
