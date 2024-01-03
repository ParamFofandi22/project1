import pygame
from pygame import mixer
import random

mixer.init()
pygame.init()

screen_width = 1000
screen_height = 600
fps = 60

char_num1 = 0
char_num2 = 0


class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_image(sprite_sheet, animation_steps)
        self.action = 0  #:idle #1:run #2:jump #3:attack1 #4:attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True
        self.ch1 = 0
        self.ch2 = 0

    def load_image(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_image_list = []
            for x in range(animation):
                temp_image = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_image_list.append(
                    pygame.transform.scale(temp_image, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_image_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0
        key = pygame.key.get_pressed()

        if self.attacking == False and self.alive == True and round_over == False:
            if self.player == char_num1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2
            if self.player == char_num2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # death
        elif self.hit == True:
            self.update_action(5)  # hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)  # attack 1
            elif self.attack_type == 2:
                self.update_action(4)  # attack2
        elif self.jump == True:
            self.update_action(2)  # jump
        elif self.running == True:
            self.update_action(1)  # run
        else:
            self.update_action(0)  # idle

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                         2 * self.rect.width, self.rect.height)

            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (
            self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


gameWindow = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("fighter")

clock = pygame.time.Clock()

WARRIOR_SIZE = 162
WARRIOR_SCALE = 3
WARRIOR_OFFSET = [72, 24]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 90]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]
SAMURAI_SIZE = 200
SAMURAI_SCALE = 3
SAMURAI_OFFSET = [90, 45]
SAMURAI_DATA = [SAMURAI_SIZE, SAMURAI_SCALE, SAMURAI_OFFSET]
HUNTER_SIZE = 126
HUNTER_SCALE = 3
HUNTER_OFFSET = [40, 5]
HUNTER_DATA = [HUNTER_SIZE, HUNTER_SCALE, HUNTER_OFFSET]

battle_music1 = pygame.mixer.Sound("assets/audio/battle1.mp3")
battle_music2 = pygame.mixer.Sound("assets/audio/battle2.mp3")
battle_music1.set_volume(0.5)
battle_music2.set_volume(0.5)
music_list = [battle_music1, battle_music2]
battle_music = (random.choice(music_list))

play_fx = pygame.mixer.Sound("assets/audio/play_sound.mp3")
pygame.mixer.music.set_volume(0.5)
click_fx = pygame.mixer.Sound("assets/audio/selection_sound.mp3")
pygame.mixer.music.set_volume(0.5)

sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.8)
katana_fx = pygame.mixer.Sound("assets/audio/katana.mp3")
katana_fx.set_volume(0.6)
cutlass_fx = pygame.mixer.Sound("assets/audio/cutlass.wav")
cutlass_fx.set_volume(0.75)

bg_image1 = pygame.image.load("assets/images/background/isle.gif").convert_alpha()
bg_image2 = pygame.image.load("assets/images/background/desert.gif").convert_alpha()
bg_image3 = pygame.image.load("assets/images/background/Harbor.gif").convert_alpha()
bg_image4 = pygame.image.load("assets/images/background/temple.gif").convert_alpha()
bg_list = [bg_image1, bg_image2, bg_image3, bg_image4]
bg_image = (random.choice(bg_list))
bg_end = pygame.image.load("assets/images/background/end_screen.jpg").convert_alpha()
bg_end_scaled = pygame.transform.scale(bg_end, (screen_width, screen_height))

warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()
samurai_sheet = pygame.image.load("assets/images/Samurai/Samurai.png").convert_alpha()
hunter_sheet = pygame.image.load("assets/images/Hunter/Hunter.png").convert_alpha()
victory = pygame.image.load("assets/images/icons/Untitled-1.png").convert_alpha()
victory_img = pygame.transform.scale(victory, (screen_width, screen_height))

WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]
SAMURAI__ANIMATION_STEPS = [8, 7, 2, 6, 6, 4, 6]
HUNTER_ANIMATION_STEPS = [10, 8, 3, 7, 6, 3, 11]

count_font = pygame.font.Font("assets/fonts/edosz.ttf", 110)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
char_font = pygame.font.Font("assets/fonts/turok.ttf", 40)
win_font = pygame.font.Font("assets/fonts/turok.ttf", 110)

char_select1 = pygame.image.load("assets/images/background/char_select.png").convert_alpha()
chr_image1 = pygame.image.load("assets/images/icons/warrior1.png").convert_alpha()
chr_image2 = pygame.image.load("assets/images/icons/wizard1.png").convert_alpha()
chr_image3 = pygame.image.load("assets/images/icons/samurai1.png").convert_alpha()
chr_image4 = pygame.image.load("assets/images/icons/hunter1.png").convert_alpha()
scaled_ch1 = pygame.transform.scale(char_select1, (screen_width, screen_height))

char1 = pygame.transform.scale(chr_image1, (screen_width, screen_height + 70))
char2 = pygame.transform.scale(chr_image2, (screen_width, screen_height + 70))
char3 = pygame.transform.scale(chr_image3, (screen_width, screen_height + 70))
char4 = pygame.transform.scale(chr_image4, (screen_width, screen_height + 70))

Hp1_back = pygame.image.load("assets/images/icons/p1_health_fore.png").convert_alpha()
Hp1 = pygame.image.load("assets/images/icons/p1_health.png").convert_alpha()
Hp2_back = pygame.image.load("assets/images/icons/p2_health_fore.png").convert_alpha()
Hp2 = pygame.image.load("assets/images/icons/p2_health.png").convert_alpha()


