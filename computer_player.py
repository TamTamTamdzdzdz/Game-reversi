import copy
from grid import *

# Evaluation functions for heuristics

# Coin Parity
def evaluateCoinParity(grid, player):
    score = 0
    abs_grid = [list(abs(x) for x in grid[i]) for i in range(len(grid))]
    score += 100*sum(sum(x) for x in grid) / (sum(sum(x) for x in abs_grid))
    return score

# Corner
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

# Utility function for stability
def checkFlankNextMove(grid, position):
    '''Check if a disc could be flanked in the very next move.'''

    r, c = position

    # If the position has no disk, return False
    if grid[r][c] == 0:
        return False
    
    player = grid[r][c]
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    # Loop all possible directions
    for (i, j) in directions:
        row, col = r, c
        
        # Find the first tile that doesn't contain a player's disk in the direction
        while 0 <= row <= 7 and 0 <= col <= 7 and grid[row][col] == player:
            row, col = row + i, col + j
        
        # If there are full of player's disk in the direction or the first tile found is empty,
        # continue to the next direction
        if row in {-1, 8} or col in {-1, 8} or grid[row][col] == 0:
            continue

        # Else, find the first tile that doesn't contain a player's disk in the reverse direction.
        # If the tile is empty, then the original disc could be flanked in the very next move.
        else:
            row, col = r, c
            while 0 <= row <= 7 and 0 <= col <= 7 and grid[row][col] == player:
                row, col = row - i, col - j
            if 0 <= row <= 7 and 0 <= col <= 7 and grid[row][col] == 0:
                return True
    return False

def stabilityValue(grid):
    """Return a list of stability value."""

    # 1 for stable, 0 for semi-stable, and -1 for unstable

    # First, we determine unstable discs.
    ans = [[0 for j in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            # If the disc could be flanked in the next move, it is unstable
            if checkFlankNextMove(grid, (i, j)):
                ans[i][j] = -1

    # Next, we determine stable discs.
    # A disk is called 'stable' in a specific direction if it can not be flipped in that direction,
    # i.e, at least 1 of 3 following conditions hold:
    # (i) All tiles in the direction are not empty.
    # (ii) The disk is one of two endpoints of the direction.
    # (iii) The disk is adjacent (in the direction) to another stable disk in the direction.
    # A disk is called 'stable' if it is stable in all 4 direction (horizontal, vertical, upward diagonal and downward diagonal)

    # Here, each value of the return list is a boolean 4-tuple (x, y, z, t), where (x, y, z, t) represents the stability
    # in 4 direction horizontal, vertical, upward diagonal and downward diagonal, respectively.
    # A disk is stable if its stability value is (True, True, True, True)

    stability = [[[0, 0, 0, 0] for j in range(8)] for i in range(8)]

    # Assign the stability value according to the condition (ii).

    # All corners are stable in all 4 directions.
    for i, j in [(0, 0), (0, 7), (7, 0), (7, 7)]:
        if grid[i][j] != 0:
            stability[i][j] = [1, 1, 1, 1]
    
    # All tiles in the edge are stable in at least 3 directions.
    # The upper edge and the lower edge.
    for i in [0, 7]:
        for j in range(1, 7):
            if grid[i][j] != 0:
                stability[i][j] = [0, 1, 1, 1]
    
    # The left edge and the right edge.
    for j in [0, 7]:
        for i in range(1, 7):
            if grid[i][j] != 0:
                stability[i][j] = [1, 0, 1, 1]
    
    horizontal = [(0, 1), (0, -1)]
    vertical = [(1, 0), (-1, 0)]
    upward_diagonal = [(1, 1), (-1, -1)]
    downward_diagonal = [(1, -1), (-1, 1)]

    # Assign the stability value according to the condition (i).
    for i in range(8):
        for j in range(8):
            # If the tile has no disc, continue. 
            if grid[i][j] == 0:
                continue

            # If the tile is a corner, continue.
            if (i, j) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                continue

            # If the disc is not stable in a direction, we check if the direction is full of discs.
            # If so, then update the stability value of the disc.

            # Horizontal direction
            if stability[i][j][0] == 0:
                x, y = horizontal[0]
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r + x, c + y
                if 0 <= r <= 7 and 0 <= c <= 7:
                    continue
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r - x, c - y
                if r in {-1, 8} or c in {-1, 8}:
                    stability[i][j][0] = 1
            
            # Vertical direction
            if stability[i][j][1] == 0:
                x, y = vertical[0]
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r + x, c + y
                if 0 <= r <= 7 and 0 <= c <= 7:
                    continue
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r - x, c - y
                if r in {-1, 8} or c in {-1, 8}:
                    stability[i][j][1] = 1
            
            # Upward diagonal direction
            if stability[i][j][2] == 0:
                x, y = upward_diagonal[0]
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r + x, c + y
                if 0 <= r <= 7 and 0 <= c <= 7:
                    continue
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r - x, c - y
                if r in {-1, 8} or c in {-1, 8}:
                    stability[i][j][2] = 1

            # Downward diagonal direction
            if stability[i][j][3] == 0:
                x, y = downward_diagonal[0]
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r + x, c + y
                if 0 <= r <= 7 and 0 <= c <= 7:
                    continue
                r, c = i, j
                while 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] != 0:
                    r, c = r - x, c - y
                if r in {-1, 8} or c in {-1, 8}:
                    stability[i][j][3] = 1


    # Iterate all discs and update their stability value until nothing changes.
    change = True
    while change:
        change = False
        for i in range(8):
            for j in range(8):
                # If the tile has no disc, continue. 
                if grid[i][j] == 0:
                    continue

                # If the tile is a corner, continue.
                if (i, j) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                    continue

                # If the disc is not stable in a direction, we iterate 2 neighbors in the direction.
                # If at least 1 neighbor has the same color and is stable in the direction, we update the stability value of the disc.

                # Horizontal direction.
                if stability[i][j][0] == 0:
                    for x, y in horizontal:
                        r, c = i + x, j + y
                        if 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] == grid[i][j] and stability[r][c][0] == 1:
                            stability[i][j][0] = 1
                            change = True
                
                # Vertical direction.
                if stability[i][j][1] == 0:
                    for x, y in vertical:
                        r, c = i + x, j + y
                        if 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] == grid[i][j] and stability[r][c][1] == 1:
                            stability[i][j][1] = 1
                            change = True

                # Upward diagonal direction.
                if stability[i][j][2] == 0:
                    for x, y in upward_diagonal:
                        r, c = i + x, j + y
                        if 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] == grid[i][j] and stability[r][c][2] == 1:
                            stability[i][j][2] = 1
                            change = True

                # Downward diagonal direction.
                if stability[i][j][3] == 0:
                    for x, y in downward_diagonal:
                        r, c = i + x, j + y
                        if 0 <= r <= 7 and 0 <= c <= 7 and grid[r][c] == grid[i][j] and stability[r][c][3] == 1:
                            stability[i][j][3] = 1
                            change = True

    for i in range(8):
        for j in range(8):
            # If stability[i][j] is (True, True, True, True), then the disc in (i, j) is stable.
            if stability[i][j] == [1, 1, 1, 1]:
                ans[i][j] = 1
    
    return ans

