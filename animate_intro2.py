import pygame
import math
import sys
from utils import PerlinNoiseOverlay

class Animation:
    def __init__(self, width=1280, height=720, fps=60):
        # Initialize display parameters
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self.FADE_DURATION = 2  # Duration for fade-out effect
        
        # Initialize animation state
        self.frame_count = 0
        self.fading = False
        self.fade_alpha = 0
        self.fade_start = 0
        
        # Animation parameters
        self.start_size = 200
        self.end_size = 20
        self.animation_duration = 3
        self.k = 0.005  # Speed factor
        
        # Load assets
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sharper Turns Animation")
        self.clock = pygame.time.Clock()
        
        # Load images
        self.player_images = [pygame.image.load(f"assets/images/player/player1_{i}.png") for i in range(1, 8)]
        self.back = pygame.image.load("assets/images/river_back.png")
        
        # Create noise overlay
        self.noise_overlay = PerlinNoiseOverlay(width, height, 200, 150, scale=0.5, alpha=20)
        
        # Set up waypoints and generate control points
        self.waypoints = [(51, 596), (923, 481), (537, 383), (878, 366)]
        self.segments = self.generate_control_points(self.waypoints)
        
        # Music initialization can be uncommented if needed
        # pygame.mixer.init()
        # pygame.mixer.music.load("assets/sound/music.mp3")
        # pygame.mixer.music.play(-1)
    
    def lerp(self, a, b, t):
        """Linear interpolation between a and b at time t"""
        return a + (b - a) * t
    
    def bezier_curve(self, p0, p1, p2, p3, t):
        """Calculate position along bezier curve at time t"""
        u = 1 - t
        return (
            u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        )
    
    def generate_control_points(self, waypoints):
        """Generate control points for bezier curves connecting waypoints"""
        control_points = []
        for i in range(len(waypoints) - 1):
            p0, p3 = waypoints[i], waypoints[i + 1]
            dx, dy = p3[0] - p0[0], p3[1] - p0[1]
            dist = math.hypot(dx, dy)
            scale = dist * 0.2
            p1 = (p0[0] + scale * dx / dist, p0[1] + scale * dy / dist)
            p2 = (p3[0] - scale * dx / dist, p3[1] - scale * dy / dist)
            control_points.append((p0, p1, p2, p3))
        return control_points
    
    def update(self):
        """Update animation state for one frame"""
        self.frame_count += 1
        
        # Calculate animation progress
        t = 1 - math.exp(-self.k * self.frame_count)
        size = self.lerp(self.start_size, self.end_size, t)
        
        # Start fade out when character becomes small enough
        if size <= 45 and not self.fading:
            self.fading = True
            self.fade_start = pygame.time.get_ticks()
        
        # Update fade alpha if fading
        if self.fading:
            elapsed_fade = pygame.time.get_ticks() - self.fade_start
            self.fade_alpha = min(255, (elapsed_fade / (self.FADE_DURATION * 1000)) * 255)
            # Uncomment if using music
            # pygame.mixer.music.set_volume(0.2 - (self.fade_alpha / 255)*0.2)
        
        # Return True if animation is complete
        return self.fade_alpha >= 255
    
    def render(self):
        """Render current animation frame"""
        # Clear screen and draw background
        self.screen.fill((30, 30, 30))
        self.screen.blit(self.back, (0, 0))
        
        # Calculate animation progress
        t = 1 - math.exp(-self.k * self.frame_count)
        size = self.lerp(self.start_size, self.end_size, t)
        
        # If not fully faded, draw the player
        if not self.fading:
            num_segments = len(self.segments)
            seg_t = (t * num_segments) % 1
            seg_index = min(int(t * num_segments), num_segments - 1)
            pos = self.bezier_curve(*self.segments[seg_index], seg_t)
            
            img_index = (self.frame_count // 5) % len(self.player_images)
            player_img = pygame.transform.scale(self.player_images[img_index], (int(size), int(size)))
            
            if size > 0:
                self.screen.blit(player_img, (int(pos[0] - size // 2), int(pos[1] - size // 2)))
        
        # Apply fade effect if fading
        if self.fading:
            fade_surface = pygame.Surface((self.WIDTH, self.HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            self.screen.blit(fade_surface, (0, 0))
        
        # Apply noise overlay
        noise_surface = self.noise_overlay.generate()
        self.screen.blit(noise_surface, (0, 0))
        self.noise_overlay.update()
        
        # Update display
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events, return False to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def tick(self):
        """Advance the clock"""
        self.clock.tick(self.FPS)
