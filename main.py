import pygame
import sys
from fish import *
from utils import *
from player import *
from rocks import *
from background import *

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
        pygame.display.set_caption("Pyweek 39 downstream")
        
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
        self.rock_spawn_delay = 100  # Less frequent rock spawning
        
        # Font for score
        self.font = pygame.font.Font(None, 36)
        
        # Background music
        self._setup_background_music()

        self.noise_overlay = PerlinNoiseOverlay(self.screen_width, self.screen_height)


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
        noise_surface = self.noise_overlay.generate()
        self.screen.blit(noise_surface, (0, 0))

        self.all_sprites.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.player.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        
        # Update display
        self.noise_overlay.update()

        # FPS show
        fps = self.clock.get_fps()
        # Update the window caption with the current FPS
        pygame.display.set_caption(f"Pyweek 39 downstream. FPS: {fps:.2f}")

        pygame.display.flip()

    def _quit(self):
        """Properly quit the game."""
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game."""
    # Get the FPS
    game = SwimmingGame()
    game.run()

if __name__ == "__main__":
    main()