import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# World dimensions (larger than screen)
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000

# Checkerboard tile size
TILE_SIZE = 50

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Adjust entity position relative to camera
        return entity.rect.move((-self.camera.x, -self.camera.y))

    def update(self, target):
        # Correctly center the camera on the player
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit camera movement to world boundaries
        x = min(0, x)  # Left boundary
        x = max(-(WORLD_WIDTH - SCREEN_WIDTH), x)  # Right boundary
        y = min(0, y)  # Top boundary
        y = max(-(WORLD_HEIGHT - SCREEN_HEIGHT), y)  # Bottom boundary

        self.camera.x = -x
        self.camera.y = -y

def draw_checkerboard(screen, camera):
    # Colors for checkerboard
    colors = [(200, 200, 200), (230, 230, 230)]
    
    # Calculate the camera's position
    camera_x = camera.camera.x
    camera_y = camera.camera.y
    
    # Draw checkerboard pattern to cover the entire screen
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            # Calculate precise world coordinates
            world_x = x + camera_x
            world_y = y + camera_y
            
            # Determine color based on precise world coordinates
            color = colors[int(math.floor(world_x / TILE_SIZE) + math.floor(world_y / TILE_SIZE)) % 2]
            
            # Draw tile
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

class Player:
    def __init__(self, x, y):
        # Player rectangle
        self.rect = pygame.Rect(x, y, 50, 50)
        # Player movement speed
        self.speed = 5
        # Player color (start with blue)
        self.color = (0, 0, 255)
        # Player facing direction (in degrees)
        self.facing = 0
        # Attack cooldown
        self.attack_cooldown = 0
        # Attack parameters
        self.attack_radius = 100
        self.attack_angle = 90

    def move(self, keys, camera):
        # WASD movement and direction tracking
        dx, dy = 0, 0
        if keys[pygame.K_a] and self.rect.left > 0:
            dx -= self.speed
        if keys[pygame.K_d] and self.rect.right < WORLD_WIDTH:
            dx += self.speed
        if keys[pygame.K_w] and self.rect.top > 0:
            dy -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < WORLD_HEIGHT:
            dy += self.speed
        
        # Update position
        self.rect.x += dx
        self.rect.y += dy
        
        # Update facing direction based on mouse position
        mouse_pos = pygame.mouse.get_pos()
        # Adjust mouse position to world coordinates
        world_mouse_x = mouse_pos[0] + camera.camera.x
        world_mouse_y = mouse_pos[1] + camera.camera.y
        
        # Calculate angle to mouse
        ex = world_mouse_x - self.rect.centerx
        ey = world_mouse_y - self.rect.centery
        
        # Calculate facing angle (using negative ey to correct for inverted y-axis)
        self.facing = math.degrees(math.atan2(-ey, ex))

    def is_point_in_attack_hitbox(self, point):
        # Calculate vector from player center to point
        player_center = (
            self.rect.centerx, 
            self.rect.centery
        )
        
        # Calculate vector components
        ex = point[0] - player_center[0]
        ey = point[1] - player_center[1]
        
        # Calculate distance
        distance = math.sqrt(ex**2 + ey**2)
        
        # Check if point is within attack radius
        if distance > self.attack_radius:
            return False
        
        # Calculate angle to point
        point_angle = math.degrees(math.atan2(-ey, ex))
        
        # Normalize angles
        angle_diff = abs(point_angle - self.facing)
        angle_diff = min(angle_diff, 360 - angle_diff)
        
        # Check if point is within attack slice
        return angle_diff <= self.attack_angle / 2

    def is_enemy_in_hitbox(self, enemy):
        # Check enemy's corner and center points
        points_to_check = [
            enemy.rect.topleft,
            enemy.rect.topright,
            enemy.rect.bottomleft,
            enemy.rect.bottomright,
            enemy.rect.center
        ]
        
        # If any point is in the hitbox, return True
        return any(self.is_point_in_attack_hitbox(point) for point in points_to_check)

    def draw(self, screen, camera):
        # Draw the player rectangle relative to camera
        pygame.draw.rect(screen, self.color, camera.apply(self))
        
        # Draw attack zone for visualization
        if self.attack_cooldown > 0:
            # Calculate attack zone arc
            start_angle = math.radians(self.facing - self.attack_angle / 2)
            end_angle = math.radians(self.facing + self.attack_angle / 2)
            
            # Get camera-adjusted player center
            camera_player = camera.apply(self)
            player_center = (
                camera_player.x + self.rect.width // 2, 
                camera_player.y + self.rect.height // 2
            )
            
            # Draw attack arc
            pygame.draw.arc(
                screen, 
                (255, 0, 0, 128),  # Semi-transparent red
                (
                    player_center[0] - self.attack_radius, 
                    player_center[1] - self.attack_radius, 
                    self.attack_radius * 2, 
                    self.attack_radius * 2
                ), 
                start_angle, 
                end_angle, 
                5  # Line thickness
            )
            
            # Visualize enemy detection
            for enemy in enemies:
                if self.is_enemy_in_hitbox(enemy):
                    # Draw green dots at points inside hitbox
                    points_to_check = [
                        enemy.rect.topleft,
                        enemy.rect.topright,
                        enemy.rect.bottomleft,
                        enemy.rect.bottomright,
                        enemy.rect.center
                    ]
                    for point in points_to_check:
                        # Convert to camera-adjusted coordinates
                        adjusted_point = (
                            point[0] - camera.camera.x,
                            point[1] - camera.camera.y
                        )
                        pygame.draw.circle(
                            screen, 
                            (0, 255, 0),  # Green
                            adjusted_point, 
                            5  # Radius
                        )

