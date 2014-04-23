# -*-coding:utf-8 -*

#-------------------------#
# Reversi_v1.0            #
# Author : Edouard Rosset #
# Date : 2014_04_23       #
#-------------------------#

from django.shortcuts import render
from django.http import HttpResponseRedirect
from random import getrandbits

# import AI and game mechanics
from app_reversi.ai import evaluate
from app_reversi.gameMechanics import getPile, isValidMove


# import objects specific to the game
from app_reversi.models import Player, Board


#----------------------#
#------ Display -------#
#----------------------#
def display(request):
 """ Display board with info stocked in session
 Create a new game if no data is found in session"""
 if request.session["board"] is None:
  newGame(request)
 return render(request, 'template_reversi.html',locals())

#----------------------#
#--- Game Mechanics ---#
#----------------------#
def newGame(request):
 """ Game Initialization :
 - get a new board
 - set variable to test of end of game to False
 - set message of welcome page"""

 board=Board()
 request.session["board"] = board # stock board in session
 request.session["testEndOfGame"] = False
 request.session["message"] = "Choose the type of Game"
 return display(request) # choose the type of game on the main screen

def chooseGame(request,typeOfGame):
 """ Choose your game :
 - get the player choice for the game from the URL """

 newGame(request)
 typeOfGame=int(typeOfGame)
 if typeOfGame not in [0,1,2]:
  # if the player forces the url, everything exploses :
  return HttpResponseRedirect("http://armedia.am/_images_/image/2013/4%2830%29.jpg")

 # Initialize players
 p0=Player()
 p1=Player()
 p1["color"] = 1
 # choose to be 0 or 1 and set the other to computer if needed
 if typeOfGame == 0: 
  p0["human"] = False # p0 is a computer
 elif typeOfGame == 1: 
  p1["human"] = False # p1 is a computer
 elif typeOfGame == 2: # play with a friend
  pass

# Stock players in session :
 request.session["players"] = [p0,p1] 
 
 # randomize starter
 if bool(getrandbits(1)):
  request.session["playersTurn"]=0
  request.session["message"]="Orange starts"
 else:
  request.session["playersTurn"]=1
  request.session["message"]="Blue starts"

# start the game : 
 return play(request,request.session["playersTurn"])



def play(request,playerColor):
 """ Play :
 - if the player is human, present the board
 - if not, get the move from computer"""

 # get local variable "player" from data stocked in session 
 player = request.session["players"][playerColor]
 # get possible moves for the player
 player["pile"]=getPile(request.session["board"],playerColor)
 
 # test if possible moves exists for one of the player
 if player["pile"]==[]:
  if request.session["testEndOfGame"]==True:
   return displayScore(request)
  else:
   request.session["testEndOfGame"]=True
   return nextPlayer(request) # no possible move -> switch player
 else:
  request.session["testEndOfGame"]=False
  if player["human"]==True:
   # present the board to the player
   return display(request)
  else:
   # get computer move
   return computerMoves(request, playerColor)



def computerMoves(request, compColor):
 """ Return move of computer"""
 # Set a local variable with possible moves
 rawPile = request.session["players"][compColor]["pile"]
 # Call AI to sort the cells according to computer's choice
 pile = evaluate(request, rawPile, compColor)
 # Play the prefered move of computer
 return move (request, pile[0]["position"])


def move(request, idCell):
 """ Play in cell idCell, get idCell from the URL :
 - Modify board stocked in session following the move 
 - Send data for animation sequence
 - Call next player """
 board = request.session["board"]
 color = request.session["playersTurn"]

 # Check if the player tried to force an illegal move
 if not isValidMove(board,idCell,color):
  return HttpResponseRedirect("http://www.mathcs.duq.edu/~jackson/opinions/Cheating.html") # eastern egg
  #<-------------------------- https://www.youtube.com/watch?v=tO7LIRhGbfo&feature=youtu.be&t=45s

 # get coordinates if the move from the string idCell
 xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
 board[xCell][yCell]["color"]=color
 # flip tiles for this move :
 for i in range(8):
  for j in range(8):
   board[i][j]["motion"]=False
 # Check all directions, if the pattern for flipping is found, tiles are flipped :
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
     # line found, lets flip them :
     x -= xdirection
     y -= ydirection
     while board[x][y]["color"] == 1-color:
      # for the animation :
      board[x][y]["motion"]=True
      # actual flip :
      board[x][y]["color"]=color
      x -= xdirection
      y -= ydirection
 # reset pile of the player
 request.session["players"][color]["pile"]=[]

 # Call next player
 return nextPlayer(request)
  # to improve visual effect, a step may be added, it would start with a test on who is playing :
  # (before calling next player)
  # if request.session["players"][color]["human"]==True:


def nextPlayer(request):
 """ Switch players"""
 # switch player stocked in session
 request.session["playersTurn"] = 1-request.session["playersTurn"]

 # Adapt message to know who's turn it is :
 if request.session["playersTurn"]==0:
  request.session["message"]="Orange"
 else:
  request.session["message"]="Blue"

 return play(request,request.session["playersTurn"])


def displayScore(request): 
 """ Display score in the message of the game"""
 blue=0
 orange=0
 # count cells for each color
 for i in range(8):
  for j in range(8):
   if request.session["board"][i][j]["color"]==1:
    blue+=1
   elif request.session["board"][i][j]["color"]==0:
    orange+=1
 blue=str(blue)
 orange=str(orange)

 # concatenate data in the message to display
 request.session["message"] = "Blue : "+blue+" - "+orange+" : Orange"

 # return result
 return display(request)

 
