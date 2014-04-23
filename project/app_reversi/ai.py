# -*-coding:utf-8 -*

#-------------------------#
# Reversi_v1.0            #
# Author : Edouard Rosset #
# Date : 2014_04_23       #
#-------------------------#

# import objects specific to the game
from app_reversi.models import Board, BorderPattern, RawPattern, DiagPatternsAuthorized

# import method specific to the game
from app_reversi.gameMechanics import getPile
 
def evaluate(request,pile,color):
 """ Return a list with the possible moves for the computer sorted by order of preference :
 - An evaluation of the risk opportunity for each cell of the board
 - An objective of limitation of the moves offered to the opponent 
 - The intrinseque value of the position of the cell"""

 #-------------------------------------------
 # Evaluate risk / opportunity by the borders
 #-------------------------------------------
 borders=getBorders(request)
 patterns = BorderPattern()
 rawPattern=RawPattern()
 
 posPatBorder=0
# request.session["messageBorder"]=[]                  # <----DEBUG

 # Determinate pattern of each border :
 for border in borders:
  localPattern=[]
  if border[0]["color"]==' ' and border[-1]["color"]==' ':
   localPattern=['']
   i = 1
   while i<7:
    if border[i]["color"] == ' ':
     localPattern.append('')
    elif border[i]["color"] == color and border[i-1]["color"] != color:
     localPattern.append('o')
    elif border[i]["color"] == 1-color and border[i-1]["color"] != 1-color:
     localPattern.append('x')
    i+=1
   localPattern.append('')

  # If the pattern exists in the references, apply results : 
  if localPattern in rawPattern:
   posPatBorder=rawPattern.index(localPattern)
   j=0
   for i in range(8):
    if border[i]["color"]==' ':
     while patterns[posPatBorder][j]=='o' or patterns[posPatBorder][j]=='x':
      j+=1
     if (border[i]["risk"] < patterns[posPatBorder][j] and \
      (border[i]["risk"] >=0 or patterns[posPatBorder][j] == 4)) \
     or (patterns[posPatBorder][j] < border[i]["risk"] and patterns[posPatBorder][j] <0):
      border[i]["risk"] = patterns[posPatBorder][j]
     j+=1
#  else:                        # <----DEBUG
#   posPatBorder=99998                    # <----DEBUG
#  request.session["messageBorder"].append(str(border)+" position du pattern : "+str(posPatBorder+1)) # <----DEBUG


 #-------------------------------------------
 # Evaluate risk / opportunity by the diagonales
 #-------------------------------------------
 diagonales=getDiagonales(request)
 diagPatterns=DiagPatternsAuthorized()
 for diagonale in diagonales:
  localPattern=[]
  diagonale[1]["risk"]= -2
  for i in range(8):
   if diagonale[i]["color"] == ' ':
    localPattern.append('')
   elif diagonale[i]["color"] == color and diagonale[i-1]["color"] != color:
    localPattern.append('o')
   elif diagonale[i]["color"] == 1-color and diagonale[i-1]["color"] != 1-color:
    localPattern.append('x')

  if localPattern in diagPatterns:
   diagonale[1]["risk"]= -1

 #-------------------------------------------
 # if opponent took a risky position on a diagonale, avoid flipping his tile
 #-------------------------------------------
 for cell in pile:
  flipsList = wouldFlip(request,cell["position"])
  if not cell["position"] in ['00','77','70','07']:
   if '11' in flipsList or \
   '66' in flipsList or \
   '61' in flipsList or \
   '16' in flipsList:
    cell["risk"]= -2

 #-------------------------------------------
 # Count number of flips for a move # <------------------ deactivated
 #-------------------------------------------
 # for cell in pile:
 #  flipsList = wouldFlip(request,cell["position"])
 #  cell["nbFlips"] = len(flipsList)

 #-------------------------------------------
 # get nb of positions offered to the opponent 
 #-------------------------------------------
 for cell in pile:
  cell["nbPositionsOffered"] = getNbPosOffered(request,cell["position"])


 #-------------------------------------------
 # Synthesis
 #-------------------------------------------

 # sort pile, form least to most important :
 # - intrinsec value
 # - nb of positions offered to opponent
 # - risk / opportunity

 sortedToValue = sorted(pile, key=lambda x: x["value"], reverse=True)
 # sortedToNbFlipsOrPosOffered = sorted(sortedToValue, key=lambda x: x["nbFlips"]) # <---------- deactivated
 sortedToNbFlipsOrPosOffered = sorted(sortedToValue, key=lambda x: x["nbPositionsOffered"]) 
 sortedToRisk = sorted(sortedToNbFlipsOrPosOffered, key=lambda x: x["risk"], reverse=True)

