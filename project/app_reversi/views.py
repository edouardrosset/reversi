# -*-coding:utf-8 -*
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from random import getrandbits

# import objects specific to the game
from app_reversi.models import Cell, Player, Board, BorderPattern, RawPattern, DiagPatternsAuthorized


def newGame(request):
	board=Board()
	request.session["board"] = board # stock board in session
	request.session["testEndOfGame"] = False
	request.session["message"] = "Choose the type of Game"
	return display(request) # choose the type of game on the main screen

def chooseGame(request,typeOfGame):
	newGame(request)
	typeOfGame=int(typeOfGame)
	if typeOfGame not in [0,1,2]:
		return HttpResponseRedirect("http://armedia.am/_images_/image/2013/4%2830%29.jpg")
	p0=Player()
	p1=Player()
	p1["color"] = 1

	if typeOfGame == 0: # choose to be 0 or 1
		p0["human"] = False
	elif typeOfGame == 1: # choose to be 0 or 1
		p1["human"] = False
	elif typeOfGame == 2: # play with a friend
		pass

	request.session["players"] = [p0,p1] #stock players in session
 
	# randomize starter
	if bool(getrandbits(1)):
		request.session["playersTurn"]=0
		request.session["message"]="Orange starts"
	else:
		request.session["playersTurn"]=1
		request.session["message"]="Blue starts"


	return play(request,request.session["playersTurn"])

def play(request,playerColor):
	
	player = request.session["players"][playerColor]
	player["pile"]=getPile(request.session["board"],playerColor)
	
	if player["pile"]==[]:
		if request.session["testEndOfGame"]==True:
			return displayScore(request)
		else:
			request.session["testEndOfGame"]=True
			return nextPlayer(request) # no possible move -> switch player
	else:
		request.session["testEndOfGame"]=False
		if player["human"]==True:
			return display(request) # play screen
		else:
			return computerMoves(request, playerColor)#   <--- AI

def getPile(board,color):
	color=int(color)
	pile=[]
	for x in range(8):
		for y in range(8):
			board[x][y]["playable"]=False
			#board[x][y]["motion"]=False
			if isValidMove(board,str(x)+str(y),color):
				board[x][y]["playable"]=True
				pile.append(board[x][y])
	return pile

def isValidMove(board,idCell,color):
	color=int(color)
	xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
	if board[xCell][yCell]["color"]==' ':
		for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
			x, y = xCell, yCell
			x += xdirection # first step in the direction
			y += ydirection # first step in the direction
			if x<8 and y<8 and x>=0 and y >=0 and board[x][y]["color"] == 1-color:
				while x<8 and y<8 and x>=0 and y >=0 and board[x][y]["color"] == 1-color:
					x += xdirection
					y += ydirection
				if x<8 and y<8 and x>=0 and y >=0:
					if board[x][y]["color"] == color:
						# this cell works
						return True
	return False

def move(request, idCell):
	board = request.session["board"]
	color = request.session["playersTurn"]
	if not isValidMove(board,idCell,color):
		return HttpResponseRedirect("http://www.mathcs.duq.edu/~jackson/opinions/Cheating.html") # eastern egg
		#<-------------------------- https://www.youtube.com/watch?v=tO7LIRhGbfo&feature=youtu.be&t=45s

	xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
	board[xCell][yCell]["color"]=color
	# flip tiles
	for i in range(8):
		for j in range(8):
			board[i][j]["motion"]=False
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
					# line found, lets flip them
					x -= xdirection
					y -= ydirection
					while board[x][y]["color"] == 1-color:
						board[x][y]["motion"]=True
						board[x][y]["color"]=color
						x -= xdirection
						y -= ydirection
	request.session["players"][color]["pile"]=[]
	if request.session["players"][color]["human"]==True:
		return nextPlayer(request) # animation du move et bouton nextPlayer
	else:
		return nextPlayer(request)

def display(request):
	if request.session["board"] is None:
		newGame(request)
	return render(request, 'template_reversi.html',locals())

