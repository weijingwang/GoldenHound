import pygame
import math
import random

class Bird(pygame.sprite.Sprite):
    """Bird enemy that flies across the screen and eats fish."""
    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Load eagle image
        try:
            self.original_image = pygame.image.load("assets/images/eagle.png").convert_alpha()
            # Scale the image to an appropriate size
            # self.original_image = pygame.transform.scale(original_image, (100, 70))
            self.image = self.original_image.copy()
            self.width, self.height = self.image.get_size()
        except Exception as e:
            print(f"Error loading bird image: {e}")
            # Fallback to a colored rectangle if image fails
            self.original_image = pygame.Surface((100, 70), pygame.SRCALPHA)
            self.original_image.fill((139, 69, 19))  # Brown color
            self.image = self.original_image.copy()
            self.width, self.height = self.image.get_size()

        # eagle sound
        self.bird_sound = asset_manager.load_sound("assets/sounds/bird.ogg", 0.8)

        # Randomly choose entry side with offset to ensure completely off-screen
        entry_side = random.choice(['bottom', 'right', 'top'])
        
        # Set initial position based on entry side, ensuring fully off-screen
        if entry_side == 'bottom':
            self.rect = self.image.get_rect(midbottom=(screen_width + self.width, 
                                                       random.randint(-self.height, screen_height + self.height)))
            self.speed_x = -random.uniform(3, 6)
            self.speed_y = random.uniform(-1, 1)
        elif entry_side == 'right':
            self.rect = self.image.get_rect(midright=(screen_width + self.width, 
                                                      random.randint(-self.height, screen_height + self.height)))
            self.speed_x = -random.uniform(3, 6)
            self.speed_y = random.uniform(-1, 1)
        else:  # top
            self.rect = self.image.get_rect(midtop=(random.randint(-self.width, screen_width + self.width), 
                                                    -self.height))
            self.speed_x = random.uniform(-1, 1)
            self.speed_y = random.uniform(3, 6)
        
        # Bird tracking and behavior
        self.hunting = False
        self.target_fish = None
        self.eat_delay = 30  # Frames to stay over a fish
        self.eat_timer = 0

    def update(self, fish_group):
        """Update bird movement and fish hunting behavior."""
        if not self.hunting:
            # Calculate movement angle
            # Subtract 90 degrees to align the top of the image with movement direction
            movement_angle = math.degrees(math.atan2(-self.speed_y, self.speed_x)) - 90
            
            # Rotate the image based on movement direction
            self.image = pygame.transform.rotate(self.original_image, movement_angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            
            # Normal flight movement
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            
            # Check for potential fish to hunt
            for fish in fish_group:
                if self.rect.colliderect(fish.rect):
                    self.hunting = True
                    self.target_fish = fish
                    break
        
        if self.hunting and self.target_fish:
            # Track the fish
            self.rect.centerx = self.target_fish.rect.centerx
            self.rect.centery = self.target_fish.rect.centery
            
            # Eat timer
            self.eat_timer += 1
            if self.eat_timer >= self.eat_delay:
                # Remove the fish
                self.bird_sound.play()
                self.target_fish.kill()
                self.target_fish = None
                self.hunting = False
                self.eat_timer = 0