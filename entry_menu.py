import pygame
from interface import text_output, InputBox, Button_rect
import sqlite3
import hashlib


def search(login, name_column):
    """Поиск нужной информации в БД"""

    con = sqlite3.connect("Базы данных/Данные аккаунтов.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT {name_column} FROM Data
            WHERE name=='{login}'""").fetchall()

    con.close()
    if result:
        return result[0][0]
    else:
        return None


def addendum(login, password):
    """Добавление аккаунта"""

    con = sqlite3.connect("Базы данных/Данные аккаунтов.db")
    cur = con.cursor()
    cur.execute(
        f"""INSERT INTO Data(name, password, money, training_1, training_2, lvl_1, lvl_glock) VALUES('{login}','{password}', '0', '0', '0', '0','0')""").fetchall()
    con.commit()
    con.close()


def registration():
    global text, running
    """регистрация и вход в аккаунт"""

    login_Account = input_boxes[0].text
    if search(login_Account, 'password'):
        text.change_text('Аккаунт с таким логином уже существует!')
    else:
        password_Account = input_boxes[1].text
        if password_check(password_Account):
            text.change_text(f'{password_check(password_Account)}')
        else:
            addendum(login_Account, hashlib.sha224(bytes(password_Account, encoding='utf-8')).hexdigest())
            running = False
            return


def Entrance():
    """вход в аккаунт"""
    global running
    login_Account = input_boxes[0].text
    if search(login_Account, 'Password'):
        if hashlib.sha224(bytes(input_boxes[1].text, encoding='utf-8')).hexdigest() == search(
                login_Account, 'Password'):
            running = False
        else:
            text.change_text('Вы ввели неправильный пароль!')

    else:
        text.change_text('Аккаунта с таким логином не существует!')


def password_check(password):
    """проверка пароля"""

    if len(password) >= 5:
        if password == password.lower():
            return 'В пароле нет заглавных букв!'
        elif password == password.upper():
            return 'В пароле нет строчных букв!'
        else:
            return False
    else:
        return 'Вы ввели слишком короткий пароль!'


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('2d_shooter')
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)

    background = pygame.image.load('Все для дизайна/Меню регистрации.jpg').convert()
    background = pygame.transform.smoothscale(background, screen.get_size())

    input_boxes = []
    input_boxes.append(InputBox(screen, 55, 250, 492, 26, size=24))
    input_boxes.append(InputBox(screen, 55, 326, 492, 26, size=24))

    buttons = []
    buttons.append(Button_rect(screen, 42, 372, 250, 60, Entrance))
    buttons.append(Button_rect(screen, 308, 372, 250, 60, registration))

    text = text_output(screen, 65, 490, text='', size=32)

    fps = 60
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for box in input_boxes:
                box.handle_event(event)
        screen.blit(background, (0, 0))

        for box in input_boxes:
            box.draw(screen)
        for button in buttons:
            button.update()
        text.update()
        pygame.display.flip()
        clock.tick(fps)
