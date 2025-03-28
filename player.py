import pygame
import math

class Player(pygame.sprite.Sprite):
    """Represents the player character in the game."""
    def __init__(self, asset_manager, x, y, screen_width, screen_height):
        super().__init__()
        
        # Screen dimensions for boundary checks
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load animation frames
        self.animation_frames = [
            asset_manager.load_image(f'assets/images/player{i}.png') 
            for i in range(1, 8)
        ]
        
        # Load special state images and sounds
        self.eating_image = asset_manager.load_image("assets/images/player_eat.png")
        self.eat_sound = asset_manager.load_sound("assets/sounds/CLICK.ogg", 0.2)
        self.move_sound = asset_manager.load_sound("assets/sounds/swim.ogg", 0.1)

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
        """
        Handle player input and movement with continuous rock pushback and screen boundary checks.
        
        Args:
            rocks (pygame.sprite.Group): Group of rock sprites
        """
        keys = pygame.key.get_pressed()
        
        # Reset velocities
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        
        # WASD Movement with collision detection and rock pushback
        movement_map = {
            pygame.K_w: (0, -self.speed),
            pygame.K_s: (0, self.speed),
            pygame.K_a: (-self.speed, 0),
            pygame.K_d: (self.speed, 0)
        }
        
        # Player's desired movement
        player_dx, player_dy = 0, 0
        
        # Track which keys are pressed
        pressed_keys = [key for key, (dx, dy) in movement_map.items() if keys[key]]
        
        for key, (dx, dy) in movement_map.items():
            if keys[key]:
                player_dx += dx
                player_dy += dy
                self.is_moving = True
        
        # Normalize diagonal movement speed
        if len(pressed_keys) == 2:  # Diagonal movement
            player_dx *= 0.707  # 1/sqrt(2)
            player_dy *= 0.707  # 1/sqrt(2)
        
        # Tentative move based on player input
        tentative_rect = self.rect.copy()
        tentative_rect.x += player_dx
        tentative_rect.y += player_dy
        
        # Check for rock collisions
        rock_collisions = [rock for rock in rocks if tentative_rect.colliderect(rock.rect)]
        
        if rock_collisions:
            # Continuous pushback even when not moving
            for rock in rock_collisions:
                # Determine rock's movement
                rock_dx = getattr(rock, 'velocity_x', 0)
                rock_dy = getattr(rock, 'velocity_y', 0)
                
                # Push player out of the rock completely
                overlap_left = tentative_rect.right - rock.rect.left
                overlap_right = rock.rect.right - tentative_rect.left
                overlap_top = tentative_rect.bottom - rock.rect.top
                overlap_bottom = rock.rect.bottom - tentative_rect.top
                
                # Find the smallest overlap to minimize displacement
                min_overlap = min(
                    overlap_left if overlap_left > 0 else float('inf'),
                    overlap_right if overlap_right > 0 else float('inf'),
                    overlap_top if overlap_top > 0 else float('inf'),
                    overlap_bottom if overlap_bottom > 0 else float('inf')
                )
                
                # Push out based on the smallest overlap
                if min_overlap == overlap_left:
                    self.rect.right = rock.rect.left - self.speed *2
                elif min_overlap == overlap_right:
                    self.rect.left = rock.rect.right + self.speed
                elif min_overlap == overlap_top:
                    self.rect.bottom = rock.rect.top - self.speed
                elif min_overlap == overlap_bottom:
                    self.rect.top = rock.rect.bottom + self.speed
                
                # Apply rock's movement to ensure continuous pushback
                self.rect.x += rock_dx
                self.rect.y += rock_dy
        else:
            # Normal movement when no collision
            self.rect.x += player_dx
            self.rect.y += player_dy
            self.velocity_x = player_dx
            self.velocity_y = player_dy
        
        # Screen boundary checks
        # Left boundary (always 0)
        self.rect.left = max(-100, self.rect.left)
        
        # Right boundary
        self.rect.right = min(self.screen_width, self.rect.right)
        
        # Top boundary 
        self.rect.top = max(0, self.rect.top)
        
        # Bottom boundary
        self.rect.bottom = min(self.screen_height, self.rect.bottom)
        
        # Manage sound playback only when actually moving
        if self.is_moving:
            self._manage_movement_sound()

    # Rest of the methods remain the same as in the original code

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
        self.handle_input(rocks)
        
        # Handle eating animation
        if self.is_eating:
            self.eating_timer -= 1
            if self.eating_timer <= 0:
                self.is_eating = False

        # Only update position if actually moving
        if self.is_moving:
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y
            self.original_y = self.rect.y

        self.animate()
        self.swimming_bob()