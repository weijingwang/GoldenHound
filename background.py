import pygame
import noise
import numpy as np

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
        return pygame.transform.scale(surface, (self.width, self.height))  # Upscale
    
    def update(self):
        self.time += 1  # Increment time for animation
