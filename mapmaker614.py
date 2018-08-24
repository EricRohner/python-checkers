import random, pygame, sys
from pygame.locals import *

#Define globals
GAMETIME = 0
NEXTTOPLAY = 0
PLAYERS = 3
FPS = 30
HEXWIDTH = 60
HEXHEIGHT = 40
BOARDWIDTH = 7
BOARDHEIGHT = 7
BORDERWIDTH = 15
UNITSIZE = HEXHEIGHT/3
SELECTSIZE = UNITSIZE + 5
WINDOWWIDTH = BOARDWIDTH*HEXWIDTH/3*2+BORDERWIDTH*2+HEXWIDTH/3
WINDOWHEIGHT = BOARDHEIGHT*HEXHEIGHT+HEXHEIGHT/2+BORDERWIDTH*2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DKRED = (127, 0, 0)
LTRED = (255, 127, 127)
GREEN = (0, 255, 0)
DKGREEN = (0, 127, 0)
LTGREEN = (127, 255, 127)
BLUE = (0, 0, 255)
DKBLUE = (0, 0, 127)
LTBLUE = (127, 127, 255)
COLORS = [[LTRED, RED, DKRED], [LTBLUE, BLUE, DKBLUE], [LTGREEN, GREEN, DKGREEN]]
#x, y, unit owner, time offset, length of turn
UNITS = [[0,0,0,0,6],[2,2,0,0,13],[1,1,0,0,20],[6,6,1,0,6],[4,4,1,0,13],[5,5,1,0,20],[0,6,2,0,6],[2,4,2,0,13],[1,5,2,0,20]]


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Move them units')
    DISPLAYSURF.fill(WHITE)
    
    #initialize so that game won't break when attempting to draw last selection black on first click
    x = None
    y = None
    player = 0
    time = 0
    player, time = getNextUnit(player, time, 1)[0], getNextUnit(player, time, 1)[1]
    for index in range(len(UNITS)):
        drawUnit(UNITS[index])
        drawBoard(BOARDWIDTH,BOARDHEIGHT)
    while True:
        nextunit = nextUnitIndex(player, time)
        highlightNextUnit(nextunit)
        mouseclicked = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseclicked = True
        if mouseclicked:
            index = getUnitAt(x, y)
            clearHexagonAt(x, y)
            x, y = getHexAtPixel(mousex, mousey)
            #Next unit is selected and movement is confirmed
            if nextunit == index and [x,y] in getMoveGrid(index):
                clearGrid(getMoveGrid(index))
                attoptions = getAttackGrid(index)
                if len(attoptions) != 0:
                    clearGrid(attoptions)
                    redrawSurvivors(attoptions)
                incrementUnitTimeOffset(index)
                moveUnit(index,x,y)
                drawUnit(UNITS[index])
                x,y = None, None
                player = getNextPlayer(player)
                player, time = getNextUnit(player, time, 1)[0], getNextUnit(player, time, 1)[1]
            #Attack
            if nextunit == index and [x,y] in getAttackGrid(index):
                UNITS[getUnitAt(x, y)][2] = -1
                clearGrid(getMoveGrid(index))
                attoptions = getAttackGrid(index)
                clearGrid(attoptions)
                redrawSurvivors(attoptions)
                incrementUnitTimeOffset(index)
                moveUnit(index,x,y)
                drawUnit(UNITS[index])
                x,y = None, None
                player = getNextPlayer(player)
                player, time = getNextUnit(player, time, 1)[0], getNextUnit(player, time, 1)[1]
            #Unit was selected, mouse is outside move grid or not next to move so redraw unit unmoved and unselected
            if index != None:
                drawUnit(UNITS[index])
            #No unit was selected but one is now. If it gets to go next draw where
            if index == None and getUnitAt(x,y) == nextunit:
                highlightGrid (getMoveGrid(nextunit), GREEN)
                highlightGrid (getAttackGrid(nextunit), RED)
            #No Matter what draw that red select hexagon
            drawHexagonAt(x, y, RED, 2)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def redrawSurvivors(grid):
    for x in range(len(grid)):
        x, y = grid[x]
        drawUnit(UNITS[getUnitAt(x,y)])
        
