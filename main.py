import pygame
import sys
from swimming_game import SwimmingGame
from title import TitleScreen
from animate_intro import *
from fade_in_frame import FadeInOutFrame

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("Pyweek 39: Golden Hound")

    # Set up screen - assuming the screen size from context
    screen = pygame.display.set_mode((1280, 720))

    # Load and play title music once at the beginning
    pygame.mixer.music.load("assets/sounds/mountain.ogg")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    
    # Main game state
    current_state = "swimming"
    previous_state = None  # Track the previous state
    running = True

    # Create game states
    title_screen = TitleScreen()
    intro = GameIntro()
    swimming_game = SwimmingGame()
    
    # Create end scene states
    end_1 = CurveAnimation(start_size=20, end_size=400, k=0.005, back=1)
    end_1.set_waypoints([(508, 390), (600, 475), (415, 529), (590, 672)])
    
    end_3 = CurveAnimation(start_size=20, end_size=400, k=0.005, back=2)
    end_3.set_waypoints([(448, 341), (576, 434), (328, 581), (1231, 683)])

    # Load all end game images
    end_2_img = pygame.image.load("assets/images/end_frame_2.png").convert_alpha()
    end_4_img = pygame.image.load("assets/images/end_frame_3.png").convert_alpha()
    end_5_img = pygame.image.load("assets/images/end_frame_4.png").convert_alpha()
    end_6_img = pygame.image.load("assets/images/end_frame_5.png").convert_alpha()
    end_7_img = pygame.image.load("assets/images/end_frame_6.png").convert_alpha()
    
    # Create FadeInOutFrame objects for each end state
    end_2 = FadeInOutFrame(screen, end_2_img, fade_duration=1.5, stay_duration=3.0)
    end_4 = FadeInOutFrame(screen, end_4_img, fade_duration=1.5, stay_duration=3.0)
    end_5 = FadeInOutFrame(screen, end_5_img, fade_duration=1.5, stay_duration=3.0)
    end_6 = FadeInOutFrame(screen, end_6_img, fade_duration=1.5, stay_duration=3.0)
    end_7 = FadeInOutFrame(screen, end_7_img, fade_duration=1.5, stay_duration=4.0, last_slide=True)
    
    # Clock for managing delta time
    clock = pygame.time.Clock()
    dt = 0  # delta time for animations
    
    # Variables to track animation completion
    end_1_complete = False
    end_3_complete = False

    while running:
        print(current_state)
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         sys.exit()
        # Calculate delta time in seconds
        dt = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
        
        # Handle state change and music transitions
        if current_state != previous_state:
            if current_state == "swimming" and previous_state != "swimming":
                # Switch music only when first entering swimming state
                pygame.mixer.music.load("assets/sounds/pastoral_cut.ogg")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            elif current_state == "end" and previous_state == "swimming":
                # When transitioning from swimming to end after the fade
                # Start the end state music
                pygame.mixer.music.load("assets/sounds/victory.ogg")  # Assuming you have this file
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            
            previous_state = current_state
        
        
        # Additional event handling from original code
        if current_state == "title":
            running = title_screen.handle_events()
        elif current_state == "intro":
            running = intro.handle_events()
        elif current_state == "swimming":
            running = swimming_game._handle_events()
        elif current_state == "end":
            running = end_1.handle_events()
        elif current_state == "end_3":
            running = end_3.handle_events()
            
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
            
            # Check for state transition after drawing
            next_state = swimming_game._draw()
            if next_state == "end":
                current_state = "end"
        elif current_state == "end":
            # Update animation and check if it's complete based on a timer or condition
            end_1.update()
            # Check animation completion (will need a custom way to determine when it's done)
            animation_duration = 5.0  # Example: 5 seconds for animation
            end_1_timer = getattr(end_1, 'timer', 0) + dt
            setattr(end_1, 'timer', end_1_timer)
            if end_1_timer >= animation_duration:
                end_1_complete = True
            
            if end_1_complete:
                current_state = "end_2"
                end_1_complete = False  # Reset for next time
        elif current_state == "end_2":
            if not end_2.update(dt):
                current_state = "end_3"
        elif current_state == "end_3":
            end_3.update()
            # Similar timing mechanism for end_3
            animation_duration = 5.0  # Example: 5 seconds for animation
            end_3_timer = getattr(end_3, 'timer', 0) + dt
            setattr(end_3, 'timer', end_3_timer)
            if end_3_timer >= animation_duration:
                end_3_complete = True
                
            if end_3_complete:
                current_state = "end_4"
                end_3_complete = False  # Reset for next time
        elif current_state == "end_4":
            if not end_4.update(dt):
                current_state = "end_5"
        elif current_state == "end_5":
            if not end_5.update(dt):
                current_state = "end_6"
        elif current_state == "end_6":
            if not end_6.update(dt):
                current_state = "end_7"
        elif current_state == "end_7":
            # Last slide stays visible until user quits
            end_7.update(dt)
        
        # Render based on current state
        if current_state == "title":
            screen.fill((0, 0, 0))  # Clear screen
            title_screen.render()
        elif current_state == "intro":
            screen.fill((0, 0, 0))  # Clear screen
            intro.render()
        elif current_state == "swimming":
            # Swimming game handles its own rendering in _draw
            pass
        elif current_state == "end":
            screen.fill((0, 0, 0))  # Clear screen
            end_1.render()
        elif current_state == "end_2":
            screen.fill((0, 0, 0))  # Clear screen
            end_2.draw()
        elif current_state == "end_3":
            screen.fill((0, 0, 0))  # Clear screen
            end_3.render()
        elif current_state == "end_4":
            screen.fill((0, 0, 0))  # Clear screen
            end_4.draw()
        elif current_state == "end_5":
            screen.fill((0, 0, 0))  # Clear screen
            end_5.draw()
        elif current_state == "end_6":
            screen.fill((0, 0, 0))  # Clear screen
            end_6.draw()
        elif current_state == "end_7":
            screen.fill((0, 0, 0))  # Clear screen
            end_7.draw()
        
        # Update the display
        pygame.display.flip()
        
        # Control timing - following original pattern from your code
        if current_state == "title":
            title_screen.tick()
        elif current_state == "intro":
            intro.tick()
        elif current_state == "swimming":
            swimming_game.clock.tick(60)
        elif current_state == "end":
            # Use transition approach from original code
            if end_1_complete:
                current_state = "end_2"
        elif current_state == "end_2":
            # Timing handled by FadeInOutFrame
            pass
        elif current_state == "end_3":
            # Use transition approach from original code
            if end_3_complete:
                current_state = "end_4"
        elif current_state == "end_4" or current_state == "end_5" or current_state == "end_6" or current_state == "end_7":
            # Timing handled by FadeInOutFrame
            pass
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()