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
        
        # Load fish animation frames
        self.base_frames = [
            asset_manager.load_image('assets/images/rock1.png'),
            asset_manager.load_image('assets/images/rock2.png')
        ]
        self.image = self.base_frames[0]
        # Animation parameters
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # Lower is faster

        # Randomize rock size slightly
        scale = 0.5 #random.uniform(0.7, 1.3)
        original_size = self.image.get_size()
        new_size =  (int(original_size[0] * scale), int(original_size[1] * scale))
        self.image = pygame.transform.scale(self.image, new_size)
        
        # Position
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.y = random.randint(0, screen_height - self.rect.height)
        
        # Movement
        self.speed = 5



    def update(self):
        """Update rock animation and movement."""
        # Animate
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1)  % len(self.base_frames)
            self.image = self.base_frames[self.current_frame]
        
        # Move left
        self.rect.x -= self.speed
        
        # Apply vertical sine wave movement
        time = pygame.time.get_ticks()  # Get elapsed time
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()