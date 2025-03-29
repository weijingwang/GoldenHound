import pygame
import sys
from swimming_game import SwimmingGame
from title import TitleScreen
from animate_intro import *

def main():
    pygame.init()
    pygame.mixer.init()
    
    # Load and play title music once at the beginning
    pygame.mixer.music.load("assets/sounds/mountain.ogg")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    
    # Create game states
    end_animation = CurveAnimation(start_size=20, end_size=400, k=0.005, back=1)
    end_animation.set_waypoints([(508, 390), (600, 475), (415, 529), (590, 672)])

    title_screen = TitleScreen()
    intro = GameIntro()
    swimming_game = SwimmingGame()
    
    # Main game state
    current_state = "title"
    previous_state = None  # Track the previous state
    running = True
    
    while running:
        if current_state == "end":
            end_animation.render()

            end_animation.update()
            # end_animation.tick()
        # Handle state change and music transitions
        if current_state != previous_state:
            if current_state == "swimming" and previous_state != "swimming":
                # Switch music only when first entering swimming state
                pygame.mixer.music.load("assets/sounds/pastoral_cut.ogg")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            # Add more state-specific music changes here if needed
            
            previous_state = current_state
        
        # Handle events based on current state
        if current_state == "title":
            running = title_screen.handle_events()
        elif current_state == "intro":
            running = intro.handle_events()
        elif current_state == "swimming":
            running = swimming_game._handle_events()
        elif current_state == "end":
            running = end_animation.handle_events()
        
        if not running:
            break
            
        # Update based on current state
        if current_state == "title":
            if title_screen.update():
                current_state = "intro"
        elif current_state == "intro":
            if intro.update():
                current_state = "swimming"
        elif current_state == "swimming":
            if not swimming_game.game_over:
                game_continues = swimming_game._update_game_state()
                if not game_continues:
                    swimming_game.game_over = True
                    # You can add transition to another state here
        
        # Render based on current state
        if current_state == "title":
            title_screen.render()
        elif current_state == "intro":
            intro.render()
        elif current_state == "swimming":
            swimming_game._draw()
        
        # Control timing
        if current_state == "title":
            title_screen.tick()
        elif current_state == "intro":
            intro.tick()
        elif current_state == "swimming":
            swimming_game.clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()