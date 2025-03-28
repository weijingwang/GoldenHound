import pygame
import random

class GoldPiece(pygame.sprite.Sprite):
    """Represents a collectible gold piece in the game."""
    def __init__(self, asset_manager, screen_width, screen_height):
        """
        Initialize a gold piece sprite.
        
        Args:
            asset_manager (AssetManager): Manages game assets
            screen_width (int): Width of the game screen
            screen_height (int): Height of the game screen
        """
        super().__init__()
        


        # Load gold piece image (you'll need to add this to your asset manager)
        try:
            self.image = asset_manager.load_image("gold_piece.png")  # You'll need to create this image
            self.image = pygame.transform.scale(self.image, (30, 30))  # Adjust size as needed
        except:
            # Fallback if image loading fails
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 215, 0))  # Gold color
        
        self.rect = self.image.get_rect()
        
        # Spawn on the left side of the screen
        self.rect.x = 0
        
        # Random vertical position
        self.rect.y = random.randint(100, screen_height - 100)
        
        # Movement parameters
        self.speed = random.uniform(2, 5)
        
        # Screen dimensions for boundary checking
        self.screen_width = screen_width
        
    def update(self):
        """Update gold piece movement."""
        # Move right
        self.rect.x += self.speed
        
        # Remove if off screen
        if self.rect.left > self.screen_width:
            self.kill()