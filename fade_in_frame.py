import pygame
class FadeInOutFrame:
    def __init__(self, screen, image, fade_duration=1.0, stay_duration=1.0, last_slide=False):
        """
        Creates a frame that fades in an image, stays for a duration, then fades out
        
        Args:
            screen: The pygame surface to draw on
            image: The pygame surface/image to display
            fade_duration: Duration of fade in and fade out in seconds
            stay_duration: Duration to stay fully visible in seconds
            last_slide: If True, remains visible after fade in and doesn't fade out
        """
        self.screen = screen
        self.image = image
        self.fade_duration = fade_duration
        self.stay_duration = stay_duration
        self.last_slide = last_slide
        
        # State tracking
        self.state = "fade_in"  # States: fade_in, stay, fade_out, complete
        self.alpha = 0  # 0 = transparent, 255 = fully visible
        self.timer = 0
        self.done = False
        
        # Create a surface with per-pixel alpha to handle the fade effect
        self.alpha_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        
    def update(self, dt):
        """
        Update the fade state based on elapsed time
        
        Args:
            dt: Time elapsed since last frame in seconds
            
        Returns:
            bool: True if the frame is still active, False if complete and can be removed
        """
        self.timer += dt
        
        if self.state == "fade_in":
            # Calculate alpha based on timer progress
            progress = min(1.0, self.timer / self.fade_duration)
            self.alpha = int(255 * progress)
            
            # Move to next state if fade in complete
            if progress >= 1.0:
                self.timer = 0
                self.state = "stay"
                self.alpha = 255
                
        elif self.state == "stay":
            # If it's the last slide, just stay visible indefinitely
            if self.last_slide:
                return True
                
            # Stay visible for the specified duration
            if self.timer >= self.stay_duration:
                self.timer = 0
                self.state = "fade_out"
                
        elif self.state == "fade_out":
            # Calculate alpha based on timer progress
            progress = min(1.0, self.timer / self.fade_duration)
            self.alpha = int(255 * (1.0 - progress))
            
            # Mark as complete if fade out is done
            if progress >= 1.0:
                self.state = "complete"
                self.done = True
                return False
                
        return True
        
    def draw(self):
        """
        Draw the image with the current alpha value
        """
        # Clear the alpha surface
        self.alpha_surface.fill((0, 0, 0, 0))
        
        # Blit the image onto the alpha surface
        self.alpha_surface.blit(self.image, (0, 0))
        
        # Set the alpha for the entire surface
        self.alpha_surface.set_alpha(self.alpha)
        
        # Draw the alpha surface to the screen
        self.screen.blit(self.alpha_surface, (0, 0))
        
    def is_done(self):
        """
        Check if the frame has completed its fade cycle
        
        Returns:
            bool: True if the frame is done and should be removed
        """
        return self.done