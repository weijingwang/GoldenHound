import pygame
import sys
import math
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load animation frames
        self.animation_frames = []
        for i in range(1, 8):
            frame = pygame.image.load(f'assets/images/player{i}.png').convert_alpha()
            self.animation_frames.append(frame)

        # Load eating image
        self.eating_image = pygame.image.load("assets/images/player_eat.png").convert_alpha()

        # Load eating sound
        self.eat_sound = pygame.mixer.Sound("assets/sounds/CLICK.ogg")  # Ensure the file exists
        self.eat_sound.set_volume(0.2)  # Adjust volume if needed


        # Load movement sound
        self.move_sound = pygame.mixer.Sound("assets/sounds/swim.ogg")  # Ensure the file exists
        self.move_sound.set_volume(0.05)  # Adjust volume if needed
        self.sound_playing = False

        # Initial state
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Lower is faster
        
        # Eating state
        self.is_eating = False
        self.eating_timer = 0
        self.eating_duration = 20  # Number of frames the eating image stays


        # Swimming bob parameters
        self.bob_timer = 0
        self.bob_amplitude = 5  # Vertical bob distance
        self.bob_frequency = 3  # Speed of bobbing
        
        # Player attributes
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect()
        self.original_y = y  # Store the original y position
        self.rect.x = x
        self.rect.y = y
        
        # Movement attributes
        self.speed = 5
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        
        # Score
        self.score = 0

    def handle_input(self):
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Reset velocities
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Track if player is moving
        self.is_moving = False
        
        # WASD Movement
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
            self.is_moving = True
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.is_moving = True
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.is_moving = True
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.is_moving = True

        # Manage sound playback
        if self.is_moving:
            print('sadf')
            if not self.sound_playing:
                self.move_sound.play(-1, fade_ms=200)  # Loop indefinitely
                self.sound_playing = True
                print('move')
        else:
            self.move_sound.fadeout(200)
            self.sound_playing = False

    def animate(self):
        if self.is_eating:
            self.image = self.eating_image  # Show eating image
            return 
        # Increment animation timer
        self.animation_timer += 1
        
        # Change frame based on timer
        if self.animation_timer >= self.animation_speed:
            # Reset timer
            self.animation_timer = 0
            
            # Move to next frame if moving
            if self.is_moving:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            else:
                # Stay on first frame when idle
                self.current_frame = 0
            
            # Update image
            self.image = self.animation_frames[self.current_frame]

    def swimming_bob(self):
        # Only bob when not moving
        if not self.is_moving:
            # Increment bob timer
            self.bob_timer += self.bob_frequency
            
            # Calculate vertical offset using sine wave
            bob_offset = math.sin(self.bob_timer * 0.1) * self.bob_amplitude
            
            # Update y position with bob
            self.rect.y = self.original_y + bob_offset
        else:
            # Reset to original position when moving
            self.rect.y = self.original_y
            self.bob_timer = 0

    def update(self):
        # Handle input
        self.handle_input()
        
        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Update original y for bobbing
        self.original_y = self.rect.y

        # Handle eating animation timing
        if self.is_eating:
            self.eating_timer -= 1
            if self.eating_timer <= 0:
                self.is_eating = False  # Return to normal animation

        
        # Animate and bob
        self.animate()
        self.swimming_bob()

import pygame
import random
import math

class Fish(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        
        # Random fish colors
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255)   # Magenta
        ]
        
        # Create a simple colored fish surface
        self.image = pygame.Surface((30, 15), pygame.SRCALPHA)
        color = random.choice(colors)
        pygame.draw.polygon(self.image, color, 
            [(0, 7), (20, 0), (30, 7), (20, 15)])
        
        # Position
        self.rect = self.image.get_rect()
        self.rect.x = screen_width  # Start from right side
        self.start_y = random.randint(0, screen_height - self.rect.height)
        
        # Movement
        self.speed = random.randint(2, 5)
        self.frequency = random.uniform(0.005, 0.02)  # Random sine frequency
        self.amplitude = random.randint(10, 30)  # Amplitude of sine wave

    def update(self):
        # Move left
        self.rect.x -= self.speed
        
        # Apply vertical sine wave movement
        time = pygame.time.get_ticks()  # Get elapsed time
        self.rect.y = self.start_y + int(self.amplitude * math.sin(time * self.frequency))
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()


def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize the mixer module
    pygame.mixer.init()

    # Load and play background music
    pygame.mixer.music.load("assets/sounds/pastoral_cut.ogg")  # Change to your BGM file
    pygame.mixer.music.set_volume(0.3)  # Adjust volume (0.0 to 1.0)
    pygame.mixer.music.play(-1)  # Loop indefinitely


    # Screen setup
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Swimming Game")
    
    # Clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create player
    player = Player(screen_width // 2, screen_height // 2)
    
    # Sprite groups
    all_sprites = pygame.sprite.Group(player)
    fish_group = pygame.sprite.Group()
    
    # Fish spawn timer
    fish_spawn_timer = 0
    fish_spawn_delay = 60  # Frames between fish spawns
    
    # Font for score
    font = pygame.font.Font(None, 36)
    
    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Spawn fish periodically
        fish_spawn_timer += 1
        if fish_spawn_timer >= fish_spawn_delay:
            new_fish = Fish(screen_width, screen_height)
            fish_group.add(new_fish)
            all_sprites.add(new_fish)
            fish_spawn_timer = 0
        
        # Update
        all_sprites.update()
        
        # Check for fish collisions
        fish_eaten = pygame.sprite.spritecollide(player, fish_group, True)
        if fish_eaten:
            player.eat_sound.play()
            player.score += len(fish_eaten)
            player.is_eating = True
            player.eating_timer = player.eating_duration  # Set timer for eating state
        
        # Draw
        screen.fill((135, 206, 235))  # Sky blue background to simulate water
        all_sprites.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        
        # Refresh display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()