import pygame
import csv
import os
import random

pygame.init()

clock = pygame.time.Clock()
FPS = 60

# editor window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('PixEditor')
pygame.display.set_icon(pygame.image.load('img/icon.png').convert_alpha())

# define game variables
ROWS = 64
MAX_COLS = 150
PIXEL_SIZE = SCREEN_HEIGHT // ROWS
canvas = 1
current_color = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
clear = False
load = False
save = False
start = False
need_to_save = False
special_color_1_r = random.randint(0, 255)
special_color_1_g = random.randint(0, 255)
special_color_1_b = random.randint(0, 255)
special_color_1 = (special_color_1_r, special_color_1_g, special_color_1_b)

special_color_2_r = random.randint(0, 255)
special_color_2_g = random.randint(0, 255)
special_color_2_b = random.randint(0, 255)
special_color_2 = (special_color_2_r, special_color_2_g, special_color_2_b)

special_color_3_r = random.randint(0, 255)
special_color_3_g = random.randint(0, 255)
special_color_3_b = random.randint(0, 255)
special_color_3 = (special_color_3_r, special_color_3_g, special_color_3_b)

# define font
text_font = pygame.font.SysFont('Futura', 15)
title_text_font = pygame.font.SysFont('Futura', 40)

# create empty tile list
world_data = []
r = [0] * MAX_COLS
for row in range(ROWS):
    r = [0] * MAX_COLS
    world_data.append(r)

# load images
save_img = pygame.image.load('img/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/load_btn.png').convert_alpha()
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
house_img = pygame.image.load('img/house_icon.png').convert_alpha()

# color values in list
# order is: white(0), red(1), orange(2), yellow(3), green(4), blue(5), purple(6), black(7), light grey/gray(8), special color 1(9), special color 2(10), special color 3(11)
rgb_value_list = [(255, 255, 255), (255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128), (0, 0, 0), (211, 211, 211), special_color_1, special_color_2, special_color_3]
WHITE = (255, 255, 255)


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def update(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class ColorPicker:
    def __init__(self, x, y, color, scale):
        self.image = pygame.draw.rect(screen, color, pygame.Rect((x, y), (scale, scale)))
        self.clicked = False

        self.x = x
        self.y = y
        self.color = color
        self.scale = scale

    def update(self, surface):
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.image.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        pygame.draw.rect(screen, self.color, pygame.Rect((self.x, self.y), (self.scale, self.scale)))
        pygame.draw.rect(screen, rgb_value_list[7], pygame.Rect((self.x, self.y), (self.scale, self.scale)), 3)

        return self.clicked


# function for putting text on screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# create function for background
def draw_bg():
    screen.fill(rgb_value_list[0])


# define grid
def draw_grid():
    # vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, rgb_value_list[7], (c * PIXEL_SIZE - scroll, 0), (c * PIXEL_SIZE - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, rgb_value_list[7], (0, c * PIXEL_SIZE), (SCREEN_WIDTH, c * PIXEL_SIZE))


# function for drawing colors
def draw_colors():
    for y, row in enumerate(world_data):
        for x, color in enumerate(row):
            if color > 0:
                pygame.draw.rect(screen, rgb_value_list[color], pygame.Rect(((x * PIXEL_SIZE - scroll) + 1, (y * PIXEL_SIZE) + 1), (PIXEL_SIZE - 1, PIXEL_SIZE - 1)))


# create buttons
save_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 96, save_img, 3)
load_button = Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 96, load_img, 3)
start_button = Button(25, 150, start_img, 3)
home_button = Button(SCREEN_WIDTH + SIDE_MARGIN - 110, SCREEN_HEIGHT + LOWER_MARGIN - 90, house_img, 3)

