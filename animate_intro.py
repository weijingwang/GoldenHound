import pygame
from utils import PerlinNoiseOverlay
import math
import sys

class Animation:
    def __init__(self, width=1280, height=720):
        pygame.init()
        
        # Initialize display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        
        # Create noise overlay
        self.noise_overlay = PerlinNoiseOverlay(width, height, 200, 150, scale=0.5, alpha=20)
        
        # Load background image
        self.bg = pygame.image.load("assets/images/intro1/intro1_bg.png")
        
        # Load intro frames
        self.frames = [pygame.image.load(f"assets/images/intro1/intro{i}.png") for i in range(1, 13)]
        
        # Set custom frame durations (in milliseconds)
        self.frame_durations = [500, 500, 100, 200, 100, 100, 100, 200, 200, 200, 200, 800]
        
        # Animation state
        self.clock = pygame.time.Clock()
        self.frame_index = 0
        self.time_accumulator = 0
        self.completed = False
    
    def update(self):
        """Update animation state for one frame"""
        # Skip if animation is already complete
        if self.completed:
            return True
            
        # Get time passed since last frame (limit to 60 FPS)
        dt = self.clock.tick(60)
        self.time_accumulator += dt
        
        # Advance frame if the duration has elapsed
        if self.time_accumulator >= self.frame_durations[self.frame_index]:
            self.time_accumulator = 0
            self.frame_index += 1
            
            # Check if animation is complete
            if self.frame_index >= len(self.frames):
                self.completed = True
                return True
        
        return False
    
    def render(self):
        """Render current animation frame"""
        # Draw background
        self.screen.blit(self.bg, (0, 0))
        
        # Draw current frame if animation is not complete
        if not self.completed and self.frame_index < len(self.frames):
            self.screen.blit(self.frames[self.frame_index], (0, 0))
        
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
    
    def is_completed(self):
        """Check if animation is complete"""
        return self.completed
    
    def reset(self):
        """Reset animation to beginning"""
        self.frame_index = 0
        self.time_accumulator = 0
        self.completed = False



class CurveAnimation:
    def __init__(self, start_size=200, end_size=20, k=0.005, back=0, width=1280, height=720, fps=60):
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
        self.start_size = start_size
        self.end_size = end_size
        self.k = k  # Speed factor
        
        # Determine if we're growing or shrinking
        self.is_growing = end_size > start_size
        
        # Set fade trigger size based on animation direction
        if self.is_growing:
            # If growing, trigger fade when close to target size
            self.fade_trigger_size = end_size * 0.9  # Start fade at 90% of target size
        else:
            # If shrinking, trigger fade when small enough (as in original)
            self.fade_trigger_size = 45
        
        # Load assets
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Load images
        if back == 0:
            self.player_images = [pygame.image.load(f"assets/images/player/player1_{i}.png") for i in range(1, 8)]
            self.back = pygame.image.load("assets/images/river_back.png")
        else:
            self.player_images = [pygame.image.load(f"assets/images/player/player4_{i}.png") for i in range(1, 8)]
            self.back = pygame.image.load("assets/images/river_forest.png")

        # Create noise overlay
        self.noise_overlay = PerlinNoiseOverlay(width, height, 200, 150, scale=0.5, alpha=20)
        
        # Set up waypoints and generate control points
        self.waypoints = [(51, 596), (923, 481), (537, 383), (878, 366)]
        self.segments = self.generate_control_points(self.waypoints)
        
        # Music initialization can be uncommented if needed
        # pygame.mixer.init()
        # pygame.mixer.music.load("assets/sound/music.mp3")
        # pygame.mixer.music.play(-1)

    def handle_events(self):
        """Handle pygame events, return False to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def set_waypoints(self, waypoints):
        """Set custom waypoints for the animation path"""
        self.waypoints = waypoints
        self.segments = self.generate_control_points(self.waypoints)
    
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
        
        # Check fade trigger condition based on animation direction
        if self.is_growing:
            # For growing, start fade when close enough to target size
            fade_condition = size >= self.fade_trigger_size
        else:
            # For shrinking, start fade when small enough
            fade_condition = size <= self.fade_trigger_size
        
        # Start fade out when trigger condition is met
        if fade_condition and not self.fading:
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
        if not self.fading or self.fade_alpha < 255:
            num_segments = len(self.segments)
            seg_t = (t * num_segments) % 1
            seg_index = min(int(t * num_segments), num_segments - 1)
            pos = self.bezier_curve(*self.segments[seg_index], seg_t)
            
            img_index = (self.frame_count // 5) % len(self.player_images)
            
            # Ensure size is at least 1 to avoid scaling errors
            current_size = max(1, int(size))
            player_img = pygame.transform.scale(self.player_images[img_index], (current_size, current_size))
            
            self.screen.blit(player_img, (int(pos[0] - current_size // 2), int(pos[1] - current_size // 2)))
        
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


class GameIntro:
    def __init__(self):
        # Initialize both animations
        self.intro_animation = Animation()
        self.character_animation = CurveAnimation()
        
        # Track current animation state
        self.current_animation = "intro"
        self.transition_delay = 500  # milliseconds to wait between animations
        self.transition_timer = 0
        
        self.clock = pygame.time.Clock()
        self.completed = False
    
    def update(self):
        """Update the current animation state. Returns True when all animations are complete."""
        if self.completed:
            return True
            
        # Update based on current animation
        if self.current_animation == "intro":
            # Update intro animation
            intro_completed = self.intro_animation.update()
            
            # Check if intro animation is complete
            if intro_completed:
                self.current_animation = "transition"
                self.transition_timer = 0
                
        elif self.current_animation == "transition":
            # Update transition timer
            self.transition_timer += self.clock.tick(60)
            
            # Check if transition period is complete
            if self.transition_timer >= self.transition_delay:
                self.current_animation = "character"
                
        elif self.current_animation == "character":
            # Update character animation
            animation_completed = self.character_animation.update()
            
            # Check if character animation is complete
            if animation_completed:
                self.completed = True
                return True
        
        return False
    
    def render(self):
        """Render the current animation frame"""
        if self.current_animation == "intro" or self.current_animation == "transition":
            self.intro_animation.render()
        elif self.current_animation == "character":
            self.character_animation.render()
    
    def handle_events(self):
        """Handle pygame events, return False to quit"""
        if self.current_animation == "intro":
            return self.intro_animation.handle_events()
        elif self.current_animation == "character":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            # return self.character_animation.handle_events()
        elif self.current_animation == "transition":
            # Handle events during transition
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            return True
        
        return True
    
    def tick(self):
        """Control frame rate if not already handled by current animation"""
        if self.current_animation == "transition":
            # We already called tick in the update method
            pass
        elif self.current_animation == "intro":
            # The update method already calls tick
            pass
        elif self.current_animation == "character":
            self.character_animation.clock.tick()
    
    def is_completed(self):
        """Check if all animations are complete"""
        return self.completed
    
    def reset(self):
        """Reset all animations to beginning"""
        self.intro_animation.reset()
        # Reset character animation (assuming it has a reset method)
        self.character_animation.frame_count = 0
        self.character_animation.fading = False
        self.character_animation.fade_alpha = 0
        
        self.current_animation = "intro"
        self.transition_timer = 0
        self.completed = False