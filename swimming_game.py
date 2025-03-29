import pygame
import math
import sys
import random
from fish import Fish
from utils import AssetManager, PerlinNoiseOverlay
from player import Player
from rocks import Rock
from bird import Bird
from miner import Miner
from gold import GoldPiece

class SwimmingGame:
    """Main game class managing game state and loop."""
    def __init__(self):

        
        # Screen setup
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
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
        self.max_levels = 4
    
        # Level gold piece requirements
        self.level_gold_requirements = {
            1: 5,   # 10 gold pieces to reach level 2
            2: 10,   # 20 gold pieces to reach level 3
            3: 15,   # 30 gold pieces to reach level 4
            4: 20    # 40 gold pieces to win the game
        }
            
        # Level spawn configuration
        self.level_spawn_config = {
            1: {'fish': True, 'rocks': False, 'birds': True, 'miners': False},
            2: {'fish': True, 'rocks': True, 'birds': True, 'miners': False},
            3: {'fish': True, 'rocks': True, 'birds': True, 'miners': True},
            4: {'fish': True, 'rocks': True, 'birds': True, 'miners': True}
        }


    def _update_level_progression(self):
        """Manage level progression."""
        # Increment level timer
        self.level_timer += 1

        # Calculate progress percentage
        self.level_progress = min(100, (self.level_timer / self.level_duration) * 100)

        # Check if level is complete
        if self.level_timer >= self.level_duration:
            print('asdfasd')
            if self.current_level < self.max_levels:
                self.current_level += 1
                self.level_timer = 0
                self.level_progress = 0
            else:
                # Stop the game when the max level is reached
                self.game_over = True


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

    def _restart_game(self):
        """Restart the game while preserving level and minimum gold pieces."""
        # Preserve current level and minimum gold for that level
        preserved_level = self.current_level
        preserved_gold = self.level_gold_requirements.get(preserved_level - 1, 0)
        
        # Reset game parameters
        self._init_game_parameters()
        
        # Restore level and gold pieces
        self.current_level = preserved_level
        self.collected_gold_pieces = preserved_gold
        
        # Reset player
        self.player = Player(self.asset_manager, self.screen_width // 2, self.screen_height // 2, self.screen_width, self.screen_height, self.current_level)

        # Clear sprite groups
        self.all_sprites.empty()
        self.fish_group.empty()
        self.rocks_group.empty()
        self.bird_group.empty()
        self.miner_group.empty()
        self.gold_pieces_group.empty()
        
        # Add player back to sprite groups
        self.all_sprites.add(self.player)
        
        # Reset game over state
        self.game_over = False

    def _update_game_state(self):
        """Update all game state elements."""
        # If the game is already won, stop updates
        if self.game_over:
            return False

        # Spawn game elements
        self._spawn_elements()
        
        # Update game objects
        self.player.update(self.rocks_group)
        self.fish_group.update()
        self.rocks_group.update()
        self.miner_group.update()
        self.bird_group.update(self.fish_group)
        self._handle_miner_collisions()

        # Manage hit cooldown
        if self.miner_hit_cooldown > 0:
            self.miner_hit_cooldown -= 1
        
        # Handle interactions
        self._handle_fish_collisions()
        
        # Check if player is trapped
        if self._check_player_trapped_by_rocks():
            return False
        
        # Update gold piece group
        self.gold_pieces_group.update()
        
        # Handle gold piece collection
        self._handle_gold_piece_collection()
        
        # Check for level progression via gold piece collection
        self._check_level_progression()
        
        # Check hunger
        if self.current_hunger <= 0:
            return False
        
        self._update_hunger()
        
        return True

    def _check_level_progression(self):
        """Check and handle level progression based on collected gold pieces."""
        # Check if we've collected enough gold pieces to advance
        if self.current_level < self.max_levels:
            if self.collected_gold_pieces >= self.level_gold_requirements[self.current_level]:
                # Advance to next level
                self.player.set_level(self.asset_manager, self.current_level +1)

                self.current_level += 1
        else:
            # Check if we've collected enough gold pieces to win the game
            if self.collected_gold_pieces >= self.level_gold_requirements[self.current_level]:
                self.game_over = True  # Win condition


    def _progress_to_next_level(self):
        """Progress to the next level when gold pieces are collected."""
        if self.current_level < self.max_levels:
            self.current_level += 1
            self.collected_gold_pieces = 0  # Reset for next level
        else:
            # Game completed
            self.game_over = True


    def _draw_win_screen(self):
        """Display the win screen."""
        win_text = self.death_font_large.render("Congratulations! You Win!", True, (255, 215, 0))  # Gold color
        score_text = self.death_font_small.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
        restart_text = self.death_font_small.render("Press R to Restart or Q to Quit", True, (255, 255, 255))

        self.screen.blit(win_text, (self.screen_width // 2 - win_text.get_width() // 2, self.screen_height // 3))
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, self.screen_height // 2))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, self.screen_height // 2 + 50))
        
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
            # If the player won (reached max level and collected required gold)
            if self.current_level == self.max_levels and self.collected_gold_pieces >= self.level_gold_requirements[self.current_level]:
                # Start the fade effect
                if not self.fading:
                    self.fading = True
                
                # Draw sprites and UI for a smooth transition
                self.all_sprites.draw(self.screen)
                self._draw_ui()
                
                # Draw the fade overlay
                self.fade_surface.set_alpha(self.fade_alpha)
                self.screen.blit(self.fade_surface, (0, 0))
                
                # Check if fade is complete
                if self._update_fade():
                    self.player.stop_sound()
                    return "end"
            else:
                self._draw_death_screen()
        
        # Update display
        self.noise_overlay.update()
        pygame.display.flip()
        
        # Default return if we didn't transition to a new state
        return None



    def _update_fade(self):
        """Update the fade effect after winning."""
        if self.fading:
            # Increase alpha to make the screen darker
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
            
            # Start fading music when screen begins to darken
            if not self.music_fade_started and self.fade_alpha > 20:
                pygame.mixer.music.fadeout(2000)  # 3000ms = 3 seconds to fade out
                self.music_fade_started = True
            
            # Return True when fade is complete
            return self.fade_alpha >= 255
        return False

    def _init_game_parameters(self):
        """Initialize game state parameters."""
        
        # Add fade parameters
        self.fading = False
        self.fade_alpha = 0  # Start completely transparent
        self.fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.fade_surface.fill((0, 0, 0))  # Black surface for fading
        self.fade_speed = 3  # How quickly to fade (alpha increase per frame)
        self.music_fade_started = False

        # Gold piece collection
        self.gold_pieces_group = pygame.sprite.Group()
        self.gold_piece_spawn_timer = 0
        self.gold_piece_spawn_delay = 300  # Adjust spawning frequency
        self.collected_gold_pieces = 0
        self.gold_pieces_needed_for_level = 10  # Collect 10 gold pieces to progress
        
        # Replace level_timer with gold piece progression
        self.current_gold_pieces = 0

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
        
        # Spawn gold pieces
        self._spawn_gold_pieces()

    def _load_game_assets(self):
        """Load game images and fonts."""
        self.texture = pygame.image.load("assets/images/texture.png").convert_alpha()
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
        self.coin_sound = self.asset_manager.load_sound("assets/sounds/coins.ogg", 0.5)
        self.miner_sound = self.asset_manager.load_sound("assets/sounds/miner.ogg", 0.2)

        # self._setup_background_music()

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



    def _quit(self):
        pygame.quit()
        sys.exit()

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
    



    def _spawn_gold_pieces(self):
        """Spawn gold pieces at intervals."""
        self.gold_piece_spawn_timer += 1
        if self.gold_piece_spawn_timer >= self.gold_piece_spawn_delay:
            new_gold_piece = GoldPiece(self.asset_manager, self.screen_width, self.screen_height)
            self.gold_pieces_group.add(new_gold_piece)
            self.all_sprites.add(new_gold_piece)
            self.gold_piece_spawn_timer = 0

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
        # print(f"Miner spawn timer: {self.miner_spawn_timer}, Delay: {self.miner_spawn_delay}")  # Debug print
        if self.miner_spawn_timer >= self.miner_spawn_delay:
            # print("Spawning miner!")  # Debug print
            new_miner = Miner(self.asset_manager, self.screen_width, self.screen_height)
            self.miner_group.add(new_miner)
            self.all_sprites.add(new_miner)
            self.miner_spawn_timer = 0



    def _draw_death_screen(self):
        """Draw game over screen."""
        # Darken the screen
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.death_font_large.render("game over...", True, (255, 0, 0))
        score_text = self.death_font_small.render(f"Score: {self.player.score}", True, (255, 255, 255))
        restart_text = self.death_font_small.render("press R for restart", True, (255, 255, 255))
        quit_text = self.death_font_small.render("press q for quit", True, (255, 255, 255))
        
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
        """Draw user interface elements with updated positioning."""
        # UI Configuration
        ui_margin = 20
        text_color = (255, 255, 255)  # White text for better contrast
        shadow_color = (0, 0, 0)  # Black shadow for depth
        
        # Level in top left
        level_text = self.font.render(f"Level: {self.current_level}", True, text_color)
        level_shadow = self.font.render(f"Level: {self.current_level}", True, shadow_color)
        self.screen.blit(level_shadow, (ui_margin + 2, ui_margin + 2))
        self.screen.blit(level_text, (ui_margin, ui_margin))
        
        # Coins and level center top
        center_top_x = self.screen_width // 2
        center_top_y = ui_margin
        
        score_text = self.font.render(f"Score: {self.player.score}", True, text_color)
        score_shadow = self.font.render(f"Score: {self.player.score}", True, shadow_color)
        score_rect = score_text.get_rect(center=(center_top_x, center_top_y))
        
        self.screen.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
        self.screen.blit(score_text, score_rect)
        
        # Hunger bar center bottom
        self._draw_heart_hunger_bar_centered()
        
        # Level progress bar
        self._draw_level_progress_centered()

    def _draw_heart_hunger_bar_centered(self):
        """Draw heart hunger bar centered at the bottom of the screen."""
        if not self.full_heart_image or not self.half_heart_image:
            return
        
        # Calculate total width of hunger bar
        total_width = (self.full_heart_image.get_width() + 5) * (self.max_hunger // 2)
        
        # Starting position to center the hunger bar
        start_x = (self.screen_width - total_width) // 2
        start_y = self.screen_height - self.full_heart_image.get_height() - 80  # 20 pixels from bottom
        
        for i in range(self.max_hunger // 2):
            jiggle_offset = self._calculate_heart_jiggle(i)
            
            # Calculate heart positions
            heart_x = start_x + i * (self.full_heart_image.get_width() + 5)
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
                # Ghosted/empty hearts
                self.screen.blit(self.ghosted_heart, (heart_x, heart_y))

    def _draw_level_progress_centered(self):
        """Draw level progress bar centered near the bottom of the screen with texture over entire bar and glitter effects."""        
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height - 70  # Positioned above the hunger bar
        
        # Calculate current level's gold requirement
        current_level_requirement = self.level_gold_requirements[self.current_level]
        
        # Calculate gold piece collection progress
        progress_width = int((self.collected_gold_pieces / current_level_requirement) * bar_width)
        
        # Create a surface for the entire bar (background and progress)
        bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        
        # Draw the background (gray) part
        pygame.draw.rect(bar_surface, (100, 100, 100), pygame.Rect(0, 0, bar_width, bar_height), border_radius=10)
        
        # Draw the progress (gold) part
        if progress_width > 0:
            pygame.draw.rect(bar_surface, (255, 215, 0), pygame.Rect(0, 0, progress_width, bar_height), border_radius=10)
        
        # Apply texture to the entire bar
        texture_width, texture_height = self.texture.get_size()
        texture_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        
        # Tile the texture across the entire bar area
        for x in range(0, bar_width, texture_width):
            for y in range(0, bar_height, texture_height):
                texture_surface.blit(self.texture, (x, y))
        
        # Create a mask for the rounded corners
        mask_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), pygame.Rect(0, 0, bar_width, bar_height), border_radius=10)
        
        # Apply the mask to the texture (to respect rounded corners)
        texture_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Apply the textured mask to the bar
        bar_surface.blit(texture_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw the final bar to the screen
        self.screen.blit(bar_surface, (bar_x, bar_y))
        
        # Add glitter effect - only to the filled portion of the progress bar
        if not hasattr(self, 'glitter_particles'):
            # Initialize glitter particles the first time
            self.glitter_particles = []
            self.last_glitter_spawn = 0
        
        # Spawn new glitter particles periodically
        current_time = pygame.time.get_ticks()
        if current_time - self.last_glitter_spawn > 150:  # Spawn every 150ms (less frequent)
            self.last_glitter_spawn = current_time
            # Add 1-2 new particles (less particles)
            for _ in range(random.randint(1, 2)):
                if progress_width > 0:  # Only add particles if there's progress
                    particle_x = random.randint(bar_x, bar_x + progress_width)
                    particle_y = random.randint(bar_y, bar_y + bar_height)
                    particle_size = random.uniform(1.5, 2.5)
                    particle_color = random.choice([
                        (255, 255, 255),  # White
                        (255, 255, 200),  # Light yellow
                        (200, 255, 255),  # Light blue
                    ])
                    particle_life = random.randint(30, 60)  # Longer lifespan for smoother effect
                    
                    # Add consistent, gentle movement vectors
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0.1, 0.3)  # Much slower movement
                    
                    self.glitter_particles.append({
                        'x': particle_x,
                        'y': particle_y,
                        'size': particle_size,
                        'color': particle_color,
                        'life': particle_life,
                        'max_life': particle_life,
                        'vel_x': math.cos(angle) * speed,
                        'vel_y': math.sin(angle) * speed
                    })
        
        # Update and draw existing particles
        for i, particle in enumerate(self.glitter_particles[:]):
            # Reduce particle life
            particle['life'] -= 1
            
            # Make particle fade out over time
            alpha = int(255 * (particle['life'] / particle['max_life']))
            
            # Create a surface with per-pixel alpha for the glitter particle
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            
            # Draw the glitter as a soft circle with transparency
            pygame.draw.circle(
                particle_surface,
                (*particle['color'], alpha),
                (particle['size'], particle['size']),
                particle['size']
            )
            
            # Blit the particle to the screen
            self.screen.blit(
                particle_surface, 
                (int(particle['x'] - particle['size']), int(particle['y'] - particle['size']))
            )
            
            # Apply consistent movement based on velocity vectors
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            # Gradually change direction for organic movement
            particle['vel_x'] += random.uniform(-0.02, 0.02)
            particle['vel_y'] += random.uniform(-0.02, 0.02)
            
            # Cap maximum velocity to prevent erratic movement
            max_speed = 0.4
            current_speed = (particle['vel_x']**2 + particle['vel_y']**2)**0.5
            if current_speed > max_speed:
                factor = max_speed / current_speed
                particle['vel_x'] *= factor
                particle['vel_y'] *= factor
            
            # Remove particles when they die or move outside the progress bar
            if (particle['life'] <= 0 or 
                particle['x'] < bar_x or 
                particle['x'] > bar_x + progress_width or
                particle['y'] < bar_y or 
                particle['y'] > bar_y + bar_height):
                self.glitter_particles.remove(particle)
        
        # Progress text centered
        progress_text = self.font.render(
            f"Level {self.current_level}: {self.collected_gold_pieces}/{current_level_requirement}", 
            True, 
            (255, 255, 255)
        )
        progress_text_rect = progress_text.get_rect(center=(self.screen_width // 2, bar_y + bar_height + 25))
        self.screen.blit(progress_text, progress_text_rect)
        
    def _handle_gold_piece_collection(self):
        """Handle player collecting gold pieces."""
        collected_pieces = pygame.sprite.spritecollide(self.player, self.gold_pieces_group, True)
        if collected_pieces:
            # Play a collection sound (add to asset manager)
            # self.gold_collect_sound.play()
            self.coin_sound.play()
            # Increment collected gold pieces
            self.collected_gold_pieces += len(collected_pieces)
            
            # Optional: Increase player score
            self.player.score += len(collected_pieces) * 5

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
                    self.miner_sound.play()
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

