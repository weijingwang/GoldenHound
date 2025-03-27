import pygame
import noise
import numpy as np

class AssetManager:
    """Manages loading and caching of game assets."""
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def load_image(self, path, convert=True):
        """
        Load and cache an image.
        
        Args:
            path (str): Path to the image file
            convert (bool): Whether to convert image for faster rendering
        
        Returns:
            pygame.Surface: Loaded and cached image
        """
        if path not in self.images:
            try:
                image = pygame.image.load(path)
                self.images[path] = image.convert_alpha() if convert else image
            except pygame.error as e:
                print(f"Error loading image {path}: {e}")
                # Fallback to a default image or surface
                self.images[path] = pygame.Surface((50, 50), pygame.SRCALPHA)
        return self.images[path]

    def load_sound(self, path, volume=1.0):
        """
        Load and cache a sound.
        
        Args:
            path (str): Path to the sound file
            volume (float): Volume level for the sound
        
        Returns:
            pygame.mixer.Sound: Loaded and cached sound
        """
        if path not in self.sounds:
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                self.sounds[path] = sound
            except pygame.error as e:
                print(f"Error loading sound {path}: {e}")
                # Fallback to a silent sound
                self.sounds[path] = pygame.mixer.Sound(None)
        return self.sounds[path]


class PerlinNoiseOverlay:
    def __init__(self, width, height, noise_width=25, noise_height=100, scale=0.05, alpha=60):
        self.width = width
        self.height = height
        self.noise_width = noise_width
        self.noise_height = noise_height
        self.scale = scale
        self.alpha = alpha
        self.time = 0
    
    def generate(self):
        """Generates a Perlin noise texture."""
        x_vals, y_vals = np.meshgrid(
            np.linspace(0, self.noise_width * self.scale, self.noise_width),
            np.linspace(0, self.noise_height * self.scale, self.noise_height)
        )

        noise_array = np.vectorize(lambda x, y: noise.pnoise3(x, y, self.time * 0.1, octaves=3))(x_vals, y_vals)
        noise_array = ((noise_array + 1) * 127.5).astype(np.uint8)  # Normalize to 0-255

        surface = pygame.Surface((self.noise_width, self.noise_height))
        noise_rgb = np.stack([noise_array.T] * 3, axis=-1)  # Convert grayscale to RGB
        pygame.surfarray.blit_array(surface, noise_rgb)
        
        surface.set_alpha(self.alpha)  # Adjust transparency
        return pygame.transform.scale(surface, (self.width, self.height)).convert_alpha()  # Upscale
    
    def update(self):
        self.time += 1  # Increment time for animation