class Enemy:
    def __init__(self, x, y):
        # Enemy rectangle
        self.rect = pygame.Rect(x, y, 60, 60)
        # Enemy color
        self.color = (128, 128, 128)  # Gray
        # Track if enemy is alive
        self.alive = True

    def draw(self, screen, camera):
        # Draw the enemy rectangle if alive
        if self.alive:
            pygame.draw.rect(screen, self.color, camera.apply(self))

def spawn_enemies(existing_enemies, max_enemies=20):
    # Spawn new enemies if below max
    if len(existing_enemies) < max_enemies:
        # Attempt to spawn 1-3 new enemies
        spawn_count = random.randint(1, 3)
        for _ in range(spawn_count):
            # Random position within world boundaries
            x = random.randint(0, WORLD_WIDTH - 60)
            y = random.randint(0, WORLD_HEIGHT - 60)
            
            # Ensure minimum distance from player
            new_enemy = Enemy(x, y)
            existing_enemies.append(new_enemy)

def main():
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player vs Enemies with Directional Attack")

    # Create camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Create player in the middle of the world
    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

    # Initial enemy list
    global enemies  # Make enemies global so it can be accessed in Player.draw()
    enemies = []
    spawn_enemies(enemies)

    # Clock to control frame rate
    clock = pygame.time.Clock()

    # Spawn timer
    spawn_timer = 0
    SPAWN_INTERVAL = 60  # Frames between enemy spawns

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Attack on SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Check for enemy elimination in attack hitbox
                for enemy in enemies:
                    if enemy.alive and player.is_enemy_in_hitbox(enemy):
                        enemy.alive = False
                
                # Set attack cooldown
                player.attack_cooldown = 30

        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Move player
        player.move(keys, camera)

        # Update camera to follow player
        camera.update(player)

        # Periodically spawn new enemies
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_enemies(enemies)
            spawn_timer = 0

        # Remove dead enemies
        enemies = [enemy for enemy in enemies if enemy.alive]

        # Manage attack cooldown
        if player.attack_cooldown > 0:
            player.attack_cooldown -= 1

        # Draw checkerboard background
        draw_checkerboard(screen, camera)

        # Draw player
        player.draw(screen, camera)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, camera)

        # Update the display
        pygame.display.flip()

        # Control frame rate
        clock.tick(60)

    # Quit Pygame
    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()