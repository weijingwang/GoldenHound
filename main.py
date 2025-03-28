import pygame
import sys
import math
import random

# Assuming these are imported from separate files as in the original code
from fish import Fish
from utils import AssetManager, PerlinNoiseOverlay
from player import Player
from rocks import Rock
from bird import Bird
from miner import Miner

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
        self.player = Player(self.asset_manager, self.screen_width // 2, self.screen_height // 2, self.screen_width, self.screen_height)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group(self.player)
        self.fish_group = pygame.sprite.Group()
        self.rocks_group = pygame.sprite.Group()
        self.miner_group = pygame.sprite.Group()
        
        # Level system parameters
        self._init_level_system()
        
        # Game state parameters
        self._init_game_parameters()
        
        # Load game assets
        self._load_game_assets()
        
        # Setup background
        self.noise_overlay = PerlinNoiseOverlay(self.screen_width, self.screen_height)
        
        # Death screen font
        self.death_font_large = pygame.font.Font(None, 72)
        self.death_font_small = pygame.font.Font(None, 48)

    def _init_level_system(self):
        """Initialize level progression system."""
        self.current_level = 1
        self.level_duration = 500  # 5 seconds per level at 60 FPS
        self.level_timer = 0
        self.level_progress = 0
        self.max_levels = 4
        
        # Level spawn configuration
        self.level_spawn_config = {
            1: {'fish': True, 'rocks': False, 'birds': False, 'miners': False},
            2: {'fish': True, 'rocks': True, 'birds': False, 'miners': False},
            3: {'fish': True, 'rocks': True, 'birds': True, 'miners': False},
            4: {'fish': True, 'rocks': True, 'birds': True, 'miners': True}
        }

    def _init_game_parameters(self):
        """Initialize game state parameters."""
        # Spawn timers
        self.fish_spawn_timer = 0
        self.fish_spawn_delay = 60
        self.rock_spawn_timer = 0
        self.rock_spawn_delay = 100

        # Add bird group
        self.bird_group = pygame.sprite.Group()
        
        # Bird spawn parameters
        self.bird_spawn_timer = 0
        self.bird_spawn_delay = 500  # Infrequent bird spawns
        
        # Add miner spawn parameters
        self.miner_spawn_timer = 0
        self.miner_spawn_delay = 300  # Adjust spawn rate as needed
        
        # Miner hit cooldown to prevent multiple hits at once
        self.miner_hit_cooldown = 0

        # Hunger system
        self.max_hunger = 10  # 10 half-hearts
        self.current_hunger = self.max_hunger
        self.hunger_decrease_rate = 0.1
        self.hunger_decrease_timer = 0
        self.hunger_decrease_interval = 100
        self.hunger_replenish_amount = 2
        
        # Heart animation
        self.heart_jiggle_time = 0
        
        # Game state
        self.game_over = False

    def _update_level_progression(self):
        """Manage level progression."""
        # Increment level timer
        self.level_timer += 1

        # Calculate progress percentage
        self.level_progress = min(100, (self.level_timer / self.level_duration) * 100)

        # Check if level is complete
        if self.level_timer >= self.level_duration:
            if self.current_level < self.max_levels:
                self.current_level += 1
                self.level_timer = 0
                self.level_progress = 0
            else:
                # Stop the game when the max level is reached
                self.game_over = True


    def _spawn_elements(self):
        """Spawn game elements based on current level."""
        current_config = self.level_spawn_config[self.current_level]
        
        # Spawn fish (always active)
        self._spawn_fish()
        
        # Conditional spawns based on current level
        if current_config['rocks']:
            self._spawn_rocks()
        
        if current_config['birds']:
            self._spawn_birds()
        
        if current_config['miners']:
            self._spawn_miners()

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
            if not self.game_over:
                game_continues = self._update_game_state()
                if not game_continues:
                    self.game_over = True
                
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
            
            # Restart game on death screen
            if self.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._restart_game()
                elif event.key == pygame.K_q:
                    return False
        return True
    
    def _restart_game(self):
        """Restart the game after death."""
        # Reset game parameters
        self._init_game_parameters()
        
        # Reset level system
        self._init_level_system()
        
        # Reset player
        self.player = Player(self.asset_manager, self.screen_width // 2, self.screen_height // 2, self.screen_width, self.screen_height)
        
        # Clear sprite groups
        self.all_sprites.empty()
        self.fish_group.empty()
        self.rocks_group.empty()
        self.bird_group.empty()
        self.miner_group.empty()
        
        # Add player back to sprite groups
        self.all_sprites.add(self.player)
        
        # Reset game over state
        self.game_over = False

    def _spawn_birds(self):
        """Spawn birds at intervals."""
        self.bird_spawn_timer += 1
        if self.bird_spawn_timer >= self.bird_spawn_delay:
            new_bird = Bird(self.asset_manager, self.screen_width, self.screen_height)
            self.bird_group.add(new_bird)
            self.all_sprites.add(new_bird)
            self.bird_spawn_timer = 0

    def _spawn_miners(self):
        """Spawn miners at intervals."""
        self.miner_spawn_timer += 1
        print(f"Miner spawn timer: {self.miner_spawn_timer}, Delay: {self.miner_spawn_delay}")  # Debug print
        if self.miner_spawn_timer >= self.miner_spawn_delay:
            print("Spawning miner!")  # Debug print
            new_miner = Miner(self.asset_manager, self.screen_width, self.screen_height)
            self.miner_group.add(new_miner)
            self.all_sprites.add(new_miner)
            self.miner_spawn_timer = 0

    def _update_game_state(self):
        """Update all game state elements."""
        # If the game is already won, stop updates
        if self.game_over:
            return False

        # Update level progression
        self._update_level_progression()
        
        # Check if the player has reached the final level and completed it
        if self.current_level == self.max_levels and self.level_timer >= self.level_duration:
            self.game_over = True  # This now represents a win state
            return False
        
        # Spawn game elements
        self._spawn_elements()
        
        # Update game objects
        self.player.update(self.rocks_group)
        self.fish_group.update()
        self.rocks_group.update()
        
        # Update based on current level
        if self.current_level >= 3:
            self.bird_group.update(self.fish_group)
        
        if self.current_level == 4:
            self.miner_group.update()
        
        # Manage hit cooldown
        if self.miner_hit_cooldown > 0:
            self.miner_hit_cooldown -= 1
        
        # Handle interactions
        self._handle_fish_collisions()
        
        # Add miner collisions only in level 4
        if self.current_level == 4:
            self._handle_miner_collisions()
        
        # Check if player is trapped
        if self._check_player_trapped_by_rocks():
            return False
        
        # Update hunger
        if self.current_hunger <= 0:
            return False
        
        self._update_hunger()
        
        return True

    

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

    def _handle_miner_collisions(self):
        """Handle player collisions with miners."""
        # Only check for collisions if not in cooldown
        if self.miner_hit_cooldown <= 0:
            for miner in self.miner_group:
                if miner.check_collision(self.player):
                    # Lose one heart
                    self.current_hunger = max(0, self.current_hunger - 2)
                    
                    # Set hit cooldown to prevent rapid multiple hits
                    self.miner_hit_cooldown = 30  # Adjust as needed for balance
                    
                    # Optional: Add hit sound
                    # You might want to add a hit sound to your asset manager
                    # self.hit_sound.play()
                    break

    def _check_player_trapped_by_rocks(self):
        """
        Check if player is trapped between a rock and the left screen edge.
        
        Returns:
            bool: True if player is trapped, False otherwise
        """
        # Check if player is at the left edge of the screen
        if self.player.rect.left <= 0:
            # Find rocks touching the player's left side
            for rock in self.rocks_group:
                if self.player.rect.colliderect(rock.rect) and \
                   rock.rect.right >= self.player.rect.left and \
                   rock.rect.left <= self.player.rect.left:
                    return True
        return False
    
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
    
    def _draw_level_progress(self):
        """Draw level progression indicator with continuous progress."""
        # Progress bar settings
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = 10
        
        # Background bar
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
        
        # Calculate progress segment width
        total_segments = self.max_levels  # 4 segments between 5 dots
        level_segment_width = bar_width / total_segments
        
        # Compute overall progress fraction
        total_progress = min(self.current_level - 1 + (self.level_progress / 100), total_segments)
        accumulated_progress_width = total_progress * level_segment_width  # Ensure max is bar_width
        
        # Draw accumulated green progress
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, accumulated_progress_width, bar_height))
        
        # Level dots
        dot_radius = 10
        
        for i in range(total_segments + 1):  # 5 dots total
            dot_x = bar_x + i * level_segment_width
            
            # Determine dot color based on progress
            if total_progress >= i:
                dot_color = (0, 0, 255)  # Blue for reached dots
            else:
                dot_color = (100, 100, 100)  # Gray for future dots
            
            pygame.draw.circle(self.screen, dot_color, (int(dot_x), bar_y + bar_height // 2), dot_radius)

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

    def _draw_win_screen(self):
        """Display the win screen."""
        win_text = self.death_font_large.render("You Win!", True, (255, 215, 0))  # Gold color
        restart_text = self.death_font_small.render("Press R to Restart or Q to Quit", True, (255, 255, 255))

        self.screen.blit(win_text, (self.screen_width // 2 - win_text.get_width() // 2, self.screen_height // 3))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, self.screen_height // 2))

    def _draw(self):
        """Draw game elements."""
        # Background
        self.screen.fill((135, 206, 235))  # Sky blue 
        noise_surface = self.noise_overlay.generate()
        self.screen.blit(noise_surface, (0, 0))

        if not self.game_over:
            # Draw sprites
            self.all_sprites.draw(self.screen)
            
            # Draw UI elements
            self._draw_ui()
        else:

            # If the player won, show the win screen
            if self.current_level == self.max_levels and self.level_timer >= self.level_duration:
                self._draw_win_screen()
            else:
                self._draw_death_screen()
        
        # Update display
        self.noise_overlay.update()
        pygame.display.flip()

    def _draw_death_screen(self):
        """Draw game over screen."""
        # Darken the screen
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.death_font_large.render("GAME OVER", True, (255, 0, 0))
        score_text = self.death_font_small.render(f"Score: {self.player.score}", True, (255, 255, 255))
        restart_text = self.death_font_small.render("Press 'R' to Restart", True, (255, 255, 255))
        quit_text = self.death_font_small.render("Press 'Q' to Quit", True, (255, 255, 255))
        
        # Center text
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 100))
        quit_rect = quit_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 150))
        
        # Blit text
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(quit_text, quit_rect)

    def _draw_ui(self):
        """Draw user interface elements."""
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        
        # Level text
        level_text = self.font.render(f"Level: {self.current_level}", True, (0, 0, 0))
        self.screen.blit(level_text, (10, 50))
        
        # Hunger bar
        self._draw_heart_hunger_bar()
        
        # Level progress bar
        self._draw_level_progress()
        
        # FPS display
        fps = self.clock.get_fps()
        pygame.display.set_caption(f"Downstream. FPS: {fps:.2f}")

def main():
    """Entry point for the game."""
    game = SwimmingGame()
    game.run()

if __name__ == "__main__":
    main()