import pygame

# Define Button class.
class Button:
    def __init__(self, text, x, y, fontsize=40):
        # Initialize some attributes: text on the button, font of the text, position of the button
        # and a boolean attribute to check if the button is clicked.

        self.font = pygame.font.SysFont('Candara', fontsize, True, False)
        self.text = self.font.render(text, 1, (111, 91, 130))
        self.rect = self.text.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = True
    
    def draw(self, screen):
        """Draw the button on your screen. Return True if the button is clicked."""

        action = False
        
        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check if the button is clicked
        if self.rect.collidepoint(pos):
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False
            elif pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        else:
            self.clicked = True

        # Draw the button on the screen
        screen.blit(self.text, self.rect.topleft)

        return action