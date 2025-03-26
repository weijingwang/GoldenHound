import pygame
import sys
import math

# Screen and game configuration
SCREEN_WIDTH = 1270
SCREEN_HEIGHT = 720
FPS = 60

# Camera settings
CAMERA_DEADZONE_TOP = 300
CAMERA_DEADZONE_BOTTOM = 400

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Player movement constants
PLAYER_WIDTH = 200
PLAYER_HEIGHT = 100
MAX_MOVE_SPEED = 10
ACCELERATION = 1
FRICTION = 0.2
JUMP_STRENGTH = 22
GRAVITY = 0.6
JUMP_BUFFER_TIME = 6
COYOTE_TIME = 6

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Apply camera offset to an entity's rect."""
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        """Apply camera offset to a given rect."""
        return rect.move(self.camera.topleft)

    def update(self, target):
        """Update camera position based on player position."""
        # Calculate the target y position
        x = -target.rect.x + self.width // 2
        y = -target.rect.y + self.height // 2

        # Vertical camera movement with deadzone
        if target.rect.y < self.camera.y + CAMERA_DEADZONE_TOP:
            y = -(target.rect.y - CAMERA_DEADZONE_TOP)
        
        if target.rect.y > self.camera.y + self.height - CAMERA_DEADZONE_BOTTOM:
            y = -(target.rect.y - (self.height - CAMERA_DEADZONE_BOTTOM))

        # Update camera position
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load and set up player images
        self.load_images()
        
        # Player state
        self.rect = self.image.get_rect(x=x, y=y)
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Movement and jumping variables
        self.on_ground = False
        self.still_on_ground = False
        self.jump_buffer = 0
        self.coyote_timer = 0
        self.facing_right = True

    def load_images(self):
        """Load player images with error handling."""
        def load_safe_image(path, fallback_color):
            try:
                image = pygame.image.load(path)
                return pygame.transform.scale(image, (PLAYER_WIDTH, PLAYER_HEIGHT))
            except pygame.error:
                surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
                surface.fill(fallback_color)
                return surface

        self.rest_image = load_safe_image('assets/images/player_1.png', (255, 0, 0))
        self.jump_image = load_safe_image('assets/images/player_jump.png', (0, 255, 0))
        self.fall_image = load_safe_image('assets/images/player_fall.png', (0, 0, 255))
        
        # Default to rest image
        self.image = self.rest_image

    def handle_horizontal_movement(self, keys):
        """Handle horizontal player movement."""
        if keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
            # Stop if both directions pressed
            self.velocity_x = 0 if abs(self.velocity_x) <= FRICTION else self.velocity_x - math.copysign(FRICTION, self.velocity_x)
        elif keys[pygame.K_LEFT]:
            # Move left
            self.velocity_x = max(self.velocity_x - ACCELERATION, -MAX_MOVE_SPEED)
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            # Move right
            self.velocity_x = min(self.velocity_x + ACCELERATION, MAX_MOVE_SPEED)
            self.facing_right = True
        else:
            # Apply friction when no movement keys are pressed
            self.velocity_x = 0 if abs(self.velocity_x) <= FRICTION else self.velocity_x - math.copysign(FRICTION, self.velocity_x)

    def handle_jumping(self, keys):
        """Handle player jumping mechanics."""
        if keys[pygame.K_SPACE]:
            self.jump_buffer = JUMP_BUFFER_TIME
        
        self.jump_buffer = max(0, self.jump_buffer - 1)
        
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Execute jump
        if self.jump_buffer > 0 and self.coyote_timer > 0:
            self.velocity_y = -JUMP_STRENGTH
            self.jump_buffer = 0
            self.coyote_timer = 0
            self.on_ground = False

    def update(self, platforms):
        """Update player state and position."""
        keys = pygame.key.get_pressed()
        
        # Handle movement and jumping
        self.handle_horizontal_movement(keys)
        self.handle_jumping(keys)

        # Apply gravity
        self.velocity_y += GRAVITY

        # Horizontal movement and collision
        self.rect.x += self.velocity_x
        self.handle_horizontal_collision(platforms)

        # Vertical movement and collision
        self.rect.y += self.velocity_y
        self.handle_vertical_collision(platforms)

        # Update image
        self.update_image()
        
        # Track ground state
        self.still_on_ground = self.on_ground

    def update_image(self):
        """Determine and set current player image."""
        if not self.still_on_ground:
            # In air
            self.image = self.jump_image if self.velocity_y < 0 else self.fall_image
        else:
            # On ground
            self.image = self.rest_image

        # Flip image based on direction
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def handle_horizontal_collision(self, platforms):
        """Handle horizontal collisions with platforms."""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.velocity_x = 0
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.velocity_x = 0

    def handle_vertical_collision(self, platforms):
        """Handle vertical collisions with platforms."""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

        self.still_on_ground |= self.on_ground

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(x=x, y=y)

def load_background():
    """Load or create background."""
    try:
        background = pygame.image.load('assets/images/bot_back.png')
        return pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        # Create a gradient background
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            r = int(135 * (1 - y / SCREEN_HEIGHT))
            g = int(206 * (1 - y / SCREEN_HEIGHT))
            pygame.draw.line(background, (r, g, 235), (0, y), (SCREEN_WIDTH, y))
        return background

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer with Scrolling Camera")
    clock = pygame.time.Clock()

    # Load background
    background = load_background()

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Create player
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    all_sprites.add(player)

    # Create camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Create platforms with more vertical variety
    platform_data = [
        (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),     # Ground
        (0, 374, 84, 350),                             # Platform 1
        (110, 90, 250, 20),                            # Platform 2
        (930, 348, 400, 20),                           # Platform 3
        (605, 50, 100, 20),                            # Platform 4
        (300, -200, 200, 20),                          # Higher platform
        (700, -400, 250, 20),                          # Even higher platform
        (100, -600, 180, 20)                           # Highest platform
    ]
    for platform_info in platform_data:
        platform = Platform(*platform_info)
        all_sprites.add(platform)
        platforms.add(platform)

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update player
        player.update(platforms)

        # Update camera
        camera.update(player)

        # Clear the screen
        screen.blit(background, (0, 0))

        # Draw sprites with camera offset
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        pygame.display.flip()
        clock.tick(FPS)

    # Quit the game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()