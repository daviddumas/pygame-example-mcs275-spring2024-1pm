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
        self.image = pygame.image.load("assets/Player.png")
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

    def __init__(self,position=None):
        super().__init__()
        self.image = pygame.image.load("assets/RobotNPC.png")
        self.rect = (
            self.image.get_rect()
        )  # rectangular region representing image dimensions
        if position is None:
            self.rect.center = (
            random.randrange(DISP_WIDTH),
            random.randrange(DISP_HEIGHT)
            )  # move the center to display center
        else:
            self.rect.center = position

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class WanderRobot(Robot):
    """NPC robot that moves randomly (up,down,left,right)"""

    # TODO: Make wanderbot speed FPS-independent!
    possible_steps = [  # class attribute
        (3, 0),
        (-3, 0),
        (0, 3),
        (0, -3),
    ]

    def update(self):
        "Take one step, randomly"
        step = random.choice(self.possible_steps) # e.g. step=(1,2)
        self.rect.move_ip(*step)  #   move_ip(1,2)

class PatrolRobot(Robot):
    """Robot walks back and forth along a straight line segment"""

    state_transitions = {
        "out": "back",
        "back": "out",
    }

    def __init__(self, position=None, direction=None, steps=80):
        """
        Initialize a robot at `position` that takes `steps`
        steps in `direction` then turns around, repeats.
        """
        # Call Robot constructor
        super().__init__(position)
        if direction is None:
            direction = random.choice([
                (3, 0),
                (-3, 0),
                (0, 3),
                (0, -3),                
                (3, 3),
                (-3, 3),
                (3, -3),
                (-3, -3),                
            ])
        # Do Patrol-specific initialization
        self.vectors = {
            "out": direction,
            "back": (-direction[0],-direction[1]),
        }
        self.steps = steps  # constant
        self.state = "out"  # either "out" or "back"
        self.n = 0  # number of steps so far in the current state

    def update(self):
        "Take a step and turn around if appropriate"
        # Take a step
        self.rect.move_ip(*self.vectors[self.state])
        self.n += 1
        # Is it time to turn around?
        if self.n == self.steps:
            # indeed, turn around
            self.n = 0
            self.state = self.state_transitions[self.state]



sprites = []
sprites.append(Player())
for _ in range(5):
    sprites.append(Robot())
for _ in range(5):
    sprites.append(WanderRobot())
for _ in range(5):
    sprites.append(PatrolRobot())

# MAIN LOOP
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()  # Shut down pygame/window/etc
            exit()

    # Have each sprite update its internal state
    for s in sprites:
        s.update()

    # Clear the display
    DISPLAYSURF.fill(GAME_BG)
    # Draw the sprites
    for s in sprites:
        s.draw(DISPLAYSURF)

    # Put the new content on the screen
    pygame.display.update()

    # Wait until it's time to update again
    GameClock.tick(FPS)
