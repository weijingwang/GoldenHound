import pygame
import sys
import math
from typing import Optional

# Assuming these are imported from separate files as in the original code
from fish import Fish
from utils import AssetManager, PerlinNoiseOverlay
from player import Player
from rocks import Rock

class SwimmingGame:
    """Main game class managing game state and loop."""
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Screen setup
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Downstream")
        
        # Asset management
        self.asset_manager = AssetManager()
        
        # Game objects
        self.clock = pygame.time.Clock()
        self.player = Player(self.asset_manager, self.screen_width // 2, self.screen_height // 2)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group(self.player)
        self.fish_group = pygame.sprite.Group()
        self.rocks_group = pygame.sprite.Group()
        
        # Game state parameters
        self._init_game_parameters()
        
        # Load game assets
        self._load_game_assets()
        
        # Setup background
        self.noise_overlay = PerlinNoiseOverlay(self.screen_width, self.screen_height)

    def _init_game_parameters(self):
        """Initialize game state parameters."""
        # Spawn timers
        self.fish_spawn_timer = 0
        self.fish_spawn_delay = 60
        self.rock_spawn_timer = 0
        self.rock_spawn_delay = 100
        
        # Hunger system
        self.max_hunger = 10  # 10 half-hearts
        self.current_hunger = self.max_hunger
        self.hunger_decrease_rate = 0.1
        self.hunger_decrease_timer = 0
        self.hunger_decrease_interval = 180
        self.hunger_replenish_amount = 2
        
        # Heart animation
        self.heart_jiggle_time = 0

    def _load_game_assets(self):
        """Load game images and fonts."""
        # Heart images
        try:
            full_heart_sheet = pygame.image.load("assets/images/player6.png").convert_alpha()
            half_heart_sheet = pygame.image.load("assets/images/player_half.png").convert_alpha()
            
            # Heart image scaling
            heart_size = (50, 50)
            self.full_heart_image = self._process_heart_image(full_heart_sheet, heart_size)
            self.half_heart_image = self._process_heart_image(half_heart_sheet, heart_size)
            
            # Ghosted heart for empty states
            self.ghosted_heart = self.full_heart_image.copy()
            self.ghosted_heart.set_alpha(50)
        except Exception as e:
            print(f"Error loading heart images: {e}")
            self.full_heart_image = None
            self.half_heart_image = None
            self.ghosted_heart = None
        
        # Fonts and sound
        self.font = pygame.font.Font(None, 36)
        self._setup_background_music()

    def _process_heart_image(self, sheet: pygame.Surface, size: tuple) -> pygame.Surface:
        """Process heart image from sprite sheet."""
        heart_image = sheet.subsurface((0, 0, sheet.get_height(), sheet.get_height()))
        return pygame.transform.scale(heart_image, size)

    def _setup_background_music(self):
        """Set up and play background music."""
        try:
            pygame.mixer.music.load("assets/sounds/pastoral_cut.ogg")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error loading background music: {e}")

    def run(self):
        """Main game loop."""
        running = True
        while running:
            # Event handling
            running = self._handle_events()
            
            # Game updates
            self._update_game_state()
            
            # Drawing
            self._draw()
            
            # Cap frame rate
            self.clock.tick(60)
        
        # Clean up
        self._quit()

    def _handle_events(self) -> bool:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def _update_game_state(self):
        """Update all game state elements."""
        # Spawn game elements
        self._spawn_fish()
        self._spawn_rocks()
        
        # Update game objects
        self.player.update(self.rocks_group)
        self.fish_group.update()
        self.rocks_group.update()
        
        # Handle interactions
        self._handle_fish_collisions()
        
        # Update hunger
        self._update_hunger()
        
        # Check game over condition
        return self.current_hunger > 0

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
            
            # Replenish hunger
            self.current_hunger = min(self.max_hunger, self.current_hunger + self.hunger_replenish_amount * len(fish_eaten))

    def _calculate_heart_jiggle(self, heart_index: int) -> float:
        """Calculate jiggle offset for heart animation."""
        if not self.full_heart_image or not self.half_heart_image:
            return 0
        
        # Jiggle parameters
        hunger_percentage = self.current_hunger / self.max_hunger
        base_intensity = 5
        max_intensity = 10
        
        # Dynamic jiggle calculation
        intensity = max_intensity * (1 - hunger_percentage) + base_intensity
        jiggle_speed = 10 * (hunger_percentage + 0.2)
        phase_offset = heart_index * 0.5
        
        return math.sin(self.heart_jiggle_time / jiggle_speed + phase_offset) * intensity

    def _update_hunger(self):
        """Decrease hunger at discrete intervals."""
        self.hunger_decrease_timer += 1
        
        # Decrease hunger
        if self.hunger_decrease_timer >= self.hunger_decrease_interval:
            if self.current_hunger > 0:
                self.current_hunger -= 1
            self.hunger_decrease_timer = 0
        
        # Increment jiggle time for heart animation
        self.heart_jiggle_time += 1

    def _draw_heart_hunger_bar(self):
        """Draw hearts representing hunger with jiggle animation."""
        if not self.full_heart_image or not self.half_heart_image:
            return
        
        # Heart drawing parameters
        heart_spacing = 10
        start_x, start_y = 20, 50
        
        for i in range(self.max_hunger // 2):
            jiggle_offset = self._calculate_heart_jiggle(i)
            
            # Calculate heart positions
            heart_x = start_x + i * (self.full_heart_image.get_width() + heart_spacing)
            heart_y = start_y + jiggle_offset
            
            # Draw hearts based on current hunger
            if i < self.current_hunger / 2:
                if i < self.current_hunger // 2:
                    # Full hearts
                    self.screen.blit(self.full_heart_image, (heart_x, heart_y))
                elif self.current_hunger % 2 == 1:
                    # Half heart
                    self.screen.blit(self.ghosted_heart, (heart_x, heart_y))
                    self.screen.blit(self.half_heart_image, (heart_x, heart_y))
            else:
                self.screen.blit(self.ghosted_heart, (heart_x, heart_y))

    def _draw(self):
        """Draw game elements."""
        # Background
        self.screen.fill((135, 206, 235))  # Sky blue 
        noise_surface = self.noise_overlay.generate()
        self.screen.blit(noise_surface, (0, 0))

        # Draw sprites
        self.all_sprites.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Update display
        self.noise_overlay.update()
        pygame.display.flip()

    def _draw_ui(self):
        """Draw user interface elements."""
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        
        # Hunger bar
        self._draw_heart_hunger_bar()
        
        # FPS display
        fps = self.clock.get_fps()
        pygame.display.set_caption(f"Downstream. FPS: {fps:.2f}")

    def _quit(self):
        """Properly quit the game."""
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game."""
    game = SwimmingGame()
    game.run()

if __name__ == "__main__":
    main()