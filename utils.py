import pygame

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
