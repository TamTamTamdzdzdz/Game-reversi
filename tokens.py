# Define Token class.
class Token:
    def __init__(self, player, gridX, gridY, image, main):
        # Initialize some attributes of a token: color (player), position, game, image.
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 85 + (gridY * 80)
        self.posY = 85 + (gridX * 80)
        self.GAME = main
        self.image = image

    def transition(self, transitionImages, tokenImage):
        '''For token transition.'''

        for i in range(30):
            # Change the image of the token and draw it on the screen.
            self.image = transitionImages[i // 10]
            self.GAME.draw()

        # Final image of the token.
        self.image = tokenImage

    def draw(self, window):
        '''Draw the token on the screen.'''
        window.blit(self.image, (self.posX, self.posY))