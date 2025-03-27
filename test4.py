import pygame
import noise
import numpy as np

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.noise_width, self.noise_height = 200, 150  # Lower resolution noise
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.time = 0  # Time variable for animated noise

    def generate_noise_texture(self, scale=0.1):
        """Generates a Perlin noise texture at a lower resolution"""
        x_vals, y_vals = np.meshgrid(
            np.linspace(0, self.noise_width * scale, self.noise_width), 
            np.linspace(0, self.noise_height * scale, self.noise_height)
        )

        noise_array = np.vectorize(lambda x, y: noise.pnoise3(x, y, self.time * 0.1, octaves=3))(x_vals, y_vals)
        noise_array = ((noise_array + 1) * 127.5).astype(np.uint8)  # Normalize to 0-255

        surface = pygame.Surface((self.noise_width, self.noise_height))
        noise_rgb = np.stack([noise_array.T] * 3, axis=-1)  # Ensure correct shape
        pygame.surfarray.blit_array(surface, noise_rgb)  

        surface.set_alpha(60)  # Adjust transparency
        return pygame.transform.scale(surface, (self.width, self.height))  # Upscale

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((135, 206, 235))  # Sky blue background
            
            # Generate and overlay noise texture
            noise_surface = self.generate_noise_texture()
            self.screen.blit(noise_surface, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)
            self.time += 1  # Increment time for animation

        pygame.quit()

if __name__ == "__main__":
    Game().run()