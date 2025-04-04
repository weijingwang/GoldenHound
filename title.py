import pygame
import os
import sys

class Button:
    def __init__(self, x, y, width, height, text, font, idle_color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_clicked = False
    
    def draw(self, surface):
        """Draw the button on the given surface."""
        current_color = self.hover_color if self.is_hovered else self.idle_color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=1)
        pygame.draw.rect(surface, self.text_color, self.rect, 2, border_radius=1)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos, mouse_clicked):
        """Update button state based on mouse position and click."""
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Check for click
        if self.is_hovered and mouse_clicked:
            self.is_clicked = True
            return True
        
        return False

class TitleScreen:
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Colors
        self.WHITE = (220, 220, 220)
        self.BLACK = (0, 0, 0)
        self.GRAY = (100, 100, 100)
        self.DARK_GRAY = (50, 50, 50)
        self.LIGHT_BLUE = (113, 91, 100)
        self.DARK_BLUE = (93, 70, 49)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 120)
        self.subtitle_font = pygame.font.Font(None, 60)
        self.button_font = pygame.font.Font(None, 45)
        
        # Start Button
        button_width = 250
        button_height = 70
        button_x = (self.screen_width - button_width) // 2
        button_y = self.screen_height // 2 + 250
        self.start_button = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Start game", 
            self.button_font, 
            self.DARK_BLUE, 
            self.LIGHT_BLUE, 
            self.WHITE
        )
        
        # Background images
        self.background_images = self._load_background_images()
        self.current_bg_index = 0
        self.next_bg_index = 1
        
        # Crossfade variables
        self.fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.fade_alpha = 0
        self.fade_speed = 3
        self.hold_timer = 0
        self.HOLD_TIME = 800  # 800 ms
        
        # Initial fade-in variables
        self.is_first_fade = True
        self.first_fade_alpha = 0
        
        # State tracking
        self.completed = False
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
    def _load_background_images(self):
        """Load background images from assets/images/titles directory."""
        images_path = 'assets/images/titles'
        try:
            image_files = [f for f in os.listdir(images_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            images = [pygame.transform.scale(
                pygame.image.load(os.path.join(images_path, img)).convert(), 
                (self.screen_width, self.screen_height)
            ) for img in image_files]
            return images
        except FileNotFoundError:
            print(f"Could not find images in {images_path}")
            return [pygame.Surface((self.screen_width, self.screen_height))]
    
    def _draw_text(self):
        """Draw title and subtitles."""
        # Main title
        title_text = self.title_font.render("Golden Hound", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 250))
        
        # Second subtitle
        subtitle_text = self.subtitle_font.render("art, code, music by speedlimit35", True, self.WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 200))
        
        # Draw text with a subtle shadow for better readability
        shadow_offset = 3
        
        # Title shadow
        shadow_title = self.title_font.render("Golden Hound", True, self.BLACK)
        self.screen.blit(shadow_title, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle shadow
        shadow_subtitle = self.subtitle_font.render("art, code, music by speedlimit35", True, self.BLACK)
        self.screen.blit(shadow_subtitle, (subtitle_rect.x + shadow_offset, subtitle_rect.y + shadow_offset))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw start button
        self.start_button.draw(self.screen)
    
    def _handle_first_fade_in(self):
        """Handle initial fade-in of the first background image."""
        if self.is_first_fade:
            # Create a surface with the first background image
            first_bg = self.background_images[self.current_bg_index].copy()
            first_bg.set_alpha(self.first_fade_alpha)
            self.screen.blit(first_bg, (0, 0))
            
            # Increase fade alpha
            self.first_fade_alpha += 5
            
            # Stop first fade when fully visible
            if self.first_fade_alpha >= 255:
                self.is_first_fade = False
                self.first_fade_alpha = 255
    
    def _cycle_backgrounds(self):
        """Handle background image cycling with crossfade."""
        # If in first fade, handle that separately
        if self.is_first_fade:
            return
        
        # Draw current background
        self.screen.blit(self.background_images[self.current_bg_index], (0, 0))
        
        # Check if it's time to cycle
        self.hold_timer += self.clock.get_time()
        
        if self.hold_timer >= self.HOLD_TIME:
            # Start fading
            self.fade_surface.blit(self.background_images[self.next_bg_index], (0, 0))
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
            
            # Increase fade
            self.fade_alpha += self.fade_speed
            
            # When fully faded, reset indexes and timer
            if self.fade_alpha >= 255:
                self.current_bg_index = self.next_bg_index
                self.next_bg_index = (self.next_bg_index + 1) % len(self.background_images)
                self.hold_timer = 0
                self.fade_alpha = 0
    
    def update(self):
        """Update title screen state for one frame. Returns True when completed."""
        if self.completed:
            return True
            
        # Update button with mouse state
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        # Check if button is clicked
        if self.start_button.update(mouse_pos, mouse_clicked):
            self.completed = True
            return True
            
        return False
    
    def render(self):
        """Render the title screen."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Cycle backgrounds or handle first fade-in
        if self.is_first_fade:
            self._handle_first_fade_in()
        else:
            self._cycle_backgrounds()
        
        # Draw text and button
        self._draw_text()
        
        # Update display
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events, return False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return False
                
            # Additional event handling for button hover
            if event.type == pygame.MOUSEMOTION:
                self.start_button.is_hovered = self.start_button.rect.collidepoint(event.pos)
                
        return True
    
    def tick(self):
        """Control frame rate."""
        self.clock.tick(60)
    
    def is_completed(self):
        """Check if title screen is completed (button clicked)."""
        return self.completed
    
    def reset(self):
        """Reset title screen to initial state."""
        self.current_bg_index = 0
        self.next_bg_index = 1
        self.fade_alpha = 0
        self.hold_timer = 0
        self.is_first_fade = True
        self.first_fade_alpha = 0
        self.completed = False

        