import pygame
import sys
import random
import math

# Constants (assuming these would be in my_constants.py)
WIDTH = 800
HEIGHT = 600
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Enemy states
STANDING = 0
GRAZING = 1
WALKING = 2
PANICKING = 3

class Player:
    def __init__(self, width, height):
        self.size = 50
        self.x = width // 2 - self.size // 2
        self.y = height // 2 - self.size // 2
        self.speed = 5
        self.direction = 0
        self.keys = {
            'w': False,
            'a': False,
            's': False,
            'd': False
        }
    
    def handle_key_event(self, event):
        """Handle key down and key up events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.keys['w'] = True
            if event.key == pygame.K_a:
                self.keys['a'] = True
            if event.key == pygame.K_s:
                self.keys['s'] = True
            if event.key == pygame.K_d:
                self.keys['d'] = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.keys['w'] = False
            if event.key == pygame.K_a:
                self.keys['a'] = False
            if event.key == pygame.K_s:
                self.keys['s'] = False
            if event.key == pygame.K_d:
                self.keys['d'] = False
    
    def move(self, width, height):
        """Move the player based on key states"""
        dx = 0
        dy = 0
        
        if self.keys['w']:
            dy -= self.speed
        if self.keys['s']:
            dy += self.speed
        if self.keys['a']:
            dx -= self.speed
        if self.keys['d']:
            dx += self.speed
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071
        
        # Update position
        self.x += dx
        self.y += dy
        
        # Update direction
        if dx != 0 or dy != 0:
            self.direction = math.atan2(dy, dx)
        
        # Keep within screen bounds
        self.x = max(0, min(width - self.size, self.x))
        self.y = max(0, min(height - self.size, self.y))
    
    def get_center(self):
        """Get the center coordinates of the player"""
        return self.x + self.size // 2, self.y + self.size // 2

    def draw(self, screen):
        """Draw the player"""
        # Draw player square
        pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))
        
        # Draw direction indicator when moving
        if any(self.keys.values()):
            dir_length = 25
            end_x = self.x + self.size/2 + math.cos(self.direction) * dir_length
            end_y = self.y + self.size/2 + math.sin(self.direction) * dir_length
            pygame.draw.line(screen, WHITE, 
                            (self.x + self.size/2, self.y + self.size/2),
                            (end_x, end_y), 3)

class Enemy:
    def __init__(self, width, height, player_x, player_y):
        # Generate random position away from player
        while True:
            x = random.randint(0, width - 40)
            y = random.randint(0, height - 40)
            # Make sure enemy isn't spawning directly on player
            if abs(x - player_x) > 100 or abs(y - player_y) > 100:
                break
        
        self.x = x
        self.y = y
        self.size = 40
        self.vx = 0
        self.vy = 0
        self.direction = random.uniform(0, 2 * math.pi)
        self.state = random.choice([GRAZING, STANDING, WALKING])
        self.state_timer = random.randint(60, 180)
        self.panic_direction_timer = 0
        self.color = BLUE
        self.just_panicked = False
        self.chain_reaction_source = False
        self.flee_from_x = 0
        self.flee_from_y = 0
    
    def update(self, width, height, player, repulsion_distance, chain_panic_distance):
        """Update enemy behavior"""
        # Decrease state timer
        self.state_timer -= 1
        
        # Handle panic direction updates
        if self.state == PANICKING:
            self.panic_direction_updates(player, width, height)
        
        # State change logic
        if self.state_timer <= 0:
            self.change_state()
        
        # Apply friction
        self.apply_friction()
        
        # Move based on state
        self.move(width, height)
        
        # Boundary handling
        self.handle_boundaries(width, height)
    
    def panic_direction_updates(self, player, width, height):
        """Update direction when panicking"""
        self.panic_direction_timer -= 1
        if self.panic_direction_timer <= 0:
            enemy_center_x = self.x + self.size // 2
            enemy_center_y = self.y + self.size // 2
            
            dx = enemy_center_x - self.flee_from_x
            dy = enemy_center_y - self.flee_from_y
            
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                dx /= dist
                dy /= dist
            
            flee_angle = math.atan2(dy, dx)
            self.direction = flee_angle + random.uniform(-0.3, 0.3)
            
            self.panic_direction_timer = random.randint(10, 20)
    
    def change_state(self):
        """Change enemy state"""
        previous_state = self.state
        
        if previous_state == PANICKING:
            self.state = WALKING
            self.color = BLUE
        else:
            # Weighted random state selection
            if previous_state == STANDING:
                self.state = random.choices([GRAZING, WALKING], weights=[70, 30])[0]
            elif previous_state == GRAZING:
                self.state = random.choices([GRAZING, STANDING, WALKING], weights=[50, 30, 20])[0]
            else:  # WALKING
                self.state = random.choices([GRAZING, STANDING, WALKING], weights=[40, 40, 20])[0]
        
        # Maybe change direction
        if self.state != previous_state or random.random() < 0.3:
            self.direction = random.uniform(0, 2 * math.pi)
        
        # Set new state timer
        if self.state == STANDING:
            self.state_timer = random.randint(120, 240)
        elif self.state == GRAZING:
            self.state_timer = random.randint(180, 360)
        elif self.state == WALKING:
            self.state_timer = random.randint(60, 180)
        else:  # PANICKING
            panic_time = random.randint(180, 300)
            if self.chain_reaction_source:
                panic_time = int(panic_time * 0.7)
            self.state_timer = panic_time
    
    def apply_friction(self):
        """Apply friction to slow down momentum"""
        if self.state == PANICKING:
            self.vx *= 0.95
            self.vy *= 0.95
        else:
            self.vx *= 0.9
            self.vy *= 0.9
    
    def move(self, width, height):
        """Move enemy based on current state"""
        if self.state != STANDING:
            # Determine speed based on state
            if self.state == PANICKING:
                speed = 4.0
                if self.chain_reaction_source:
                    speed *= 0.85
            elif self.state == WALKING:
                speed = 1.5
            else:  # GRAZING
                speed = 0.8
            
            target_vx = math.cos(self.direction) * speed
            target_vy = math.sin(self.direction) * speed
            
            # Gradually adjust velocity
            if self.state == PANICKING:
                self.vx = 0.3 * target_vx + 0.7 * self.vx
                self.vy = 0.3 * target_vy + 0.7 * self.vy
            else:
                self.vx = 0.1 * target_vx + 0.9 * self.vx
                self.vy = 0.1 * target_vy + 0.9 * self.vy
        
        # Move enemy
        self.x += self.vx
        self.y += self.vy
    
    def handle_boundaries(self, width, height):
        """Handle screen boundaries"""
        edge_buffer = 50
        # Horizontal boundaries
        if self.x < edge_buffer:
            self.direction = random.uniform(-math.pi/2, math.pi/2) if self.state == PANICKING else random.uniform(-math.pi/4, math.pi/4)
        elif self.x > width - self.size - edge_buffer:
            self.direction = random.uniform(math.pi/2, 3*math.pi/2) if self.state == PANICKING else random.uniform(3*math.pi/4, 5*math.pi/4)
        
        # Vertical boundaries
        if self.y < edge_buffer:
            self.direction = random.uniform(0, math.pi) if self.state == PANICKING else random.uniform(math.pi/4, 3*math.pi/4)
        elif self.y > height - self.size - edge_buffer:
            self.direction = random.uniform(math.pi, 2*math.pi) if self.state == PANICKING else random.uniform(5*math.pi/4, 7*math.pi/4)
        
        # Keep within screen bounds
        self.x = max(0, min(width - self.size, self.x))
        self.y = max(0, min(height - self.size, self.y))
    
    def draw(self, screen):
        """Draw enemy"""
        # Draw body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        
        # Draw direction indicator
        dir_length = 20
        end_x = self.x + self.size/2 + math.cos(self.direction) * dir_length
        end_y = self.y + self.size/2 + math.sin(self.direction) * dir_length
        pygame.draw.line(screen, WHITE, 
                        (self.x + self.size/2, self.y + self.size/2),
                        (end_x, end_y), 2)
        
        # Draw state indicator
        indicator_color = WHITE
        indicator_size = 8
        if self.state == STANDING:
            indicator_color = (200, 200, 200)  # Light gray
        elif self.state == GRAZING:
            indicator_color = (100, 200, 100)  # Light green
        elif self.state == WALKING:
            indicator_color = (200, 100, 100)  # Light red
        elif self.state == PANICKING:
            # Make indicator blink when panicking
            if pygame.time.get_ticks() % 500 < 250:
                indicator_color = (255, 100, 0)  # Orange
            else:
                indicator_color = (255, 0, 0)  # Red
        
        pygame.draw.circle(screen, indicator_color, 
                          (int(self.x + self.size//2), 
                           int(self.y + self.size//2)), 
                          indicator_size)

class Game:
    def __init__(self):
        pygame.init()
        self.width = WIDTH
        self.height = HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pyweek 39 downstream")
        
        self.player = Player(self.width, self.height)
        
        # Create enemies
        self.enemies = [Enemy(self.width, self.height, self.player.x, self.player.y) 
                        for _ in range(8)]
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Gameplay constants
        self.repulsion_distance = 150
        self.chain_panic_distance = 120
        
        self.space_pressed = False
        self.last_space_pressed = False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Player movement
            self.player.handle_key_event(event)
    
    def update(self):
        """Update game state"""
        # Player movement
        self.player.move(self.width, self.height)
        
        # Space press logic
        self.last_space_pressed = self.space_pressed
        self.space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]
        space_just_pressed = self.space_pressed and not self.last_space_pressed
        
        # Reset panic flags
        for enemy in self.enemies:
            enemy.just_panicked = False
        
        # Handle space press startling
        if space_just_pressed:
            self.handle_space_press()
        
        # Update enemies
        player_center_x, player_center_y = self.player.get_center()
        for enemy in self.enemies:
            enemy.update(self.width, self.height, self.player, 
                         self.repulsion_distance, self.chain_panic_distance)
    
    def handle_space_press(self):
        """Handle space press for startling enemies"""
        player_center_x, player_center_y = self.player.get_center()
        
        for enemy in self.enemies:
            enemy_center_x = enemy.x + enemy.size // 2
            enemy_center_y = enemy.y + enemy.size // 2
            
            dist = math.sqrt((player_center_x - enemy_center_x)**2 + 
                             (player_center_y - enemy_center_y)**2)
            
            if dist < self.repulsion_distance:
                # Direction away from player
                dx = enemy_center_x - player_center_x
                dy = enemy_center_y - player_center_y
                
                if dist > 0:
                    dx /= dist
                    dy /= dist
                
                # Apply force
                force = min(10 * (1 - dist / self.repulsion_distance), 10)
                enemy.vx += dx * force
                enemy.vy += dy * force
                
                # Panic state
                if enemy.state != PANICKING:
                    enemy.state = PANICKING
                    enemy.color = YELLOW
                    enemy.state_timer = random.randint(180, 300)
                    enemy.just_panicked = True
                    enemy.chain_reaction_source = False
                    
                    # Flee direction
                    enemy.flee_from_x = player_center_x
                    enemy.flee_from_y = player_center_y
                    enemy.direction = math.atan2(dy, dx)
                    enemy.panic_direction_timer = random.randint(15, 30)
    
    def draw(self):
        """Draw game elements"""
        # Clear screen
        self.screen.fill(GREEN)
        
        # Draw panic radius when space is pressed
        if self.space_pressed:
            radius_surface = pygame.Surface((self.repulsion_distance*2, self.repulsion_distance*2), pygame.SRCALPHA)
            pygame.draw.circle(radius_surface, (255, 200, 200, 100), 
                               (self.repulsion_distance, self.repulsion_distance), 
                               self.repulsion_distance)
            player_center_x, player_center_y = self.player.get_center()
            self.screen.blit(radius_surface, 
                             (player_center_x - self.repulsion_distance, 
                              player_center_y - self.repulsion_distance))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw controls text
        font = pygame.font.SysFont(None, 24)
        controls_text = "Controls: W,A,S,D to move, SPACE to startle nearby enemies"
        text_surface = font.render(controls_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Cap frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    Game().run()