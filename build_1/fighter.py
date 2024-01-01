import pygame

# import main
pygame.init()


class Fighter:
    def __init__(self, x, y):
        self.rect = pygame.Rect((x, y, 80, 180))

        # key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.rect.x = -10
        if key[pygame.K_d]:
            self.rect.x = +10

        # update player position

        # pygame.display.update()

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)
