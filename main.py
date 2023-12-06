import pygame
import random
import copy
import time

#  utility functions
def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    """Check to determine which directions are valid from current cell"""
    validdirections = []
    if x != minX: validdirections.append((x-1, y))
    if x != minX and y != minY: validdirections.append((x-1, y-1))
    if x != minX and y != maxY: validdirections.append((x-1, y+1))

    if x!= maxX: validdirections.append((x+1, y))
    if x != maxX and y != minY: validdirections.append((x+1, y-1))
    if x != maxX and y != maxY: validdirections.append((x+1, y+1))

    if y != minY: validdirections.append((x, y-1))
    if y != maxY: validdirections.append((x, y+1))

    return validdirections

def loadImages(path, size):
    """Load an image into the game, and scale the image"""
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img

def loadSpriteSheet(sheet, row, col, newSize, size):
    """creates an empty surface, loads a portion of the spritesheet onto the surface, then return that surface as img"""
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image

def evaluateCoinParity(grid, player):
    score = 0
    abs_grid = [list(abs(x) for x in grid[i]) for i in range(len(grid))]
    score += 100*sum(sum(x) for x in grid) / (sum(sum(x) for x in abs_grid))
    return score


def evaluateCorner(grid, player):
    # Tactical for corner capturing
    
    # Examine all corners, 100 point for each
    score_1 = 0
    score_1 += (grid[0][0] + grid[0][7] + grid[7][0] + grid[7][7])

    # corner_closeness, if a corner is empty, find number of tiles that lead to that corner be captured
    # There are 3 tiles surrounding the corner, so that let 100/3 point for each tile that belongs to enemy
    score_2 = 0
    if grid[0][0] == 0:
        score_2 -= (grid[0][1] + grid[1][1] + grid[1][0])
    if grid[0][7] == 0:
        score_2 -= (grid[0][6] + grid[1][6] + grid[1][7])
    if grid[7][0] == 0:
        score_2 -= (grid[6][0] + grid[6][1] + grid[7][1])
    if grid[7][7] == 0:
        score_2 -= (grid[6][6] + grid[6][7] + grid[7][6])    
        
    return 100*score_1 + 100/3*score_2


def check_stability(grid,dis_post):   
    row,col = dis_post
    disc=grid[row][col]

    if (row,col) in [(0,0),(0,7),(7,0),(7,7)]:
        return 'stable'
    
    for i in (-1,0,1):
        for j in (-1,0,1):
            if i==0 and j==0:
                continue
            
            n_row=row + i
            n_col=col+j
            n_dis_post=(n_row,n_col)

            if 0<=n_row<8  and 0<=n_col<8 and grid[n_row][n_col] == disc :
                return 'stable'

    for i in (-1,0,1):
        for j in (-1,0,1):
            if i==0 and j==0:
                continue

            n_row = row+i
            n_col=col+j

            if 0<=n_row<8 and 0<=n_col<8 and grid[n_row][n_col] != disc and grid[n_row][n_col] != 0:
                N_row=row+i
                N_col=col+j
                
                while 0<=N_row<8 and 0<=N_col<8 and grid[N_row][N_col] !=0:
                    if grid[N_row][N_col] == disc: 
                        return 'unstable'
                    N_row+=i
                    N_col+=j
    return 'semi-stable'


def evaluate_stability(grid,player):
    A = 0
    B = 0

    for row in range(0,7):
        for col in range(0,7):
            disc = grid[row][col]
            disc_pos = (row, col)
            stability = check_stability(grid, disc_pos)

            if disc == -1:
                if stability == 'stable':
                    A += 1
                elif stability == 'semi-stable':
                    A += 0
                elif stability == 'unstable':
                    A += -1
            elif disc == 1:
                if stability == 'stable':
                    B += 1
                elif stability == 'semi-stable':
                    B += 0
                elif stability == 'unstable':
                    B += -1

    if A + B != 0:
        stability_heuristic_value = 100 * (abs(A-B)) / (A+B)
    else:
        stability_heuristic_value = 0

    return stability_heuristic_value


