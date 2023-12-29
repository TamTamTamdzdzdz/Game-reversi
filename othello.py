import pygame
from button import *
from computer_player import *
from grid import *
from tokens import *
from color import Color

# Define the Othello game class
class Othello:
    def __init__(self):

        pygame.init()
        self.color = Color()
        # Set the size of the screen
        self.screen = pygame.display.set_mode((1000, 800))

        # Set the title of the window
        pygame.display.set_caption('Othello')

        self.player1 = -1
        self.player2 = 1

        # Color of the player
        self.playerSide = -1

        self.currentPlayer = -1
        self.time = 0
        self.lastMove = None

        self.rows = 8
        self.columns = 8

        # Some attributes for drawing main menu, opponent selection, depth selection
        # and color selection menu.
        self.menu = False
        self.opponentSelected = False
        self.depthSelected = False
        self.sideSelected = False

        self.gameOver = False
        self.paused = False
        self.passGame = False

        # Initialize the grid, computer player, heuristic and depth chosen.
        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.computerPlayer = ComputerPlayer(self.grid)
        self.heuristic = None
        self.depth = 1

        self.RUN = True

    def run(self):
        '''Run the game loop.'''

        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        '''Handle input from user.'''

        for event in pygame.event.get():
            # Quit game
            if event.type == pygame.QUIT:
                self.RUN = False

            if self.sideSelected:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If right mouse button is clicked, print the logical grid.
                    if event.button == 3:
                        self.grid.printGameLogicBoard()

                    # If left mouse button is clicked
                    if event.button == 1:
                        if self.currentPlayer == self.playerSide and not self.gameOver and not self.passGame and not self.paused:
                            x, y = pygame.mouse.get_pos()
                            x, y = (x - 80) // 80, (y - 80) // 80
                            validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                            if not validCells:
                                pass
                            else:
                                # If click on a valid cell
                                if (y, x) in validCells:
                                    self.lastMove = (y, x)
                                    # Insert a token into the cell
                                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)
                                    swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                                    # Swap all swappable tiles
                                    for tile in swappableTiles:
                                        self.grid.animateTransitions(tile, self.currentPlayer)
                                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                                    self.currentPlayer *= -1
                                    self.time = pygame.time.get_ticks()

                        # If the game is over
                        if self.gameOver:
                            x, y = pygame.mouse.get_pos()
                            if x >= 320 and x <= 480 and y >= 400 and y <= 480:
                                self.grid.newGame()
                                self.gameOver = False
                        
                        # If a player has no moves left
                        if self.passGame:                        
                            x, y = pygame.mouse.get_pos()
                            if x >= 775 and x <= 855 and y >= 300 and y <= 340:
                                self.passGame = False

    def update(self):
        '''Update the game state.'''

        if self.sideSelected:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if self.currentPlayer != self.playerSide:
                    if not self.passGame:
                        # If the opponent has no more moves
                        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                            # If the player also has no more moves, end the game
                            if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * (-1)):
                                self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
                                self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)
                                self.gameOver = True
                                return
                            # Else, pass the turn to the player.
                            else:
                                self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
                                self.grid.player2Score = self.grid.calculatePlayerScore(self.player2) 
                                self.currentPlayer *= -1
                                return
                        # Opponent's next move.
                        if self.heuristic == self.computerPlayer.EverythingRate:
                            cell, score = self.computerPlayer.EverythingRate(1, 1, 1, 1, self.grid.gridLogic, self.depth, -1000000000, 1000000000, self.currentPlayer)
                        else:
                            cell, score = self.heuristic(self.grid.gridLogic, self.depth, -1000000000, 1000000000, self.currentPlayer)
                        self.lastMove = cell

                        # Insert a token for the last move and swap tiles.
                        self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                        swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                        for tile in swappableTiles:
                            self.grid.animateTransitions(tile, self.currentPlayer)
                            self.grid.gridLogic[tile[0]][tile[1]] *= -1

                        self.currentPlayer *= -1

        # Recalculate scores of 2 players.
        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

        # If the player has no more moves
        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
            # If the opponent also has no more moves
            if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * (-1)):
                self.gameOver = True
                return
            # Else, pass the turn to the opponent.
            else:
                self.currentPlayer *= -1
                self.passGame = True
        
    def draw(self):
        '''Draw the game screen.'''
        bg_color = self.color.pinkBg
        self.screen.fill(bg_color)
        self.grid.drawGrid(self.screen)
        pygame.display.update()