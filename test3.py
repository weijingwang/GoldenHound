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

    def handle_input(self):
        """Handle player input and movement."""
        keys = pygame.key.get_pressed()
        
        # Reset velocities
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        
        # WASD Movement
        movement_map = {
            pygame.K_w: (0, -self.speed),
            pygame.K_s: (0, self.speed),
            pygame.K_a: (-self.speed, 0),
            pygame.K_d: (self.speed, 0)
        }
        
        for key, (dx, dy) in movement_map.items():
            if keys[key]:
                self.velocity_x += dx
                self.velocity_y += dy
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

    def update(self):
        """Update player state."""
        self.handle_input()
        
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

class Fish(pygame.sprite.Sprite):
    def __init__(self, asset_manager, screen_width, screen_height):
        super().__init__()
        
        # Load and tint fish frames
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
        
        # Tint frames
        self.tinted_frames = self._tint_frames(base_frames, random.choice(color_tints))
        
        # Animation parameters
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10
        
        # Position and movement
        self.rect = self.tinted_frames[0].get_rect()
        self.image = self.tinted_frames[0]
        self.rect.x = screen_width
        self.start_y = random.randint(0, screen_height - self.rect.height)
        self.rect.y = self.start_y
        
        # Fish-specific movement
        self.speed = random.randint(2, 5)
        self.frequency = random.uniform(0.005, 0.02)
        self.amplitude = random.randint(10, 30)

    def _tint_frames(self, frames, tint):
        """Apply color tint to fish frames."""
        tinted_frames = []
        for frame in frames:
            tinted_frame = frame.copy()
            for x in range(tinted_frame.get_width()):
                for y in range(tinted_frame.get_height()):
                    pixel = tinted_frame.get_at((x, y))
                    if pixel[3] > 0:  # Non-transparent pixel
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
        
        # Move left with sine wave motion
        self.rect.x -= self.speed
        time = pygame.time.get_ticks()
        self.rect.y = self.start_y + int(self.amplitude * math.sin(time * self.frequency))
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()

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
        
        # Game state
        self.fish_spawn_timer = 0
        self.fish_spawn_delay = 60
        
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
            
            # Spawn fish
            self._spawn_fish()
            
            # Update game state
            self.all_sprites.update()
            
            # Check for fish collisions
            self._handle_fish_collisions()
            
            # Draw game state
            self._draw()
            
            # Cap frame rate
            self.clock.tick(60)
        
        # Clean up
        self._quit()

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

def main():
    game = SwimmingGame()
    game.run()

if __name__ == "__main__":
    main()