#  Classes
class Othello:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 800))
        pygame.display.set_caption('Othello')

        self.player1 = 1
        self.player2 = -1

        players = [-1, 1]
        self.currentPlayer = int(input())
        self.turn = self.currentPlayer * -1
        self.time = 0

        self.rows = 8
        self.columns = 8

        self.gameOver = False

        self.passGame = False

        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.computerPlayer = ComputerPlayer(self.grid)

        self.RUN = True

    def run(self):
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.grid.printGameLogicBoard()

                if event.button == 1:
                    if self.currentPlayer == 1 and not self.gameOver and not self.passGame:
                        x, y = pygame.mouse.get_pos()
                        x, y = (x - 80) // 80, (y - 80) // 80
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * self.turn )
                        if not validCells:
                            pass
                        else:
                            if (y, x) in validCells:
                                self.grid.insertToken(self.grid.gridLogic, self.currentPlayer * self.turn, y, x)
                                swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer * self.turn)
                                for tile in swappableTiles:
                                    self.grid.animateTransitions(tile, self.currentPlayer * self.turn)
                                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                                self.currentPlayer *= -1
                                self.time = pygame.time.get_ticks()

                    if self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        if x >= 320 and x <= 480 and y >= 400 and y <= 480:
                            self.grid.newGame()
                            self.gameOver = False
                    
                    if self.passGame:                        
                        x, y = pygame.mouse.get_pos()
                        if x >= 775 and x <= 775 + 80 and y >= 300 and y <= 340:
                            # self.grid.newGame()
                            self.passGame = False


    def update(self):
        if self.currentPlayer == -1 :
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100 and not self.passGame:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * self.turn):
                    if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * (-1) * self.turn):
                        self.gameOver = True
                        return
                    else: 
                        self.currentPlayer *= -1
                        self.passGame = True
                cell, score = self.computerPlayer.computerMobility(self.grid.gridLogic, 5, -1000000000, 1000000000, -1 * self.turn)
                self.grid.insertToken(self.grid.gridLogic, self.currentPlayer * self.turn, cell[0], cell[1])
                swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer * self.turn)
                for tile in swappableTiles:
                    self.grid.animateTransitions(tile, self.currentPlayer * self.turn)
                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                self.currentPlayer *= -1

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)
        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * self.turn):
            if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer * (-1) * self.turn):
                self.gameOver = True
                return
            else:
                self.currentPlayer *= -1
                self.passGame = True
    def draw(self):
        bg_color = (195, 161, 159)
        self.screen.fill(bg_color)
        self.grid.drawGrid(self.screen)
        pygame.display.update()



