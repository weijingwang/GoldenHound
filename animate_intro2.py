import pygame
import math
import sys

def run_animation2():
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
    
    def lerp(a, b, t):
        return a + (b - a) * t
    
    def bezier_curve(p0, p1, p2, p3, t):
        """Cubic Bezier curve"""
        u = 1 - t
        return (
            u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        )
    
    def generate_control_points(waypoints):
        control_points = []
        for i in range(len(waypoints) - 1):
            p0 = waypoints[i]
            p3 = waypoints[i + 1]
            
            dx, dy = p3[0] - p0[0], p3[1] - p0[1]
            dist = math.hypot(dx, dy)
            scale = dist * 0.2  
            
            p1 = (p0[0] + scale * dx / dist, p0[1] + scale * dy / dist)
            p2 = (p3[0] - scale * dx / dist, p3[1] - scale * dy / dist)
            
            control_points.append((p0, p1, p2, p3))
        
        return control_points
    
    segments = generate_control_points(waypoints)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        
        screen.fill((30, 30, 30))  
        screen.blit(back, (0, 0))
        pygame.time.Clock().tick(FPS)
        
        t = 1 - math.exp(-k * frame_count)
        
        if t >= 1:
            break
        
        size = lerp(start_size, end_size, t)
        
        if size <= 45:
            break
        
        num_segments = len(segments)
        seg_t = (t * num_segments) % 1  
        seg_index = min(int(t * num_segments), num_segments - 1)
        
        pos = bezier_curve(*segments[seg_index], seg_t)
        
        img_index = (frame_count // 5) % len(player_images)
        player_img = pygame.transform.scale(player_images[img_index], (int(size), int(size)))
        
        if size > 0:
            screen.blit(player_img, (int(pos[0] - size // 2), int(pos[1] - size // 2)))
        
        pygame.display.flip()
        
        frame_count += 1
