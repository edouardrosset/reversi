# -*-coding:utf-8 -*

#-------------------------#
# Reversi_v1.0            #
# Author : Edouard Rosset #
# Date : 2014_04_23       #
#-------------------------#


def getPile(board,color):
 """ Calculate possible moves :
 - stock resul in attribute of the cell (stocked in the session)
 - and return a list with them"""
 color=int(color)
 pile=[]
 for x in range(8):
  for y in range(8):
   # reinitialize playability of each cell
   board[x][y]["playable"]=False
   # check for each cell if it is playable for the color called
   if isValidMove(board,str(x)+str(y),color):
   	# stock result in attribute of cell
    board[x][y]["playable"]=True
    # add cell to the list to return
    pile.append(board[x][y])
 return pile

def isValidMove(board,idCell,color):
 """ Check if a move in position idCell is possible for the color called 
 - return True if the cell will flip at least one tile
 - return False if not """
 color=int(color)
 # get coordinates from the string idCell
 xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])

 # check if the cell is empty
 if board[xCell][yCell]["color"]==' ':
  # then check if the cell is playable in a least one direction
  for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
   x, y = xCell, yCell
   x += xdirection # first step in the direction
   y += ydirection # first step in the direction

   # check if the pattern corresponds to a playable cell : [color][n x opponent][free]
   if x<8 and y<8 and x>=0 and y >=0 and board[x][y]["color"] == 1-color:
    while x<8 and y<8 and x>=0 and y >=0 and board[x][y]["color"] == 1-color:
     x += xdirection
     y += ydirection
    if x<8 and y<8 and x>=0 and y >=0:
     if board[x][y]["color"] == color:
      # if the pattern works -> this cell works, return true
      return True

 # in any other case, return false
 return False


