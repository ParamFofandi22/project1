import os.path
import cv2
import pygame
import random
import math

pygame.mixer.init()
pygame.init()
# import Title_Screen

# attributes
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 255, 255)
pink = (255, 0, 255)
pygame.init()
screen_width = 800
screen_height = 500
gameWindow = pygame.display.set_mode((screen_width, screen_height))

# image
bgimg = pygame.image.load("BG.jpg")
bgimg = pygame.transform.scale(bgimg, (screen_width, screen_height)).convert_alpha()
end_screen = pygame.image.load("End_screen.png")
end_screen = pygame.transform.scale(end_screen, (screen_width, screen_height)).convert_alpha()
start_screen = pygame.image.load("Start.jpg")
start_screen = pygame.transform.scale(start_screen, (screen_width, screen_height)).convert_alpha()
# custom font
font1 = pygame.font.Font('Persona_Font.ttf', 70)
# screen = pygame.display.set_mode((800,500))


# Game Title
pygame.display.set_caption("Snakes_By_Param")
pygame.display.update()

clock = pygame.time.Clock()
font = pygame.font.Font(None, 45)


#
# with open("Score_file.txt", "r") as f:
#     Score_file = f.read()


def screen_score(text, color, x, y):
    screen_text = font.render(text, True, color)
    gameWindow.blit(screen_text, [x, y])


def plot_snake(gameWindow, color, snk_list, snake_size):
    for x, y in snk_list:
        pygame.draw.rect(gameWindow, color, [x, y, snake_size, snake_size])


# def intro():
#     cap = cv2.VideoCapture('Titile.mp4')
#
#     while (cap.isOpened()):
#         ret, frame = cap.read()
#         if ret == True:
#             frame = cv2.resize(frame, (screen_width, screen_height))
#             cv2.imshow("gameWindow", frame)
#             if (cv2.waitKey(1) & 0xFF == pygame.K_SPACE):
#                 welcome()
#
#     cap.release()
#     cv2.destroyAllWindows()
#     # welcome()


# Game loop
def welcome():
    exit_game = False
    while not exit_game:
        gameWindow.fill(white)
        gameWindow.blit(start_screen, (0, 0))
        pygame.display.update()
        # screen_score("Welcome to snake", black, 260, 240)
        # screen_score("Press SPACE to play", black, 240, 300)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gameloop()
                    # pygame.mixer.music.load("nokia_start_up_tone.mp3")
                    # pygame.mixer.music.play()
        # pygame.display.update()
        clock.tick(60)


def gameloop():
    # Game specific variables
    exit_game = False
    game_over = False
    snake_x = 60
    snake_y = 60
    velocity_x = 0
    velocity_y = 0
    snake_size = 30
    food_x = random.uniform(20, screen_width / 2)
    food_y = random.uniform(20, screen_height / 2)
    init_velocity = 5
    score = 0
    fps = 60
    snk_list = []
    snk_len = 1

    if not os.path.exists("Score_file.txt"):
        with open("Score_file.txt", "w") as f:
            f.write("0")

    with open("Score_file.txt", "r") as f:
        Score_file = f.read()
    while not exit_game:
        if game_over:
            with open("Score_file.txt", "w") as f:
                f.write(str(Score_file))
            gameWindow.fill(white)
            gameWindow.blit(end_screen, (0, 0))

            # my_text = font1.render("Game Over", True, 'black')
            # gameWindow.blit(my_text, (250, 150))
            # screen_score("Press enter to play again", black, 220, 230)
            pygame.mixer.music.load("boom2.wav")
            pygame.mixer.music.play()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        welcome()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        velocity_x = init_velocity
                        velocity_y = 0

                    if event.key == pygame.K_LEFT:
                        velocity_x = -init_velocity
                        velocity_y = 0

                    if event.key == pygame.K_UP:
                        velocity_y = -init_velocity
                        velocity_x = 0

                    if event.key == pygame.K_DOWN:
                        velocity_y = init_velocity
                        velocity_x = 0
                    if event.key == pygame.K_KP0:
                        score += 10
            snake_x = snake_x + velocity_x
            snake_y = snake_y + velocity_y

            if abs(snake_x - food_x) < 25 and abs(snake_y - food_y) < 25:

                score += 10

                food_x = random.uniform(20, screen_width / 2)
                food_y = random.uniform(20, screen_height / 2)
                snk_len += 5
                if score>int(Score_file):
                    Score_file = score
                pygame.mixer.music.load("laser1.wav")
                pygame.mixer.music.play()

            gameWindow.fill(white)
            gameWindow.blit(bgimg, (0, 0))
            screen_score("Score:" + str(score) + "  High Score:" + str(Score_file), pink, 5, 5)

            head = []
            head.append(snake_x)
            head.append(snake_y)
            snk_list.append(head)

            if len(snk_list) > snk_len:
                del snk_list[0]
            if head in snk_list[:-1]:
                game_over = True
                pygame.mixer.music.load("boom2.wav")
                pygame.mixer.music.play()

            if snake_x < 0 or snake_x > screen_width or snake_y < 0 or snake_y > screen_height:
                game_over = True
                pygame.mixer.music.load("boom2.wav")
                pygame.mixer.music.play()
            pygame.draw.rect(gameWindow, red, (food_x, food_y, snake_size, snake_size))
            # plot_head(gameWindow,head_img,snk_list,snake_size)
            plot_snake(gameWindow, blue, snk_list, snake_size)
        pygame.display.update()
        clock.tick(fps)
    pygame.quit()
    quit()


welcome()
