import pygame
import sys
from swimming_game import SwimmingGame
from title import TitleScreen
from animate_intro import GameIntro

def main():
    pygame.init()
    
    # Create game states
    title_screen = TitleScreen()
    intro = GameIntro()  # Your previous animation class
    swimming_game = SwimmingGame()  # Add your swimming game
    
    # Main game state
    current_state = "title"
    running = True
    
    while running:
        # Handle events based on current state
        if current_state == "title":
            running = title_screen.handle_events()
        elif current_state == "intro":
            running = intro.handle_events()
        elif current_state == "swimming":
            running = swimming_game._handle_events()  # Using your existing method
        # Handle other states...
        
        if not running:
            break
            
        # Update based on current state
        if current_state == "title":
            if title_screen.update():
                current_state = "intro"  # Move to intro animations
        elif current_state == "intro":
            if intro.update():
                current_state = "swimming"  # Move to swimming game
        elif current_state == "swimming":
            if not swimming_game.game_over:
                game_continues = swimming_game._update_game_state()
                if not game_continues:
                    swimming_game.game_over = True
                    # You can add transition to another state here
                    # current_state = "some_other_state"
        # Update other states...
        
        # Render based on current state
        if current_state == "title":
            title_screen.render()
        elif current_state == "intro":
            intro.render()
        elif current_state == "swimming":
            swimming_game._draw()  # Using your existing method
        # Render other states...
        
        # Control timing
        if current_state == "title":
            title_screen.tick()
        elif current_state == "intro":
            intro.tick()
        elif current_state == "swimming":
            swimming_game.clock.tick(60)  # Using your existing clock
        # Control timing for other states...
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()