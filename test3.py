import pygame
import sys
import math
import random

class AssetManager:
    """Manages loading and caching of game assets."""
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def load_image(self, path, convert=True):
        """Load and cache an image."""
        if path not in self.images:
            image = pygame.image.load(path)
            self.images[path] = image.convert_alpha() if convert else image
        return self.images[path]

    def load_sound(self, path, volume=1.0):
        """Load and cache a sound."""
        if path not in self.sounds:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.sounds[path] = sound
        return self.sounds[path]

class Rock(pygame.sprite.Sprite):
    """Represents rocks moving across the screen."""
    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Random rock variations
        rock_images = [
            'assets/images/rock1.png',
            'assets/images/rock2.png',
            'assets/images/rock3.png'
        ]
        
        # Load a random rock image
        self.image = asset_manager.load_image(random.choice(rock_images))
        
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
        self.speed = 3

    def update(self):
        """Update rock movement."""
        # Move left
        self.rect.x -= self.speed
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, asset_manager, x, y):
        super().__init__()
        
        # Load animation frames
        self.animation_frames = [
            asset_manager.load_image(f'assets/images/player{i}.png') 
            for i in range(1, 8)
        ]
        
        # Load special state images and sounds
        self.eating_image = asset_manager.load_image("assets/images/player_eat.png")
        self.eat_sound = asset_manager.load_sound("assets/sounds/CLICK.ogg", 0.2)
        self.move_sound = asset_manager.load_sound("assets/sounds/swim.ogg", 0.05)

        # Animation and state management
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        
        # Eating state
        self.is_eating = False
        self.eating_timer = 0
        self.eating_duration = 20

        # Swimming bob parameters
        self.bob_timer = 0
        self.bob_amplitude = 5
        self.bob_frequency = 3
        
        # Player setup
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.original_y = y
        
        # Movement attributes
        self.speed = 5
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        self.sound_playing = False
        
        # Score
        self.score = 0

    def handle_input(self, rocks):
        """Handle player input and movement with rock collision check."""
        keys = pygame.key.get_pressed()
        
        # Backup current position
        old_x, old_y = self.rect.x, self.rect.y
        
        # Reset velocities
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        
        # WASD Movement with collision detection
        movement_map = {
            pygame.K_w: (0, -self.speed),
            pygame.K_s: (0, self.speed),
            pygame.K_a: (-self.speed, 0),
            pygame.K_d: (self.speed, 0)
        }
        
        for key, (dx, dy) in movement_map.items():
            if keys[key]:
                # Tentative move
                self.rect.x += dx
                self.rect.y += dy
                
                # Check for collisions
                collision = pygame.sprite.spritecollideany(self, rocks)
                
                if collision:
                    # Revert position if collision detected
                    self.rect.x = old_x
                    self.rect.y = old_y
                else:
                    # Move is valid
                    self.velocity_x = dx
                    self.velocity_y = dy
                    self.is_moving = True

        # Manage sound playback
        self._manage_movement_sound()

    def _manage_movement_sound(self):
        """Manage swimming sound based on movement state."""
        if self.is_moving:
            if not self.sound_playing:
                self.move_sound.play(-1, fade_ms=200)
                self.sound_playing = True
        else:
            self.move_sound.fadeout(200)
            self.sound_playing = False

    def animate(self):
        """Handle player animation."""
        if self.is_eating:
            self.image = self.eating_image
            return 
        
        self.animation_timer += 1
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames) if self.is_moving else 0
            self.image = self.animation_frames[self.current_frame]

    def swimming_bob(self):
        """Create a swimming bob effect."""
        if not self.is_moving:
            self.bob_timer += self.bob_frequency
            bob_offset = math.sin(self.bob_timer * 0.1) * self.bob_amplitude
            self.rect.y = self.original_y + bob_offset
        else:
            self.rect.y = self.original_y
            self.bob_timer = 0

    def update(self, rocks):
        """Update player state."""
        self.handle_input(rocks)
        
        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.original_y = self.rect.y

        # Handle eating animation
        if self.is_eating:
            self.eating_timer -= 1
            if self.eating_timer <= 0:
                self.is_eating = False

        self.animate()
        self.swimming_bob()

class SwimmingGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Screen setup
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Swimming Game")
        
        # Asset management
        self.asset_manager = AssetManager()
        
        # Game objects
        self.clock = pygame.time.Clock()
        self.player = Player(self.asset_manager, self.screen_width // 2, self.screen_height // 2)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group(self.player)
        self.fish_group = pygame.sprite.Group()
        self.rocks_group = pygame.sprite.Group()
        
        # Game state
        self.fish_spawn_timer = 0
        self.fish_spawn_delay = 60
        self.rock_spawn_timer = 0
        self.rock_spawn_delay = 200  # Less frequent rock spawning
        
        # Font for score
        self.font = pygame.font.Font(None, 36)
        
        # Background music
        self._setup_background_music()

    def _setup_background_music(self):
        """Set up and play background music."""
        pygame.mixer.music.load("assets/sounds/pastoral_cut.ogg")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Spawn fish and rocks
            self._spawn_fish()
            self._spawn_rocks()
            
            # Update game state
            self.player.update(self.rocks_group)
            self.fish_group.update()
            self.rocks_group.update()
            
            # Check for fish collisions
            self._handle_fish_collisions()
            
            # Draw game state
            self._draw()
            
            # Cap frame rate
            self.clock.tick(60)
        
        # Clean up
        self._quit()

    def _spawn_rocks(self):
        """Spawn rocks at intervals."""
        self.rock_spawn_timer += 1
        if self.rock_spawn_timer >= self.rock_spawn_delay:
            new_rock = Rock(self.asset_manager, self.screen_width, self.screen_height)
            self.rocks_group.add(new_rock)
            self.all_sprites.add(new_rock)
            self.rock_spawn_timer = 0

    def _spawn_fish(self):
        """Spawn fish at intervals."""
        self.fish_spawn_timer += 1
        if self.fish_spawn_timer >= self.fish_spawn_delay:
            new_fish = Fish(self.asset_manager, self.screen_width, self.screen_height)
            self.fish_group.add(new_fish)
            self.all_sprites.add(new_fish)
            self.fish_spawn_timer = 0

    def _handle_fish_collisions(self):
        """Handle player eating fish."""
        fish_eaten = pygame.sprite.spritecollide(self.player, self.fish_group, True)
        if fish_eaten:
            self.player.eat_sound.play()
            self.player.score += len(fish_eaten)
            self.player.is_eating = True
            self.player.eating_timer = self.player.eating_duration

    def _draw(self):
        """Draw game elements."""
        self.screen.fill((135, 206, 235))  # Sky blue background
        self.all_sprites.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.player.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        
        # Update display
        pygame.display.flip()

    def _quit(self):
        """Properly quit the game."""
        pygame.quit()
        sys.exit()

class Fish(pygame.sprite.Sprite):
    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Load fish animation frames
        base_frames = [
            asset_manager.load_image('assets/images/fish1.png'),
            asset_manager.load_image('assets/images/fish2.png')
        ]
        
        # Color tints
        color_tints = [
            (255, 200, 200),   # Light Red
            (200, 255, 200),   # Light Green
            (200, 200, 255),   # Light Blue
            (255, 255, 200),   # Light Yellow
            (255, 200, 255)    # Light Magenta
        ]
        
        # Choose a random tint
        tint = random.choice(color_tints)
        
        # Create tinted fish surfaces
        self.tinted_frames = []
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
            self.tinted_frames.append(tinted_frame)
        
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

    def update(self):
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

def main():
    game = SwimmingGame()
    game.run()

if __name__ == "__main__":
    main()