class Grid:
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size
        token_size = (size[0]*7/8, size[1]*7/8)
        self.whitetoken = loadImages('assets/WhiteToken_New.png', token_size)
        self.blacktoken = loadImages('assets/BlackToken_New.png', token_size)
        self.transitionWhiteToBlack = [loadImages(f'assets/BlackToWhite{i}_New.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'assets/WhiteToBlack{i}_New.png', self.size) for i in range(1, 4)]
        self.bg = self.loadBackGroundImages()

        self.tokens = {}

        self.gridBg = self.createbgimg()

        self.gridLogic = self.regenGrid(self.y, self.x)

        self.player1Score = 0
        self.player2Score = 0

        self.font = pygame.font.SysFont('Candara', 40, True, False)

    def newGame(self):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)
        self.currentPlayer = int(input())

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.Surface((80, 80))
        color = (245, 225, 218)
        spriteSheet.fill(color)
        # spriteSheet = pygame.image.load('assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j]+str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (31, 31))
        return imageDict

    def createbgimg(self):
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],
        ]
        image = pygame.Surface((730, 730))
        color = (205, 195, 194)
        image.fill(color)
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        
        image1 = pygame.Surface((70, 730))
        color = (195, 161, 159)
        image1.fill(color)
        
        image2 = pygame.Surface((730, 70))
        color = (195, 161, 159)
        image2.fill(color)
        
        image.blit(image1, (0,0))
        image.blit(image2, (0,0))
        return image

    def regenGrid(self, rows, columns):
        """generate an empty grid for logic use"""
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)
        self.insertToken(grid, 1, 3, 3)
        self.insertToken(grid, -1, 3, 4)
        self.insertToken(grid, 1, 4, 4)
        self.insertToken(grid, -1, 4, 3)

        return grid

    def calculatePlayerScore(self, player):
        score = 0
        for row in self.gridLogic:
            for col in row:
                if col == player:
                    score += 1
        return score

    def drawScore(self, player, score):
        textImg = self.font.render(f'{player} : {score}', 1, (111, 91, 130))
        return textImg

    def endScreen(self):
        if self.GAME.gameOver:
            endScreenImg = pygame.Surface((400, 240))
            endScreenImg.fill((201, 127, 102))
            endText = self.font.render(f'{"Congratulations, You Won!!" if self.player1Score > self.player2Score else "Bad Luck, You Lost" if self.player1Score < self.player2Score else "Draw"}', 1, (245, 225, 218))
            endScreenImg.blit(endText, (40, 40))
            newGame = pygame.draw.rect(endScreenImg, (245, 225, 218), (120, 120, 160, 80))
            newGameText = self.font.render('RETRY', 1, (201, 127, 102))
            endScreenImg.blit(newGameText, (142, 145))
        return endScreenImg


    def passScreen(self):
    
        passScreenImg = pygame.Surface((80, 40))
        
        # endText = self.font.render(f'{"Congratulations, You Won!!" if self.player1Score > self.player2Score else "Bad Luck, You Lost" if self.player1Score < self.player2Score else "Draw"}', 1, 'White')
        # endScreenImg.blit(endText, (0, 0))
        # passGame = pygame.draw.rect(endScreenImg, 'Yellow', (0, 0, 80, 40))
        passGameText = self.font.render('Pass', 1, 'Pink')
        passScreenImg.blit(passGameText, (0, 0))
        return passScreenImg            

    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))

        window.blit(self.drawScore('White', self.player1Score), (775, 100))
        window.blit(self.drawScore('Black', self.player2Score), (775, 200))

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer * self.GAME.turn)
        if self.GAME.currentPlayer == 1:
            for move in availMoves:
                pygame.draw.rect(window, (215, 136, 109), (80 + (move[1] * 80) + 30, 80 + (move[0] * 80) + 30, 20, 20))

        if self.GAME.gameOver:            
            # window.blit(self.endScreen(), (200, 280))
            pass

        if self.GAME.passGame:            
            time.sleep(3)
            window.blit(self.passScreen(), (775, 300))

    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    def findValidCells(self, grid, curPlayer):
        """Performs a check to find all empty cells that are adjacent to opposing player"""
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                if grid[gridX][gridY] != 0:
                    continue
                DIRECTIONS = directions(gridX, gridY)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue

                    if (gridX, gridY) in validCellToClick:
                        continue

                    validCellToClick.append((gridX, gridY))
        return validCellToClick

    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []

        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y
            currentLine = []

            RUN = True
            while RUN:
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                checkX += difX
                checkY += difY

                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False

            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles

    def findAvailMoves(self, grid, currentPlayer):
        """Takes the list of validCells and checks each to see if playable"""
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            #if len(swapTiles) > 0 and cell not in playableCells:
            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells

    def insertToken(self, grid, curplayer, y, x):
        tokenImage = self.whitetoken if curplayer == 1 else self.blacktoken
        self.tokens[(y, x)] = Token(curplayer, y, x, tokenImage, self.GAME)
        grid[y][x] = self.tokens[(y, x)].player

    def animateTransitions(self, cell, player):
        if player == 1:
            self.tokens[(cell[0], cell[1])].transition(self.transitionWhiteToBlack, self.whitetoken)
        else:
            self.tokens[(cell[0], cell[1])].transition(self.transitionBlackToWhite, self.blacktoken)

class Token:
    def __init__(self, player, gridX, gridY, image, main):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 85 + (gridY * 80)
        self.posY = 85 + (gridX * 80)
        self.GAME = main

        self.image = image

    def transition(self, transitionImages, tokenImage):
        for i in range(30):
            self.image = transitionImages[i // 10]
            self.GAME.draw()
        self.image = tokenImage

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))