# make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(rgb_value_list)):
    color_button = ColorPicker(SCREEN_WIDTH + (100 * button_col) + 25, 75 * button_row + 50, rgb_value_list[i], 50)
    button_list.append(color_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

run = True

while run:
    clock.tick(FPS)

    if not start:
        draw_bg()
        draw_text('PixEditor', title_text_font, rgb_value_list[7], 25, 25)
        draw_text('The Pixel Art Editor by...', text_font, rgb_value_list[7], 25, 85)
        draw_text('octaviustheking, KnightSmarts, and Kangaroos in a Can', text_font, rgb_value_list[7], 25, 110)
        draw_text('created with Python and Pygame', text_font, rgb_value_list[7], 25, 135)
        if start_button.update(screen):
            start = True

    else:
        draw_bg()
        draw_grid()
        draw_colors()
        if not need_to_save:
            draw_text(f'Canvas: {canvas}', text_font, rgb_value_list[7], 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
        else:
            draw_text(f'Canvas: {canvas}*', text_font, rgb_value_list[7], 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
        draw_text('Press UP or DOWN to change canvas', text_font, rgb_value_list[7], 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
        # draw_text('COLOR PICKER', title_text_font, rgb_value_list[7], SCREEN_WIDTH - 100, 50)

        if special_color_1_r >= 255:
            special_color_1_r = 0
        else:
            special_color_1_r += 1
        if special_color_1_g >= 255:
            special_color_1_g = 0
        else:
            special_color_1_g += 1
        if special_color_1_b >= 255:
            special_color_1_b = 0
        else:
            special_color_1_b += 1

        special_color_1 = (special_color_1_r, special_color_1_g, special_color_1_b)
        rgb_value_list[9] = special_color_1

        if special_color_2_r >= 255:
            special_color_2_r = 0
        else:
            special_color_2_r += 1
        if special_color_2_g >= 255:
            special_color_2_g = 0
        else:
            special_color_2_g += 1
        if special_color_2_b >= 255:
            special_color_2_b = 0
        else:
            special_color_2_b += 1

        special_color_2 = (special_color_2_r, special_color_2_g, special_color_2_b)
        rgb_value_list[10] = special_color_2

        if special_color_3_r >= 255:
            special_color_3_r = 0
        else:
            special_color_3_r += 1
        if special_color_3_g >= 255:
            special_color_3_g = 0
        else:
            special_color_3_g += 1
        if special_color_3_b >= 255:
            special_color_3_b = 0
        else:
            special_color_3_b += 1

        special_color_3 = (special_color_3_r, special_color_3_g, special_color_3_b)
        rgb_value_list[11] = special_color_3

        # make a button list
        button_list = []
        button_col = 0
        button_row = 0
        for i in range(len(rgb_value_list)):
            color_button = ColorPicker(SCREEN_WIDTH + (100 * button_col) + 25, 75 * button_row + 50, rgb_value_list[i], 50)
            button_list.append(color_button)
            button_col += 1
            if button_col == 3:
                button_row += 1
                button_col = 0

        # save and load data
        if save_button.update(screen) or save:
            # save level data
            with open(f'canvases/canvas{canvas}_data.csv', 'w', newline='') as csvfile:
                # save level data
                writer = csv.writer(csvfile, delimiter=',')
                for row in world_data:
                    writer.writerow(row)
            need_to_save = False
        if load_button.update(screen) or load:
            # load in level data
            # reset scroll
            scroll = 0
            if os.path.exists(f'canvases/canvas{canvas}_data.csv'):
                with open(f'canvases/canvas{canvas}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
        if home_button.update(screen):
            start = False

        # draw color panel
        pygame.draw.rect(screen, rgb_value_list[7], (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT), 3)
        pygame.draw.rect(screen, rgb_value_list[0], (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

        for button in button_list:
            button.update(screen)

        # choose a tile
        button_count = 0
        for button_count, i in enumerate(button_list):
            if i.update(screen):
                current_color = button_count

        # highlight the selected color
        pygame.draw.rect(screen, rgb_value_list[1], button_list[current_color].image, 3)

        # scroll
        if scroll_left and scroll > 0:
            scroll -= 5 * scroll_speed
        if scroll_right and scroll < (MAX_COLS * PIXEL_SIZE) - SCREEN_WIDTH:
            scroll += 5 * scroll_speed

        # check if clear
        if clear:
            for y, row in enumerate(world_data):
                for x, replacement in enumerate(row):
                    world_data[y][x] = 0

        # add new tiles to screen
        # get mouse position
        pos = pygame.mouse.get_pos()
        x = (pos[0] + scroll) // PIXEL_SIZE
        y = pos[1] // PIXEL_SIZE

        # check coordinates are in with area
        if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
            # update tile value
            if pygame.mouse.get_pressed()[0] == 1:
                if world_data[y][x] != current_color:
                    world_data[y][x] = current_color
                    need_to_save = True
            if pygame.mouse.get_pressed()[2] == 1:
                world_data[y][x] = -1
                need_to_save = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if start:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    canvas += 1
                if event.key == pygame.K_DOWN and canvas > 1:
                    canvas -= 1
                if event.key == pygame.K_LEFT:
                    scroll_left = True
                if event.key == pygame.K_RIGHT:
                    scroll_right = True
                if event.key == pygame.K_RSHIFT:
                    scroll_speed = 5
                if event.key == pygame.K_LSHIFT:
                    scroll_speed = 5
                if event.key == pygame.K_c:
                    clear = True
                if event.key == pygame.K_l:
                    load = True
                if event.key == pygame.K_s:
                    save = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1
            if event.key == pygame.K_c:
                clear = False
            if event.key == pygame.K_l:
                load = False
            if event.key == pygame.K_s:
                save = False

    pygame.display.update()

pygame.quit()