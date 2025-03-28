import pygame
import random

class Miner(pygame.sprite.Sprite):
    """Represents an enemy Miner that moves from right to left."""
    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Load animation frames
        self.animation_frames = [
            asset_manager.load_image('assets/images/miner1.png'),
            asset_manager.load_image('assets/images/miner2.png')
        ]
        
        # Animation management
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # Controls animation speed
        
        # Spawn at a random vertical position on the right side of the screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        spawn_y = random.randint(0, screen_height - 300)  # Adjust 100 based on miner sprite height
        
        # Initial setup
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect(topleft=(screen_width, spawn_y))
        
        # Movement attributes
        self.speed = random.uniform(2, 4)  # Randomized speed for variety
        
        # Collision damage
        self.damage = 1

    def update(self):
        """
        Update miner's position and animation.
        Moves from right to left.
        """
        # Move left
        self.rect.x -= self.speed
        
        # Animate
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()

    def check_collision(self, player):
        """
        Check for collision with player and apply damage.
        
        Args:
            player (Player): The player sprite
        
        Returns:
            bool: True if collision occurred, False otherwise
        """
        if self.rect.colliderect(player.rect):
            # Damage the player
            self.kill()  # Remove miner after hitting player
            return True
        return False