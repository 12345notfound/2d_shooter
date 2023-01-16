import pygame
import sqlite3
from interface import Button_rect


def addendum():
    """Добавление аккаунта"""

    con = sqlite3.connect("Базы данных/Данные аккаунтов.db")
    cur = con.cursor()
    cur.execute(
        f"""UPDATE Data
        SET money = '{money}'
        WHERE name = '{name}'""")
    cur.execute(
        f"""UPDATE Data
           SET lvl_glock = '{lvl_glock}'
           WHERE name = '{name}'""")
    con.commit()
    con.close()


def reading(name):
    """считывает нужные данные из БД"""
    con = sqlite3.connect("Базы данных/Данные аккаунтов.db")

    cur = con.cursor()

    result = cur.execute(f"""SELECT * FROM Data
                WHERE name = '{name}'""").fetchall()
    con.close()
    return result[0][3], result[0][7]


def separation():
    screen.blit(background, (0, 0))
    screen.blit(
        pygame.font.Font(None, 70).render(str(money), True,
                                          'black'), (900, 24))
    pygame.draw.rect(screen, 'black', (98, 107, 200, 200), 4)
    pygame.draw.rect(screen, 'black', (98, 417, 200, 200), 4)
    pygame.draw.rect(screen, 'black', (400, 107, 350, 200), 4)
    pygame.draw.rect(screen, 'black', (400, 417, 350, 200), 4)
    if Selected_weapon:
        if Selected_weapon == 1:
            pygame.draw.rect(screen, 'blue', (98, 107, 200, 200), 4)
            screen.blit(improvements, (0, 0, 1400, 700))
            for i in range(lvl_glock // 10):
                pygame.draw.rect(screen, [98, 215, 84], (926 + i * 40, 284, 24, 48))
            for i in range(lvl_glock % 10):
                pygame.draw.rect(screen, [98, 215, 84], (926 + i * 40, 437, 24, 48))

        elif Selected_weapon == 2:
            pygame.draw.rect(screen, 'blue', (98, 417, 200, 200), 4)
            screen.blit(not_improvements, (0, 0, 1400, 700))
        elif Selected_weapon == 3:
            pygame.draw.rect(screen, 'blue', (400, 107, 350, 200), 4)
            screen.blit(not_improvements, (0, 0, 1400, 700))
        elif Selected_weapon == 4:
            pygame.draw.rect(screen, 'blue', (400, 417, 350, 200), 4)
            screen.blit(not_improvements, (0, 0, 1400, 700))


def changing_weapons(number):
    global Selected_weapon
    Selected_weapon = number
    separation()


def plus(number):
    global money, lvl_glock
    if number == 1:
        if money >= 100 and lvl_glock // 10 <= 3:
            money -= 100
            lvl_glock += 10
            separation()
            addendum()
    else:
        if money >= 100 and lvl_glock % 10 <= 3:
            money -= 100
            lvl_glock += 1
            separation()
            addendum()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('2d_shooter')
    size = width, height = 1400, 700
    screen = pygame.display.set_mode(size)

    background = pygame.image.load('Все для дизайна/Рюкзак игра.jpg').convert()
    background = pygame.transform.smoothscale(background, screen.get_size())
    screen.blit(background, (0, 0))
    improvements = pygame.image.load('Все для дизайна/Глок.png')
    improvements.set_colorkey((0, 0, 0))
    not_improvements = pygame.image.load('Все для дизайна/Нет улучшений.png')
    not_improvements.set_colorkey((0, 0, 0))

    Selected_weapon = False
    name = 'Женя'  # самое важное в работе
    money, lvl_glock = reading(name)
    screen.blit(background, (0, 0))
    separation()

    button = []
    button.append(Button_rect(screen, 98, 107, 200, 200, lambda: changing_weapons(1)))
    button.append(Button_rect(screen, 98, 417, 200, 200, lambda: changing_weapons(2)))
    button.append(Button_rect(screen, 400, 107, 350, 200, lambda: changing_weapons(3)))
    button.append(Button_rect(screen, 400, 417, 350, 200, lambda: changing_weapons(4)))
    button.append(Button_rect(screen, 843, 284, 49, 49, lambda: plus(1)))
    button.append(Button_rect(screen, 843, 437, 49, 49, lambda: plus(2)))

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