def moveUnit(index,x,y):
    UNITS[index][0], UNITS[index][1] = x, y

def incrementUnitTimeOffset(index):
    UNITS[index][3] = (UNITS[index][3] + 1) % UNITS[index][4]

def highlightGrid(grid, color):
    for index in range(len(grid)):
        highlightHex(grid[index][0], grid[index][1], color)

def clearGrid(grid):
    for index in range(len(grid)):
        clearHexagonAt(grid[index][0], grid[index][1])

def highlightNextUnit(index):
    x, y = UNITS[index][0],UNITS[index][1]
    highlightHex(x, y, GREEN)

def highlightHex(x, y, color):
    left, top = getCoords(x, y)
    pygame.draw.circle(DISPLAYSURF, color, (left+HEXWIDTH/2, top+HEXHEIGHT/2), SELECTSIZE,2)

def nextUnitIndex(nextplayer, time):
    for x in range(len(UNITS)):
        if (UNITS[x][3] + time) % UNITS[x][4] == 0 and nextplayer == UNITS[x][2]:
            return x
    return None

def getNextUnit(player, time, iterations):
    if nextUnitIndex(player, time) != None:
        return player, time
    else:
        if iterations % (PLAYERS+1) == 0:
            return getNextUnit(player, time + 1, iterations +1)
        return getNextUnit(getNextPlayer(player), time, iterations + 1)

def getNextPlayer(player):
    player = (player + 1) % PLAYERS
    return player
    
def drawBoard(x,y):
    for hexx in range(x):
        for hexy in range(y):
            drawHexagonAt(hexx, hexy, BLACK, 2)

def drawUnit(unit):
    x, y, player, color = unit[0], unit[1], unit[2], unit[4]%3
    left, top = getCoords(x, y)
    pygame.draw.circle(DISPLAYSURF, COLORS[player][color], (left+HEXWIDTH/2, top+HEXHEIGHT/2), UNITSIZE,0)
            
#Given a board location return pixel location to draw top left of hexagon
def getCoords(x,y):
    if x%2 == 0:
        top = y*HEXHEIGHT + BORDERWIDTH
    else:
        top = y*HEXHEIGHT + BORDERWIDTH + HEXHEIGHT/2
    left = x*HEXWIDTH/3*2 + BORDERWIDTH
    return (left,top)

def getUnitAt(x,y):
    for index in range(len(UNITS)):
        if UNITS[index][0] == x and UNITS[index][1] == y and UNITS[index][2]>-1:
            return (index)
    return None

def getMoveGrid(index):
    x, y = UNITS[index][0], UNITS[index][1]
    xrng, yrng = range(BOARDWIDTH), range(BOARDHEIGHT)
    grid = []
    if x-1 in xrng:
        if getUnitAt(x-1, y) == None:
            grid = grid + [[x-1, y]]
        if (x%2 == 0):
            if y-1 in yrng and getUnitAt(x-1, y-1) == None:
                    grid = grid + [[x-1, y-1]]
        else:
            if y+1 in yrng and getUnitAt(x-1, y+1) == None:
                    grid = grid + [[x-1, y+1]]
    if x+1 in xrng:
        if getUnitAt(x+1, y) == None:
            grid = grid + [[x+1, y]]
        if (x%2 == 0):
            if y-1 in yrng and getUnitAt(x+1, y-1) == None:
                    grid = grid + [[x+1, y-1]]
        else:
            if y+1 in yrng and getUnitAt(x+1, y+1) == None:
                    grid = grid + [[x+1, y+1]]
    if y-1 in yrng and getUnitAt(x, y-1) == None:
        grid = grid + [[x, y-1]]
    if y+1 in yrng and getUnitAt(x, y+1) == None:
        grid = grid + [[x, y+1]]
    return grid