# Stability
def evaluate_stability(grid,player):
    A = 0
    B = 0

    stabilityVal = stabilityValue(grid)

    for i in range(8):
        for j in range(8):
            if grid[i][j] == -1:
                A += stabilityVal[i][j]
            elif grid[i][j] == 1:
                B += stabilityVal[i][j]
    
    if A + B == 0:
        return 0
    return 100*(A-B)/(A+B)

# Static Board
def evaluateStaticBoard(grid, player):
    score = 0
    staticBoard = [
        [100, -20, 10, 5, 10, -20, 100], 
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, -1, -1, -1, -1, -2, 10],
        [5, -2, -1, -1, -1, -1, -2, 5],
        [5, -2, -1, -1, -1, -1, -2, 5],
        [10, -2, -1, -1, -1, -1, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10, 5, 10, -20, 100]
    ]
    for i in range(8):
        for j in range(8):
            score += grid[i][j]*staticBoard[i][j]
    return score

# Mobility
def evaluateMobility(self, grid, player):
    positive = len(self.findAvailMoves(grid, 1))
    negative = len(self.findAvailMoves(grid, -1 ))
    if positive + negative == 0:
        return 0
    else:
        return  100 * (positive - negative) / (positive + negative)

# Define the ComputerPlayer class
class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject
    
    def swappableTiles(self, x, y, grid, player):
        '''Return list of tiles that can be swapped after a move.'''

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
        """Performs a check to find all empty cells that are adjacent to opposing player."""

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
        """Takes the list of validCells and checks each to see if playable.
        Return the list of available moves."""

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

    def evaluateMobility(self, grid, player):
        positive = len(self.findAvailMoves(grid, 1))
        negative = len(self.findAvailMoves(grid, -1 ))
        if positive + negative == 0:
            return 0
        else:
            return  100 * (positive - negative) / (positive + negative)
    
    # Heuristic functions

    def computerMobility(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(0, 0, 1, 0, grid, depth, alpha, beta, player)       
    
    def computerCoinParity(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(0, 1, 0, 0, grid, depth, alpha, beta, player)

    def computerStability(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(0, 0, 0, 1, grid, depth, alpha, beta, player)

    def computerCornerCapture(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(1, 0, 0, 0, grid, depth, alpha, beta, player)

    def Everything(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(1, 1, 1, 1, grid, depth, alpha, beta, player)
    
        
    def E_coins(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(1, 0, 1, 1, grid, depth, alpha, beta, player)
        
    def E_corner(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(0, 1, 1, 1, grid, depth, alpha, beta, player)

    def E_mobility(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(1, 1, 0, 1, grid, depth, alpha, beta, player)
    def E_stability(self, grid, depth, alpha, beta, player):
        return self.EverythingRate(1, 1, 1, 0, grid, depth, alpha, beta, player)

    def computerStaticBoard(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, evaluateStaticBoard(newGrid, player)
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
                
                bMove, value = self.computerStaticBoard(newGrid, depth-1, alpha, beta, player*(-1))

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
                
                bMove, value = self.computerStaticBoard(newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore
        
    def EverythingRate(self, corn, coin, mob, sta, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, corn * evaluateCorner(grid, player) + sta * evaluate_stability(grid, player) +\
                            coin * evaluateCoinParity(grid, player) + mob * self.evaluateMobility(grid, player)
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
                    value = corn * evaluateCorner(newGrid, player*(-1))  + sta * evaluate_stability(grid, player * (-1)) + \
                        coin * evaluateCoinParity(grid, player * (-1)) + mob * self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value
                
                bMove, value = self.EverythingRate(corn, coin, mob, sta, newGrid, depth-1, alpha, beta, player*(-1))

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
                    value = corn * evaluateCorner(newGrid, player*(-1))  + sta * evaluate_stability(grid, player * (-1)) + \
                        coin * evaluateCoinParity(grid, player * (-1)) + mob * self.evaluateMobility(grid, player * (-1))
                    bestMove = x, y
                    return bestMove, value

                bMove, value = self.EverythingRate(corn, coin, mob, sta, newGrid, depth-1, alpha, beta, player*(-1))

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            
            return bestMove, bestScore