import pygame
import sys
import math
import random

# Assuming these are imported from separate files as in the original code
from fish import Fish
from utils import AssetManager, PerlinNoiseOverlay
from player import Player
from rocks import Rock

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
        
        # Death screen font
        self.death_font_large = pygame.font.Font(None, 72)
        self.death_font_small = pygame.font.Font(None, 48)

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
        
        # Hunger system
        self.max_hunger = 10  # 10 half-hearts
        self.current_hunger = self.max_hunger
        self.hunger_decrease_rate = 0.1
        self.hunger_decrease_timer = 0
        self.hunger_decrease_interval = 100#180
        self.hunger_replenish_amount = 2
        
        # Heart animation
        self.heart_jiggle_time = 0
        
        # Game state
        self.game_over = False

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
        
        # Reset player
        self.player = Player(self.asset_manager, self.screen_width // 2, self.screen_height // 2)
        
        # Clear sprite groups
        self.all_sprites.empty()
        self.fish_group.empty()
        self.rocks_group.empty()
        
        # Add player back to sprite groups
        self.all_sprites.add(self.player)
        # Clear bird group
        self.bird_group.empty()
        
        # Reset bird spawn timer
        self.bird_spawn_timer = 0
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

    def _update_game_state(self):
        """Update all game state elements."""
        # Spawn game elements
        self._spawn_fish()
        self._spawn_rocks()
        self._spawn_birds()
        
        # Update game objects
        self.player.update(self.rocks_group)
        self.fish_group.update()
        self.rocks_group.update()
        self.bird_group.update(self.fish_group)
        
        # Handle interactions
        self._handle_fish_collisions()
        
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

        if not self.game_over:
            # Draw sprites
            self.all_sprites.draw(self.screen)
            
            # Draw UI elements
            self._draw_ui()
        else:
            # Draw death screen
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