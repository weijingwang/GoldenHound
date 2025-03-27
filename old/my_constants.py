WIDTH, HEIGHT = 1280, 720

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 180, 0)  # Background color for "grass"
YELLOW = (255, 255, 0)  # Color for panicked enemies
ORANGE = (255, 140, 0)  # Color for chain-reaction panicked enemies

# Enemy behavior states
GRAZING = 0    # Moving slowly in one direction
STANDING = 1   # Not moving
WALKING = 2    # Moving at normal speed
PANICKING = 3  # Moving frantically after being startled