def nextPlayer(request):
	request.session["playersTurn"] = 1-request.session["playersTurn"]

	if request.session["playersTurn"]==0:
		request.session["message"]="Orange"
	else:
		request.session["message"]="Blue"

	return play(request,request.session["playersTurn"])

def displayScore(request): 
	blue=0
	orange=0
	for i in range(8):
		for j in range(8):
			if request.session["board"][i][j]["color"]==1:
				blue+=1
			elif request.session["board"][i][j]["color"]==0:
				orange+=1
	blue=str(blue)
	orange=str(orange)
	request.session["message"] = "Blue : "+blue+" - "+orange+" : Orange"
	return display(request)

def computerMoves(request, compColor):
	rawPile = request.session["players"][compColor]["pile"]
	pile = evaluate(request, rawPile, compColor)

	return move (request, pile[0]["position"])
	
def evaluate(request,pile,color):
	
	# play by the borders
	borders=getBorders(request)
	patterns = BorderPattern()
	rawPattern=RawPattern()
	
	posPatBorder=0
	request.session["messageBorder"]=[]																		# <----DEBUG
	for border in borders:
		localPattern=[]
		if border[0]["color"]==' ' and border[-1]["color"]==' ':
			localPattern=['']
			i =	1
			while i<7:
				if border[i]["color"] == ' ':
					localPattern.append('')
				elif border[i]["color"] == color and border[i-1]["color"] != color:
					localPattern.append('o')
				elif border[i]["color"] == 1-color and border[i-1]["color"] != 1-color:
					localPattern.append('x')
				i+=1
			localPattern.append('')
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
		else:																								# <----DEBUG
			posPatBorder=99998																				# <----DEBUG
		request.session["messageBorder"].append(str(border)+" position du pattern : "+str(posPatBorder+1))	# <----DEBUG

	# play by the diagonales
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

	# if opponent took diagonale, avoid flipping his tile
	for cell in pile:
		flipsList = wouldFlip(request,cell["position"])
		if not cell["position"] in ['00','77','70','07']:
			if '11' in flipsList or \
			'66' in flipsList or \
			'61' in flipsList or \
			'16' in flipsList:
				cell["risk"]= -2

		# get nb of flips
	#	cell["nbFlips"] = len(flipsList) # <------------------ deactivated 

	# get nb of positions offered
		cell["nbPositionsOffered"] = getNbPosOffered(request,cell["position"])

	# sort pile 
	sortedToValue = sorted(pile, key=lambda x: x["value"], reverse=True)
 
	# sortedToNbFlipsOrPosOffered = sorted(sortedToValue, key=lambda x: x["nbFlips"]) # <---------- deactivated
	
	sortedToNbFlipsOrPosOffered = sorted(sortedToValue, key=lambda x: x["nbPositionsOffered"]) 
	
	sortedToRisk = sorted(sortedToNbFlipsOrPosOffered, key=lambda x: x["risk"], reverse=True)

	request.session["messagePile"] = str(sortedToRisk)														# <----DEBUG

	return sortedToRisk


def getBorders(request):
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
	board = request.session["board"]
	color = request.session["playersTurn"]
	xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
	flipsList=[]
	# flip tiles
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
					# line found, lets flip them
					x -= xdirection
					y -= ydirection
					while board[x][y]["color"] == 1-color:
						flipsList.append(board[x][y]["position"])
						x -= xdirection
						y -= ydirection

	return flipsList

def getNbPosOffered(request,idCell):
	# get a copy of the board
	tempBoard= Board()
	for x in range(8):
		for y in range(8):
			tempBoard[x][y]["color"] = request.session["board"][x][y]["color"]

	color = request.session["playersTurn"]
	xCell,yCell = int(str(idCell)[0]), int(str(idCell)[1])
	tempBoard[xCell][yCell]["color"]=color
	# flip tiles in the temp board
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
	# get the would pile length of the opponent :
	return len(getPile(tempBoard,1-color))