# request.session["messagePile"] = str(sortedToRisk)              # <----DEBUG

 # return the result
 return sortedToRisk


def getBorders(request):
 """ Return projections of borders as lists """
 borders=[]
 board=request.session["board"]
 for i in range(8):
  borders.append([])
 for i in range(8):
  borders[0].append(board[0][i])
  borders[1].append(board[0][7-i])
  borders[2].append(board[i][0])
  borders[3].append(board[7-i][0])
  borders[4].append(board[7][i])
  borders[5].append(board[7][7-i])
  borders[6].append(board[i][7])
  borders[7].append(board[7-i][7])
 return borders

def getDiagonales(request):
 """ Return projections of diagonales as lists """
 diagonales=[]
 board=request.session["board"]
 for i in range(4):
  diagonales.append([])
 for i in range(8):
  diagonales[0].append(board[i][i])
  diagonales[1].append(board[7-i][7-i])
  diagonales[2].append(board[i][7-i])
  diagonales[3].append(board[7-i][i])
 return diagonales

def wouldFlip(request,idCell):
 """ Return the list of the tiles that would be flipped by a move """

 # Get data from the session
 board = request.session["board"]
 color = request.session["playersTurn"]
 xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
 flipsList=[]

 # Check all direction, and each time a tile would be flipped, add it to the list to return
 for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
  x, y = xCell,yCell
  x += xdirection # first step in the direction
  y += ydirection # first step in the direction
  if x<8 and y<8 and x>=0 and y >=0 and board[x][y]["color"] == 1-color:
   while x<8 and y<8 and x>=0 and y >=0 and board[x][y]["color"] == 1-color:
    x += xdirection
    y += ydirection
   if x<8 and y<8 and x>=0 and y >=0:
    if board[x][y]["color"] == color:
     # line found, lets add each tile to the result to return :
     x -= xdirection
     y -= ydirection
     while board[x][y]["color"] == 1-color:
      flipsList.append(board[x][y]["position"])
      x -= xdirection
      y -= ydirection
 # return the result
 return flipsList

def getNbPosOffered(request,idCell):
 """ Return the number of possible moves that a move would offer to the opponent"""
 # get a copy of the board
 tempBoard= Board()
 for x in range(8):
  for y in range(8):
   tempBoard[x][y]["color"] = request.session["board"][x][y]["color"]

 # simulate the move
 color = request.session["playersTurn"]
 xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
 tempBoard[xCell][yCell]["color"]=color

 # simulate the flip of tiles in the temp board
 for i in range(8):
  for j in range(8):
   tempBoard[i][j]["motion"]=False
 for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
  x, y = xCell,yCell
  x += xdirection # first step in the direction
  y += ydirection # first step in the direction
  if x<8 and y<8 and x>=0 and y >=0 and tempBoard[x][y]["color"] == 1-color:
   while x<8 and y<8 and x>=0 and y >=0 and tempBoard[x][y]["color"] == 1-color:
    x += xdirection
    y += ydirection
   if x<8 and y<8 and x>=0 and y >=0:
    if tempBoard[x][y]["color"] == color:
     # line found, lets flip them
     x -= xdirection
     y -= ydirection
     while tempBoard[x][y]["color"] == 1-color:
      tempBoard[x][y]["motion"]=True
      tempBoard[x][y]["color"]=color
      x -= xdirection
      y -= ydirection

 # Count the result in the would pile length of the opponent :
 return len(getPile(tempBoard,1-color))
