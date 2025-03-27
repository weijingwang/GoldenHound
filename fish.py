import pygame
import random
import math

class Fish(pygame.sprite.Sprite):
    """Represents fish swimming across the screen."""
    COLOR_TINTS = [
        (255, 200, 200),   # Light Red
        (200, 255, 200),   # Light Green
        (200, 200, 255),   # Light Blue
        (255, 255, 200),   # Light Yellow
        (255, 200, 255)    # Light Magenta
    ]

    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Load fish animation frames
        base_frames = [
            asset_manager.load_image('assets/images/fish1.png'),
            asset_manager.load_image('assets/images/fish2.png')
        ]
        
        # Choose a random tint
        tint = random.choice(self.COLOR_TINTS)
        
        # Create tinted fish surfaces
        self.tinted_frames = self._create_tinted_frames(base_frames, tint)
        
        # Animation parameters
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # Lower is faster
        
        # Position
        self.rect = self.tinted_frames[0].get_rect()
        self.image = self.tinted_frames[0]
        self.rect.x = screen_width  # Start from right side
        self.start_y = random.randint(0, screen_height - self.rect.height)
        self.rect.y = self.start_y
        
        # Movement
        self.speed = random.randint(2, 5)
        self.frequency = random.uniform(0.005, 0.02)  # Random sine frequency
        self.amplitude = random.randint(10, 30)  # Amplitude of sine wave

    def _create_tinted_frames(self, base_frames, tint):
        """
        Create tinted fish frames.
        
        Args:
            base_frames (list): List of base fish frames
            tint (tuple): RGB color tint
        
        Returns:
            list: Tinted fish frames
        """
        tinted_frames = []
        for frame in base_frames:
            tinted_frame = frame.copy()
            for x in range(tinted_frame.get_width()):
                for y in range(tinted_frame.get_height()):
                    pixel = tinted_frame.get_at((x, y))
                    if pixel[3] > 0:  # If pixel is not transparent
                        # Blend pixel color with tint
                        new_color = tuple(
                            min(pixel[i] * tint[i] / 255, 255) 
                            for i in range(3)
                        ) + (pixel[3],)
                        tinted_frame.set_at((x, y), new_color)
            tinted_frames.append(tinted_frame)
        return tinted_frames

    def update(self):
        """Update fish animation and movement."""
        # Animate
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.tinted_frames)
            self.image = self.tinted_frames[self.current_frame]
        
        # Move left
        self.rect.x -= self.speed
        
        # Apply vertical sine wave movement
        time = pygame.time.get_ticks()  # Get elapsed time
        self.rect.y = self.start_y + int(self.amplitude * math.sin(time * self.frequency))
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()
