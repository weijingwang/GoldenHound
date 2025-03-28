import pygame
import sys
from utils import PerlinNoiseOverlay

def animate_intro1():
    pygame.init()
    
    noise_overlay = PerlinNoiseOverlay(1280, 720, 200, 150, scale=0.5, alpha=20)


    # Load background image
    bg = pygame.image.load("assets/images/intro1/intro1_bg.png")
    screen = pygame.display.set_mode(bg.get_size())
    
    # Load intro images
    frames = [pygame.image.load(f"assets/images/intro1/intro{i}.png") for i in range(1, 13)]
    
    # Set custom frame durations (in milliseconds)
    # Example: The first frame lasts 500ms, second frame 1000ms, etc.
    frame_durations = [500, 500, 100, 200, 100, 100, 100, 200, 200, 200, 200, 800]  # Custom timings
    
    clock = pygame.time.Clock()
    running = True
    frame_index = 0
    time_accumulator = 0
    
    while running and frame_index < len(frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        
        dt = clock.tick(60)  # Get time passed since last frame (limit to 60 FPS)
        time_accumulator += dt
        
        # Advance frame if the duration has elapsed
        if time_accumulator >= frame_durations[frame_index]:
            time_accumulator = 0
            frame_index += 1
            if frame_index >= len(frames):
                break  # Exit loop after last frame
        

        screen.blit(bg, (0, 0))
        screen.blit(frames[frame_index], (0, 0))
        noise_surface = noise_overlay.generate()
        screen.blit(noise_surface, (0, 0))
        noise_overlay.update()
        pygame.display.flip()

    