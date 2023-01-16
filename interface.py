import pygame

COLOR_INACTIVE = pygame.Color('white')
COLOR_ACTIVE = pygame.Color('dodgerblue2')


class Button_rect:
    def __init__(self,screen, x, y, width, height, function):
        self.screen=screen
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.function = function
        self.accomplishment = True

    def mouse_press(self):
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x >= self.x and mouse_y >= self.y and mouse_x <= self.x + self.width and mouse_y <= self.y + self.height:
                return True
        return False

    def update(self):
        # pygame.draw.rect(self.screen, 'Green', (self.x, self.y, self.width, self.height))
        self.keystate = pygame.key.get_pressed()
        if self.accomplishment:
            if self.mouse_press():
                self.accomplishment = False
                self.function()
        else:
            if not pygame.mouse.get_pressed()[0]:
                self.accomplishment = True


class Button_circle:
    def __init__(self,screen, x, y, radius, function):
        self.screen = screen
        self.x, self.y = x, y
        self.radius = radius

        self.function = function
        self.accomplishment = True

    def mouse_press(self):
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2 <= self.radius ** 2:
                return True
        return False

    def update(self):
        pygame.draw.circle(self.screen, 'Green', (self.x, self.y), self.radius)
        self.keystate = pygame.key.get_pressed()
        if self.accomplishment:
            if self.mouse_press():
                self.accomplishment = False
                self.function()
        else:
            if not pygame.mouse.get_pressed()[0]:
                self.accomplishment = True


class InputBox:
    def __init__(self, screen, x, y, w, h, text='',size=28):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.size = size
        self.txt_surface = pygame.font.Font(None, size).render(text, True, self.color)
        self.active = False
        self.screen = screen

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 30:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = pygame.font.Font(None, self.size).render(self.text, True, self.color)

    def draw(self, screen):
        self.screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class text_output:
    def __init__(self, screen, x, y, text='', size=29):
        self.screen = screen
        self.x, self.y = x, y
        self.color = COLOR_INACTIVE
        self.text = text
        self.size = size
        self.txt_surface = pygame.font.Font(None, size).render(text, True, self.color)

    def change_text(self, text):
        self.text = text
        self.txt_surface = pygame.font.Font(None, self.size).render(text, True, self.color)

    def update(self):
        self.screen.blit(self.txt_surface, (self.x, self.y))

# if __name__ == '__main__':
#     pygame.init()
#     pygame.display.set_caption('Движущийся круг 2')
#     size = width, height = 800, 400
#     screen = pygame.display.set_mode(size)
#
#     button = pygame.sprite.Group()
#
#     # background = pygame.image.load('assets/knife_image.png').convert()
#     # background.set_colorkey((255, 255, 255))
#     Button_rect(50, 50, 200, 100, lambda: print(1))
#     Button_circle(400, 400, 100, lambda: print(1))
#
#     fps = 90  # количество кадров в секунду
#     clock = pygame.time.Clock()
#     running = True
#     while running:  # главный игровой цикл
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             if event.type == pygame.KEYDOWN:
#                 print(event.unicode)
#         screen.fill('black')
#         button.update()
#         # обработка остальных событий
#         # ...
#         # формирование кадра
#         # ...
#         screen.blit(
#             pygame.font.Font(None, 40).render(str(int(clock.get_fps())), True,
#                                               'red'), (100, 100))
#         pygame.display.flip()  # смена кадра
#         # изменение игрового мира
#         # ...
#         # временная задержка
#         clock.tick(fps)
