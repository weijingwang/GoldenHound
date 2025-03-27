import pygame
import random

class Rock(pygame.sprite.Sprite):
    """Represents rocks moving across the screen."""
    ROCK_IMAGES = [
        'assets/images/rock1.png',
        'assets/images/rock2.png',
        'assets/images/rock3.png'
    ]

    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Load a random rock image
        self.image = asset_manager.load_image(random.choice(self.ROCK_IMAGES))
        
        # Randomize rock size slightly
        scale = random.uniform(0.7, 1.3)
        original_size = self.image.get_size()
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        self.image = pygame.transform.scale(self.image, new_size)
        
        # Position
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.y = random.randint(0, screen_height - self.rect.height)
        
        # Movement
        self.speed = random.randint(2, 4)

    def update(self):
        """Update rock movement."""
        # Move left
        self.rect.x -= self.speed
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()