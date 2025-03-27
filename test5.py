import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60

# Load player images
player_images = [pygame.image.load(f"assets/images/player{i}.png") for i in range(1, 8)]
back = pygame.image.load("assets/images/river_back.png")

# Define waypoints
waypoints = [(51, 596), (923, 481), (537, 383), (878, 366)]

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sharper Turns Animation")

# Player properties
start_size = 200  
end_size = 20  
animation_duration = 3  # Total animation time in seconds
num_frames = FPS * animation_duration

# Animation variables
frame_count = 0
running = True
k = 0.01  # Adjust for faster/slower slowdown

# Linear interpolation function
def lerp(a, b, t):
    return a + (b - a) * t

# Function to compute cubic Bezier curve points
def bezier_curve(p0, p1, p2, p3, t):
    """Cubic Bezier curve"""
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
    )

# Function to generate sharp control points
def generate_control_points(waypoints):
    control_points = []
    for i in range(len(waypoints) - 1):
        p0 = waypoints[i]
        p3 = waypoints[i + 1]
        
        # Compute direction vector
        dx, dy = p3[0] - p0[0], p3[1] - p0[1]
        dist = math.hypot(dx, dy)
        
        # Control points closer to waypoints for sharper turns
        scale = dist * 0.2  # Adjust factor for sharpness
        
        p1 = (p0[0] + scale * dx / dist, p0[1] + scale * dy / dist)
        p2 = (p3[0] - scale * dx / dist, p3[1] - scale * dy / dist)
        
        control_points.append((p0, p1, p2, p3))
    
    return control_points

# Generate control points for each segment
segments = generate_control_points(waypoints)

# Game loop
while running:
    screen.fill((30, 30, 30))  
    screen.blit(back, (0, 0))
    pygame.time.Clock().tick(FPS)
    
    # Exponential decay for fast start, gradual slowdown
    t = 1 - math.exp(-k * frame_count)

    if t >= 1:
        running = False  
        break
    
    # Compute size change
    size = lerp(start_size, end_size, t)
    
    # **Quit when size is 40**
    if size <= 45:
        running = False  
        break

    # Determine which segment to use
    num_segments = len(segments)
    seg_t = (t * num_segments) % 1  # Normalized time per segment
    seg_index = min(int(t * num_segments), num_segments - 1)
    
    # Compute position using the selected Bezier segment
    pos = bezier_curve(*segments[seg_index], seg_t)
    
    # Select animation frame
    img_index = (frame_count // 5) % len(player_images)
    player_img = pygame.transform.scale(player_images[img_index], (int(size), int(size)))
    
    if size > 0:
        screen.blit(player_img, (int(pos[0] - size // 2), int(pos[1] - size // 2)))
    
    pygame.display.flip()
    
    frame_count += 1

pygame.quit()