class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject
        
    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []

        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y
            currentLine = []

            RUN = True
            while RUN:
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                checkX += difX
                checkY += difY

                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False

            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles


    
    def findValidCells(self, grid, curPlayer):
        """Performs a check to find all empty cells that are adjacent to opposing player"""
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                if grid[gridX][gridY] != 0:
                    continue
                DIRECTIONS = directions(gridX, gridY)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue

                    if (gridX, gridY) in validCellToClick:
                        continue

                    validCellToClick.append((gridX, gridY))
        return validCellToClick


    def findAvailMoves(self, grid, currentPlayer):
        """Takes the list of validCells and checks each to see if playable"""
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            #if len(swapTiles) > 0 and cell not in playableCells:
            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells


    
    
    def evaluateMobility( self, grid, player):
        positive = len(self.findAvailMoves(grid, 1))
        negative = len(self.findAvailMoves(grid, -1 ))
        if positive + negative == 0:
            return 0
        else:
            return  100 * (positive - negative) / (positive + negative)
    
    
    # def computerMobility(self, grid, depth, alpha, beta, player):
    #     newGrid = copy.deepcopy(grid)
    #     availMoves = self.grid.findAvailMoves(newGrid, player)

    #     if depth == 0 or len(availMoves) == 0:
    #         bestMove, Score = None, self.evaluateMobility(grid, player)
    #         return bestMove, Score

    #     if player > 0:
    #         bestScore = -1000000000
    #         bestMove = None

    #         for move in availMoves:
    #             x, y = move
    #             swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
    #             newGrid[x][y] = player
    #             for tile in swappableTiles:
    #                 newGrid[tile[0]][tile[1]] = player
                
    #             # If there is a move in one of the corners
    #             # if (x, y) == (0, 0) or (x, y) == (0, 7) or (x, y) == (7, 0) or (x, y) == (7, 7):
    #             #     value = evaluate2(newGrid, player*(-1))
    #             #     bestMove = x, y
    #             #     return bestMove, value
                
    #             # If there is a move which immobilizes the opponent
    #             new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
    #             if len(new_availMoves) == 0:
    #                 value = self.evaluateMobility(newGrid, player*(-1))
    #                 bestMove = x, y
    #                 return bestMove, value

    #             bMove, value = self.computerMobility(newGrid, depth-1, alpha, beta, player*(-1))

    #             if value > bestScore:
    #                 bestScore = value
    #                 bestMove = move
    #             alpha = max(alpha, bestScore)
    #             if beta <= alpha:
    #                 break

    #             newGrid = copy.deepcopy(grid)
    #         return bestMove, bestScore

    #     if player < 0:
    #         bestScore = 1000000000
    #         bestMove = None

    #         for move in availMoves:
    #             x, y = move
    #             swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
    #             newGrid[x][y] = player
    #             for tile in swappableTiles:
    #                 newGrid[tile[0]][tile[1]] = player

    #             # If there is a move in one of the corners
    #             # if (x, y) == (0, 0) or (x, y) == (0, 7) or (x, y) == (7, 0) or (x, y) == (7, 7):
    #             #     value = self.evaluateMobility(newGrid, player*(-1))
    #             #     bestMove = x, y
    #             #     return bestMove, value
                
    #             # If there is a move which immobilizes the opponent
    #             new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
    #             if len(new_availMoves) == 0:
    #                 value = self.evaluateMobility(newGrid, player*(-1))
    #                 bestMove = x, y
    #                 return bestMove, value

    #             bMove, value = self.computerMobility(newGrid, depth-1, alpha, beta, player*(-1))

    #             if value < bestScore:
    #                 bestScore = value
    #                 bestMove = move
    #             beta = min(beta, bestScore)
    #             if beta <= alpha:
    #                 break

    #             newGrid = copy.deepcopy(grid)
    #         return bestMove, bestScore        

    # def computerCornerCapture(self, grid, depth, alpha, beta, player):
    #     newGrid = copy.deepcopy(grid)
    #     availMoves = self.grid.findAvailMoves(newGrid, player)

    #     if depth == 0 or len(availMoves) == 0:
    #         bestMove, Score = None, evaluateCorner(grid, player)
    #         return bestMove, Score

    #     if player > 0:
    #         bestScore = -1000000000
    #         bestMove = None

    #         for move in availMoves:
    #             x, y = move
    #             swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
    #             newGrid[x][y] = player
    #             for tile in swappableTiles:
    #                 newGrid[tile[0]][tile[1]] = player
                
    #             # If there is a move in one of the corners
    #             if (x, y) == (0, 0) or (x, y) == (0, 7) or (x, y) == (7, 0) or (x, y) == (7, 7):
    #                 value = evaluateCorner(newGrid, player*(-1))
    #                 bestMove = x, y
    #                 return bestMove, value
                
    #             # If there is a move which immobilizes the opponent
    #             new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
    #             if len(new_availMoves) == 0:
    #                 value = evaluateCorner(newGrid, player*(-1))
    #                 bestMove = x, y
    #                 return bestMove, value

    #             if (x, y) == (0, 0) or (x, y) == (0, 7) or (x, y) == (7, 0) or (x, y) == (7, 7):
    #                 value = evaluateCorner(newGrid, player*(-1))
    #                 bestMove = x, y
    #                 return bestMove, value
                
    #             bMove, value = self.computerCornerCapture(newGrid, depth-1, alpha, beta, player*(-1))

    #             if value > bestScore:
    #                 bestScore = value
    #                 bestMove = move
    #             alpha = max(alpha, bestScore)
    #             if beta <= alpha:
    #                 break

    #             newGrid = copy.deepcopy(grid)
    #         return bestMove, bestScore

        # if player < 0:
        #     bestScore = 1000000000
        #     bestMove = None

        #     for move in availMoves:
        #         x, y = move
        #         swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
        #         newGrid[x][y] = player
        #         for tile in swappableTiles:
        #             newGrid[tile[0]][tile[1]] = player

        #         # If there is a move in one of the corners
        #         if (x, y) == (0, 0) or (x, y) == (0, 7) or (x, y) == (7, 0) or (x, y) == (7, 7):
        #             value = evaluateCorner(newGrid, player*(-1))
        #             bestMove = x, y
        #             return bestMove, value
                
        #         # If there is a move which immobilizes the opponent
        #         new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
        #         if len(new_availMoves) == 0:
        #             value = evaluateCorner(newGrid, player*(-1))
        #             bestMove = x, y
        #             return bestMove, value

        #         bMove, value = self.computerCornerCapture(newGrid, depth-1, alpha, beta, player*(-1))

        #         if value < bestScore:
        #             bestScore = value
        #             bestMove = move
        #         beta = min(beta, bestScore)
        #         if beta <= alpha:
        #             break

        #         newGrid = copy.deepcopy(grid)
        #     return bestMove, bestScore
        
    def Everything(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, evaluateCorner(grid, player) + evaluate_stability(grid, player) + evaluateCoinParity(grid, player) + self.evaluateMobility(grid, player)
            return bestMove, Score

        if player > 0:
            bestScore = -1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                

                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1))  + evaluate_stability(grid, player * (-1)) + evaluateCoinParity(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value


                
                bMove, value = self.Everything(newGrid, depth-1, alpha, beta, player*(-1))

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = 1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1))  + evaluate_stability(grid, player * (-1)) + evaluateCoinParity(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value

                bMove, value = self.Everything(newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore
        

    def E_coins(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, evaluateCorner(grid, player) + evaluate_stability(grid, player) + self.evaluateMobility(grid, player)
            return bestMove, Score

        if player > 0:
            bestScore = -1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                

                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1))  + evaluate_stability(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value


                
                bMove, value = self.E_coins(newGrid, depth-1, alpha, beta, player*(-1))

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = 1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1))  + evaluate_stability(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value

                bMove, value = self.E_coins(newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore
        
    def E_corner(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None,evaluate_stability(grid, player) + evaluateCoinParity(grid, player) + self.evaluateMobility(grid, player)
            return bestMove, Score

        if player > 0:
            bestScore = -1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                

                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value =  evaluate_stability(grid, player * (-1)) + evaluateCoinParity(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value


                
                bMove, value = self.E_corner(newGrid, depth-1, alpha, beta, player*(-1))

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = 1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluate_stability(grid, player * (-1)) + evaluateCoinParity(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value

                bMove, value = self.E_corner(newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

    def E_mobility(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, evaluateCorner(grid, player) + evaluate_stability(grid, player) + evaluateCoinParity(grid, player)
            return bestMove, Score

        if player > 0:
            bestScore = -1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                

                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1))  + evaluate_stability(grid, player * (-1)) + evaluateCoinParity(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value


                
                bMove, value = self.E_mobility(newGrid, depth-1, alpha, beta, player*(-1))

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = 1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1))  + evaluate_stability(grid, player * (-1)) + evaluateCoinParity(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value

                bMove, value = self.E_mobility(newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore
    

    def E_stability(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, evaluateCorner(grid, player) + evaluateCoinParity(grid, player) + self.evaluateMobility(grid, player)
            return bestMove, Score

        if player > 0:
            bestScore = -1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                

                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1)) + evaluateCoinParity(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value


                
                bMove, value = self.E_stability(newGrid, depth-1, alpha, beta, player*(-1))

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = 1000000000
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player
                
                # If there is a move which immobilizes the opponent
                new_availMoves = self.grid.findAvailMoves(newGrid, player*(-1))
                if len(new_availMoves) == 0:
                    value = evaluateCorner(newGrid, player*(-1)) + evaluateCoinParity(grid, player * (-1)) + self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value

                bMove, value = self.E_stability(newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore



if __name__ == '__main__':
    game = Othello()
    game.run()
    pygame.quit()