def start_screen():
    exit_game = 0
    while exit_game == 0:
        background = pygame.image.load("assets/images/background/start.png").convert_alpha()
        scaled_bg = pygame.transform.scale(background, (screen_width, screen_height))
        play = pygame.image.load("assets/images/icons/Play.png")
        scaled_play = pygame.transform.scale(play, (screen_width, screen_height / 1.5))
        gameWindow.blit(scaled_bg, (0, 0))
        play_button = Button(400, 400, scaled_play, 0.2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    select_ch1()
                    exit_game += 1
        if play_button.draw(gameWindow):
            play_fx.play()
            exit_game += 1
            select_ch1()
        pygame.display.update()


def select_ch1():
    global char_num1
    char_pick1 = char_font.render("Pick the character for player 1", True, 'black')
    char1_button = Button(20, 30, char1, 0.2)
    char2_button = Button(20, 160, char2, 0.2)
    char3_button = Button(20, 290, char3, 0.2)
    char4_button = Button(20, 420, char4, 0.2)

    run = True
    while run:
        gameWindow.blit(scaled_ch1, (0, 0))
        gameWindow.blit(char_pick1, (230, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        if char1_button.draw(gameWindow):
            char_num1 = 1
            click_fx.play()
            run = False
            select_ch2()

        if char2_button.draw(gameWindow):
            char_num1 = 2
            click_fx.play()
            run = False
            select_ch2()

        if char3_button.draw(gameWindow):
            char_num1 = 3
            click_fx.play()
            run = False
            select_ch2()

        if char4_button.draw(gameWindow):
            char_num1 = 4
            click_fx.play()
            run = False
            select_ch2()
        pygame.display.update()


def select_ch2():
    global char_num2
    global char_num1
    char_pick2 = char_font.render("Pick the character for player 2", True, 'black')
    if char_num1 != 1:
        char1_button = Button(780, 30, char1, 0.2)
    if char_num1 != 2:
        char2_button = Button(780, 160, char2, 0.2)
    if char_num1 != 3:
        char3_button = Button(780, 290, char3, 0.2)
    if char_num1 != 4:
        char4_button = Button(780, 420, char4, 0.2)

    run = True
    while run:
        gameWindow.blit(scaled_ch1, (0, 0))
        gameWindow.blit(char_pick2, (230, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        if char_num1 != 1:
            if char1_button.draw(gameWindow):
                char_num2 = 1
                run = False
                gameloop()
        if char_num1 != 2:
            if char2_button.draw(gameWindow):
                char_num2 = 2
                run = False
                gameloop()
        if char_num1 != 3:
            if char3_button.draw(gameWindow):
                char_num2 = 3
                run = False
                gameloop()
        if char_num1 != 4:
            if char4_button.draw(gameWindow):
                char_num2 = 4
                run = False
                gameloop()
        pygame.display.update()


def gameloop():
    win_condition = 3
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]
    round_over = False
    ROUND_OVER_COOLDOWN = 2000
    battle_music.play()

    def draw_text(text, font, text_col, x, y):
        image = font.render(text, True, text_col)
        gameWindow.blit(image, (x, y))

    def draw_bg():
        scaled_bg = pygame.transform.scale(bg_image, (screen_width, screen_height))
        gameWindow.blit(scaled_bg, (0, 0))

    def draw_health_bar(health, x, y):
        ratio = health / 100
        scaled_Hp1_back = pygame.transform.scale(Hp1_back, (screen_width / 1.6, screen_height / 1.1))
        gameWindow.blit(scaled_Hp1_back, (x, y))
        pygame.draw.rect(gameWindow, 'red', (50, 26, 430 * ratio, 30))
        pygame.draw.rect(gameWindow, 'green', (55, 29, 420 * ratio, 25))

    def draw_health_bar2(health, x, y):
        ratio = health / 100
        scaled_Hp2_back = pygame.transform.scale(Hp2_back, (screen_width / 1.6, screen_height / 1.1))
        gameWindow.blit(scaled_Hp2_back, (x - 20, y - 180))
        pygame.draw.rect(gameWindow, 'red', (518, 26, 430 * ratio, 30))
        pygame.draw.rect(gameWindow, 'green', (523, 29, 420 * ratio, 25))

    def end_screen():
        battle_music.stop()
        gameWindow.blit(bg_end_scaled, (0, 0))
        if score[0] == win_condition and score[1] != win_condition:
            win1 = win_font.render("player 1 win", True, 'black')
            gameWindow.blit(win1, (230, 200))
        if score[1] == win_condition and score[0] != win_condition:
            win2 = win_font.render("player 2 win", True, 'black')
            gameWindow.blit(win2, (230, 200))
        if score[0] == score[1]:
            win3 = win_font.render("draw", True, 'black')
            gameWindow.blit(win3, (380, 200))
        pygame.display.update()

    if char_num1 == 1 and char_num2 == 2:
        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    if char_num1 == 1 and char_num2 == 3:
        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_3 = Fighter(3, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
    if char_num1 == 1 and char_num2 == 4:
        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_4 = Fighter(4, 700, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)

    if char_num1 == 2 and char_num2 == 1:
        fighter_2 = Fighter(2, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
        fighter_1 = Fighter(1, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    if char_num1 == 2 and char_num2 == 3:
        fighter_2 = Fighter(2, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
        fighter_3 = Fighter(3, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
    if char_num1 == 2 and char_num2 == 4:
        fighter_2 = Fighter(2, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
        fighter_4 = Fighter(4, 700, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)

    if char_num1 == 3 and char_num2 == 1:
        fighter_3 = Fighter(3, 200, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
        fighter_1 = Fighter(1, 700, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    if char_num1 == 3 and char_num2 == 2:
        fighter_3 = Fighter(3, 200, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
        fighter_2 = Fighter(2, 700, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    if char_num1 == 3 and char_num2 == 4:
        fighter_3 = Fighter(3, 200, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
        fighter_4 = Fighter(4, 700, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)

    if char_num1 == 4 and char_num2 == 1:
        fighter_4 = Fighter(4, 200, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)
        fighter_1 = Fighter(1, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    if char_num1 == 4 and char_num2 == 2:
        fighter_4 = Fighter(4, 200, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)
        fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    if char_num1 == 4 and char_num2 == 3:
        fighter_4 = Fighter(4, 200, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)
        fighter_3 = Fighter(3, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)

    if char_num2 == 1 and char_num1 == 2:
        fighter_1 = Fighter(1, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_2 = Fighter(2, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    if char_num2 == 1 and char_num1 == 3:
        fighter_1 = Fighter(1, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_3 = Fighter(3, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
    if char_num2 == 1 and char_num1 == 4:
        fighter_1 = Fighter(1, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_4 = Fighter(4, 200, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)

    if char_num2 == 2 and char_num1 == 1:
        fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    if char_num2 == 2 and char_num1 == 3:
        fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
        fighter_3 = Fighter(3, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
    if char_num2 == 2 and char_num1 == 4:
        fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
        fighter_4 = Fighter(4, 200, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)

    if char_num2 == 3 and char_num1 == 1:
        fighter_3 = Fighter(3, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    if char_num2 == 3 and char_num1 == 2:
        fighter_3 = Fighter(3, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
        fighter_2 = Fighter(2, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    if char_num2 == 3 and char_num1 == 4:
        fighter_3 = Fighter(3, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)
        fighter_4 = Fighter(4, 200, 310, False, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)

    if char_num2 == 4 and char_num1 == 1:
        fighter_3 = Fighter(4, 700, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)
        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    if char_num2 == 4 and char_num1 == 2:
        fighter_3 = Fighter(4, 700, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)
        fighter_2 = Fighter(2, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    if char_num2 == 4 and char_num1 == 3:
        fighter_4 = Fighter(4, 700, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS, cutlass_fx)
        fighter_3 = Fighter(3, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS, katana_fx)

    run = True
    while run:
        clock.tick(fps)
        draw_bg()

        if char_num1 == 1:
            draw_health_bar(fighter_1.health, -25, -170)
        if char_num1 == 2:
            draw_health_bar(fighter_2.health, -25, -170)
        if char_num1 == 3:
            draw_health_bar(fighter_3.health, -25, -170)
        if char_num1 == 4:
            draw_health_bar(fighter_4.health, -25, -170)

        if char_num2 == 1:
            draw_health_bar2(fighter_1.health, 490, 10)
        if char_num2 == 2:
            draw_health_bar2(fighter_2.health, 490, 10)
        if char_num2 == 3:
            draw_health_bar2(fighter_3.health, 490, 10)
        if char_num2 == 4:
            draw_health_bar2(fighter_4.health, 490, 10)

        if char_num1 == 1:
            draw_text("Warrior: " + str(score[0]), score_font, 'red', 190, 21)
        if char_num1 == 2:
            draw_text("Wizard: " + str(score[0]), score_font, 'red', 190, 21)
        if char_num1 == 3:
            draw_text("Samurai: " + str(score[0]), score_font, 'red', 190, 21)
        if char_num1 == 4:
            draw_text("Hunter: " + str(score[0]), score_font, 'red', 190, 21)

        if char_num2 == 1:
            draw_text("Warrior: " + str(score[1]), score_font, 'red', 680, 21)
        if char_num2 == 2:
            draw_text("Wizard: " + str(score[1]), score_font, 'red', 680, 21)
        if char_num2 == 3:
            draw_text("Samurai: " + str(score[1]), score_font, 'red', 680, 21)
        if char_num2 == 4:
            draw_text("Hunter: " + str(score[1]), score_font, 'red', 680, 21)

        if intro_count <= 0:
            if char_num1 == 1 and char_num2 == 2:
                fighter_1.move(screen_width, screen_height, gameWindow, fighter_2, round_over)
                fighter_2.move(screen_width, screen_height, gameWindow, fighter_1, round_over)
            if char_num1 == 1 and char_num2 == 3:
                fighter_1.move(screen_width, screen_height, gameWindow, fighter_3, round_over)
                fighter_3.move(screen_width, screen_height, gameWindow, fighter_1, round_over)
            if char_num1 == 1 and char_num2 == 4:
                fighter_1.move(screen_width, screen_height, gameWindow, fighter_4, round_over)
                fighter_4.move(screen_width, screen_height, gameWindow, fighter_1, round_over)

            if char_num1 == 2 and char_num2 == 1:
                fighter_2.move(screen_width, screen_height, gameWindow, fighter_1, round_over)
                fighter_1.move(screen_width, screen_height, gameWindow, fighter_2, round_over)
            if char_num1 == 2 and char_num2 == 3:
                fighter_2.move(screen_width, screen_height, gameWindow, fighter_3, round_over)
                fighter_3.move(screen_width, screen_height, gameWindow, fighter_2, round_over)
            if char_num1 == 2 and char_num2 == 4:
                fighter_2.move(screen_width, screen_height, gameWindow, fighter_4, round_over)
                fighter_4.move(screen_width, screen_height, gameWindow, fighter_2, round_over)

            if char_num1 == 3 and char_num2 == 1:
                fighter_3.move(screen_width, screen_height, gameWindow, fighter_1, round_over)
                fighter_1.move(screen_width, screen_height, gameWindow, fighter_3, round_over)
            if char_num1 == 3 and char_num2 == 2:
                fighter_3.move(screen_width, screen_height, gameWindow, fighter_2, round_over)
                fighter_2.move(screen_width, screen_height, gameWindow, fighter_3, round_over)
            if char_num1 == 3 and char_num2 == 4:
                fighter_3.move(screen_width, screen_height, gameWindow, fighter_4, round_over)
                fighter_4.move(screen_width, screen_height, gameWindow, fighter_3, round_over)

            if char_num1 == 4 and char_num2 == 1:
                fighter_4.move(screen_width, screen_height, gameWindow, fighter_1, round_over)
                fighter_1.move(screen_width, screen_height, gameWindow, fighter_4, round_over)
            if char_num1 == 4 and char_num2 == 2:
                fighter_4.move(screen_width, screen_height, gameWindow, fighter_2, round_over)
                fighter_2.move(screen_width, screen_height, gameWindow, fighter_4, round_over)
            if char_num1 == 4 and char_num2 == 3:
                fighter_4.move(screen_width, screen_height, gameWindow, fighter_3, round_over)
                fighter_3.move(screen_width, screen_height, gameWindow, fighter_4, round_over)
        else:
            draw_text(str(intro_count), count_font, 'red', screen_width / 2, screen_height / 3)
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        if char_num1 == 1 and char_num2 == 2:
            fighter_1.update()
            fighter_2.update()
            fighter_1.draw(gameWindow)
            fighter_2.draw(gameWindow)
        if char_num1 == 1 and char_num2 == 3:
            fighter_1.update()
            fighter_3.update()
            fighter_1.draw(gameWindow)
            fighter_3.draw(gameWindow)
        if char_num1 == 1 and char_num2 == 4:
            fighter_1.update()
            fighter_4.update()
            fighter_1.draw(gameWindow)
            fighter_4.draw(gameWindow)

        if char_num1 == 2 and char_num2 == 1:
            fighter_2.update()
            fighter_1.update()
            fighter_2.draw(gameWindow)
            fighter_1.draw(gameWindow)
        if char_num1 == 2 and char_num2 == 3:
            fighter_2.update()
            fighter_3.update()
            fighter_2.draw(gameWindow)
            fighter_3.draw(gameWindow)
        if char_num1 == 2 and char_num2 == 4:
            fighter_2.update()
            fighter_4.update()
            fighter_2.draw(gameWindow)
            fighter_4.draw(gameWindow)

        if char_num1 == 3 and char_num2 == 1:
            fighter_3.update()
            fighter_1.update()
            fighter_3.draw(gameWindow)
            fighter_1.draw(gameWindow)
        if char_num1 == 3 and char_num2 == 2:
            fighter_3.update()
            fighter_2.update()
            fighter_3.draw(gameWindow)
            fighter_2.draw(gameWindow)
        if char_num1 == 3 and char_num2 == 4:
            fighter_3.update()
            fighter_4.update()
            fighter_3.draw(gameWindow)
            fighter_4.draw(gameWindow)

        if char_num1 == 4 and char_num2 == 1:
            fighter_4.update()
            fighter_1.update()
            fighter_4.draw(gameWindow)
            fighter_1.draw(gameWindow)
        if char_num1 == 4 and char_num2 == 2:
            fighter_4.update()
            fighter_2.update()
            fighter_4.draw(gameWindow)
            fighter_2.draw(gameWindow)
        if char_num1 == 4 and char_num2 == 3:
            fighter_4.update()
            fighter_3.update()
            fighter_4.draw(gameWindow)
            fighter_3.draw(gameWindow)

        if round_over == False:
            if char_num1 == 1 and char_num2 == 2:
                if fighter_2.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 1 and char_num2 == 3:
                if fighter_3.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 1 and char_num2 == 4:
                if fighter_4.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num1 == 2 and char_num2 == 1:
                if fighter_1.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 2 and char_num2 == 3:
                if fighter_3.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 2 and char_num2 == 4:
                if fighter_4.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num1 == 3 and char_num2 == 1:
                if fighter_1.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 3 and char_num2 == 2:
                if fighter_2.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 3 and char_num2 == 4:
                if fighter_4.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num1 == 4 and char_num2 == 1:
                if fighter_1.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 4 and char_num2 == 2:
                if fighter_2.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num1 == 4 and char_num2 == 3:
                if fighter_3.alive == False:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num2 == 1 and char_num1 == 2:
                if fighter_2.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 1 and char_num1 == 3:
                if fighter_3.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 1 and char_num1 == 4:
                if fighter_4.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num2 == 2 and char_num1 == 1:
                if fighter_1.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 2 and char_num1 == 3:
                if fighter_3.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 2 and char_num1 == 4:
                if fighter_4.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num2 == 3 and char_num1 == 1:
                if fighter_1.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 3 and char_num1 == 2:
                if fighter_2.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 3 and char_num1 == 4:
                if fighter_4.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

            if char_num2 == 4 and char_num1 == 1:
                if fighter_1.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 4 and char_num1 == 2:
                if fighter_2.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            if char_num2 == 4 and char_num1 == 3:
                if fighter_3.alive == False:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()


        else:
            gameWindow.blit(victory_img, (0, 0))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_over = 3
                if char_num1 == 1:
                    fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS,
                                        sword_fx)
                if char_num1 == 2:
                    fighter_2 = Fighter(2, 200, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                if char_num1 == 3:
                    fighter_3 = Fighter(3, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS,
                                        katana_fx)
                if char_num1 == 4:
                    fighter_4 = Fighter(4, 200, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS,
                                        cutlass_fx)

                if char_num2 == 1:
                    fighter_1 = Fighter(1, 700, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS,
                                        sword_fx)
                if char_num2 == 2:
                    fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                if char_num2 == 3:
                    fighter_3 = Fighter(3, 700, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI__ANIMATION_STEPS,
                                        katana_fx)
                if char_num2 == 4:
                    fighter_4 = Fighter(4, 700, 310, True, HUNTER_DATA, hunter_sheet, HUNTER_ANIMATION_STEPS,
                                        cutlass_fx)
        if score[0] == win_condition:
            end_screen()
        elif score[1] == win_condition:
            end_screen()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


start_screen()
pygame.quit()
quit