def getAttackGrid(index):
    x, y, player = UNITS[index][0], UNITS[index][1], UNITS[index][2]
    xrng, yrng = range(BOARDWIDTH), range(BOARDHEIGHT)
    grid = []
    if x-1 in xrng:
        if getUnitAt(x-1, y) != None:
            if UNITS[getUnitAt(x-1, y)][2] != player:
                grid = grid + [[x-1, y]]
        if (x%2 == 0):
            if y-1 in yrng and getUnitAt(x-1, y-1) != None:
                if UNITS[getUnitAt(x-1, y-1)][2] != player:
                    grid = grid + [[x-1, y-1]]
        else:
            if y+1 in yrng and getUnitAt(x-1, y+1) != None:
                if UNITS[getUnitAt(x-1, y+1)][2] != player:
                    grid = grid + [[x-1, y+1]]
    if x+1 in xrng:
        if getUnitAt(x+1, y) != None:
            if UNITS[getUnitAt(x+1, y)][2] != player:
                grid = grid + [[x+1, y]]
        if (x%2 == 0):
            if y-1 in yrng and getUnitAt(x+1, y-1) != None:
                if UNITS[getUnitAt(x+1, y-1)][2] != player:
                    grid = grid + [[x+1, y-1]]
        else:
            if y+1 in yrng and getUnitAt(x+1, y+1) != None:
                if UNITS[getUnitAt(x+1, y+1)][2] != player:
                    grid = grid + [[x+1, y+1]]
    if y-1 in yrng and getUnitAt(x, y-1) != None:
        if UNITS[getUnitAt(x, y-1)][2] != player:
            grid = grid + [[x, y-1]]
    if y+1 in yrng and getUnitAt(x, y+1) != None:
        if UNITS[getUnitAt(x, y+1)][2] != player:
            grid = grid + [[x, y+1]]
    return grid

#Given a pixel location return board location of hex at that pixel
def getHexAtPixel(x,y):
    for hexx in range(BOARDWIDTH):
        for hexy in range(BOARDHEIGHT):
            left, top = getCoords(hexx, hexy)
            hexrect = pygame.Rect(left,top, HEXWIDTH, HEXHEIGHT)
            if hexrect.collidepoint(x,y):
                #Is collision outside top left side of hex?
                if x > (left + HEXWIDTH/3*2) and y < (top + HEXHEIGHT/2) and y < top + (x - (left + HEXWIDTH/3*2))*3/2:
                    if hexx%2 != 0 and hexx + 1 < BOARDWIDTH:
                        return (hexx + 1, hexy)
                    if hexy > 0 and hexx + 1 < BOARDWIDTH:
                        return (hexx + 1, hexy - 1)
                #Is collision outside bottom left side of hex?
                if x > (left + HEXWIDTH/3*2) and y > (top + HEXHEIGHT/2) and y > top + HEXHEIGHT - (x - (left + HEXWIDTH/3*2))*3/2:
                    if hexx%2 == 0 and hexx + 1 < BOARDWIDTH:
                        return (hexx + 1, hexy)
                    if hexy + 1 < BOARDHEIGHT and hexx + 1 < BOARDWIDTH:
                        return (hexx + 1, hexy + 1)
                #Collision is inside correct hex
                return (hexx, hexy)
    #No collision
    return (None, None)
    
def clearHexagonAt(x, y):
        drawHexagonAt(x, y, WHITE, 0)
        drawHexagonAt(x, y, BLACK, 2)
    
def drawHexagonAt(x, y, color, width):
    if x != None and y != None:
        left, top = getCoords(x, y)
        pygame.draw.polygon(DISPLAYSURF, color, ((left, top+HEXHEIGHT/2), (left+HEXWIDTH/3,top),
        (left+(HEXWIDTH/3*2),top), (left+HEXWIDTH, top+HEXHEIGHT/2), (left+(HEXWIDTH/3*2),
        top+HEXHEIGHT), (left+(HEXWIDTH/3), top+HEXHEIGHT)),width)

main()
