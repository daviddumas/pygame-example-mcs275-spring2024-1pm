import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, QUIT
import random

pygame.init()

FPS = 60  # frames per second
SPF = 1 / FPS  # seconds per frame
GameClock = pygame.time.Clock()  # manages time in the game

# Color constants
WHITE = (255, 255, 255)
GRAY = (180,180,180)
GAME_BG = GRAY

# Display area size (will be window size if windowed)
DISP_WIDTH = 800
DISP_HEIGHT = 600

# Make a "display surface" to draw the game on
DISPLAYSURF = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
pygame.display.set_caption("PyGame Example")  # window title / taskbar string


# Sprite is a movable, drawable image that is part of the game
class Player(pygame.sprite.Sprite):
    "Sprite representing the player"
    SPEED = 250  # in pixels/second

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.image.set_colorkey(WHITE)
        self.rect = (
            self.image.get_rect()
        )  # rectangular region representing image dimensions
        self.rect.center = (
            DISP_WIDTH // 2,
            DISP_HEIGHT // 2,
        )  # move the center to display center

    def update(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-self.SPEED * SPF, 0)
        if self.rect.right < DISP_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(self.SPEED * SPF, 0)
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -self.SPEED * SPF)
        if self.rect.bottom < DISP_HEIGHT:
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, self.SPEED * SPF)

    # draw should accept a surface and put this sprite onto it
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Robot(pygame.sprite.Sprite):
    "Sprite representing a robot NPC"

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("RobotNPC.png")
        self.rect = (
            self.image.get_rect()
        )  # rectangular region representing image dimensions
        self.rect.center = (
           random.randrange(DISP_WIDTH),
           random.randrange(DISP_HEIGHT)
        )  # move the center to display center

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


p = Player()
q = Robot()

# MAIN LOOP
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()  # Shut down pygame/window/etc
            exit()

    # Have each sprite update its internal state
    p.update()
    q.update()

    # Clear the display
    DISPLAYSURF.fill(GAME_BG)
    # Draw the sprites
    q.draw(DISPLAYSURF)
    p.draw(DISPLAYSURF)

    # Put the new content on the screen
    pygame.display.update()

    # Wait until it's time to update again
    GameClock.tick(FPS)
