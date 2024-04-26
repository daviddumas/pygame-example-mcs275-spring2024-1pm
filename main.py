import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, QUIT
import random

pygame.init()

FPS = 60  # frames per second
SPF = 1 / FPS  # seconds per frame
GameClock = pygame.time.Clock()  # manages time in the game

# Color constants
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
GAME_BG = WHITE

# Display area size (will be window size if windowed)
DISP_WIDTH = 1280
DISP_HEIGHT = 720

# Make a "display surface" to draw the game on
DISPLAYSURF = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
DISPLAYSURF.fill(GAME_BG)
pygame.display.set_caption("PyGame Example")  # window title / taskbar string

ASSET_SCALE = 2


def asset(name):
    unscaled = pygame.image.load("assets/" + name + ".png")
    return pygame.transform.scale_by(unscaled, ASSET_SCALE)


class ChargeBar(pygame.sprite.Sprite):
    "Bar representing battery charge state"

    def __init__(self, parent, group=None, charge=None, max=30):
        self.parent = parent
        self.charge = charge if charge is not None else max
        self.max = max
        self.images = [asset("bar{:02d}".format(n)) for n in range(31)]
        self.image = self.images[self._idx()]
        self.rect = self.image.get_rect()
        super().__init__([group] if group is not None else [])

    def _idx(self):
        return min(30, int(31.0 * self.charge / self.max))

    def add_charge(self, x):
        self.charge += x
        self.charge = min(self.max, self.charge)

    def subtract_charge(self, x):
        self.charge -= x
        self.charge = max(0, self.charge)

    def update(self):
        self.image = self.images[self._idx()]
        p = self.parent.rect.midtop
        self.rect.midbottom = (p[0], p[1] - 5)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Sprite is a movable, drawable image that is part of the game
class Player(pygame.sprite.Sprite):
    "Sprite representing the player"
    SPEED = 250  # in pixels/second

    def __init__(self, group=None):
        super().__init__([group] if group is not None else [])
        self.image = asset("Player")
        self.image.set_colorkey(WHITE)
        self.rect = (
            self.image.get_rect()
        )  # rectangular region representing image dimensions
        self.rect.center = (
            DISP_WIDTH // 2,
            DISP_HEIGHT // 2,
        )  # move the center to display center
        self.chargebar = ChargeBar(parent=self, group=group)

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
        self.chargebar.update()

    # draw should accept a surface and put this sprite onto it
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.chargebar.draw(surface)


class Robot(pygame.sprite.Sprite):
    "Sprite representing a NPC robot"
    SPEED = 150  # in pixels/second
    SPRITE_NAME = "RobotNPC_basic"
    CAPACITY = 50
    DRAIN_RATE = 0.5

    def __init__(self, group=None, position=None):
        super().__init__([group] if group is not None else [])
        self.image = asset(self.SPRITE_NAME)
        self.image.set_colorkey(WHITE)
        self.rect = (
            self.image.get_rect()
        )  # rectangular region representing image dimensions
        self.chargebar = ChargeBar(parent=self, group=group, max=self.CAPACITY)
        if position is not None:
            self.rect.center = position
        else:
            self.rect.center = (
                random.randrange(int(0.1 * DISP_WIDTH), int(0.9 * DISP_WIDTH)),
                random.randrange(int(0.1 * DISP_HEIGHT), int(0.9 * DISP_HEIGHT)),
            )

    def update(self):
        self.chargebar.subtract_charge(self.DRAIN_RATE * SPF)
        self.chargebar.update()
        if self.chargebar.charge == 0:
            self.chargebar.kill()
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.chargebar.draw(surface)


class WanderRobot(Robot):
    """Robot that moves randomly (up,down,left,right)"""

    SPRITE_NAME = "RobotNPC_wander"
    possible_steps = [
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1),
        (0.707, 0.707),
        (0.707, -0.707),
        (-0.707, 0.707),
        (-0.707, -0.707),
    ]
    DRAIN_RATE = 1.0

    def __init__(self, group=None, position=None, duration=0.5):
        self.step = random.choice(self.possible_steps)
        self.duration = duration
        self.remaining = self.duration
        super().__init__(group=group, position=position)

    def update(self):
        "Take one step, randomly"
        super().update()
        self.remaining -= SPF
        if self.remaining < 0:
            self.remaining = self.duration
            self.step = random.choice(self.possible_steps)

        v = [self.SPEED * SPF * t for t in self.step]
        self.rect.move_ip(*v)
        if self.rect.left < 0 and self.step[0] < 0:
            self.step = (-self.step[0], self.step[1])
        if self.rect.right > DISP_WIDTH and self.step[0] > 0:
            self.step = (-self.step[0], self.step[1])
        if self.rect.top < 0 and self.step[1] < 0:
            self.step = (self.step[0], -self.step[1])
        if self.rect.bottom > DISP_HEIGHT and self.step[1] > 0:
            self.step = (self.step[0], -self.step[1])


class PatrolRobot(Robot):
    """Robot walks back and forth along a straight line segment"""

    SPRITE_NAME = "RobotNPC_patrol"
    DRAIN_RATE = 1.5

    state_transitions = {
        "out": "back",
        "back": "out",
    }

    def __init__(self, group=None, position=None, direction=None, duration=2):
        """
        Initialize a robot at `position` that takes `steps`
        steps in `direction` then turns around, repeats.
        """
        # Call Bot constructor
        super().__init__(group=group, position=position)
        if direction is None:
            direction = random.choice(
                [
                    (1, 0),
                    (0, 1),
                    (-1, 0),
                    (0, -1),
                    (0.707, 0.707),
                    (0.707, -0.707),
                    (-0.707, 0.707),
                    (-0.707, -0.707),
                ]
            )
        # Do Patrol-specific initialization
        self.vectors = {
            "out": direction,
            "back": (-direction[0], -direction[1]),
        }
        self.duration = duration  # constant
        self.state = "out"  # either "out" or "back"
        self.n = 0  # number of steps so far in the current state

    def update(self):
        "Take a step and turn around if appropriate"
        super().update()
        # Take a step
        v = [self.SPEED * SPF * t for t in self.vectors[self.state]]
        self.rect.move_ip(*v)
        self.n += SPF
        # Is it time to turn around?
        if self.n >= self.duration:
            # indeed, turn around
            self.n = 0
            self.state = self.state_transitions[self.state]


sprites = []

robots = pygame.sprite.Group()  # behaves like a sprite, but is many

# create the robots
for _ in range(5):
    Robot(group=robots)
for _ in range(5):
    WanderRobot(group=robots)
for _ in range(5):
    PatrolRobot(group=robots)

# Add the group of all robots
sprites.append(robots)

# Add the player
sprites.append(Player())


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
