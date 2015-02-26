#!/usr/bin/python

import sys
from sys import argv
import os
import re
import subprocess

title	= "TicTacToe"
version	= "0.9"

DEBUG = 1

board  = ['-']*9 
tokens = ['X','O']

# Draw the game board
def draw_nice_state():
	for i in range(3):
		for j in range(3):
			print board[i*3+j],
		print ""
	print ""

# Check for a winning condition
# Return conditions:
#   0 = Game still playing
#   1 = Winner found
#   2 = Tie
def endOfGameCheck():
	# Horizontal	
	for i in range(0,7,3):
		if ((board[0+i]!='-') and (board[0+i] == board[1+i]) and (board[1+i] == board[2+i])): return 1
	# Vertical
	for i in range(0,3):
		if ((board[0+i]!='-') and (board[0+i] == board[3+i]) and (board[3+i] == board[6+i])): return 1
	# Diagonal
	if ((board[0]!='-') and (board[0] == board[4]) and (board[4] == board[8])): return 1
	if ((board[2]!='-') and (board[2] == board[4]) and (board[4] == board[6])): return 1

	# Tie
	if (board.count('-') == 0): return 2

	return 0

# Validate and process a player's move
def processMove(player,move):

	global board

	# Check for an invalid move...
	if ((move < 0) or (move > 8)): 			return 1
	if (board[move] != '-'):			return 1

	# Make the move now that everything has been validated...
	board[move] = player;

	return 0;


# Validate the command line...
if (len(argv) != 3):
	sys.exit("ERROR: Two player bots must be specified!")
if not (os.path.exists(argv[1]) and os.path.exists(argv[2])):
	sys.exit("ERROR: Unable to locate the requested players!")

# Initialize players
player0 = subprocess.Popen([argv[1]], stdout=subprocess.PIPE, stdin=subprocess.PIPE);
player1 = subprocess.Popen([argv[2]], stdout=subprocess.PIPE, stdin=subprocess.PIPE);
player0.stdin.write("ASSIGN_PLAYER: 0\n")
player0.stdin.write("GAMESTATE: ---------\n")
player0.stdin.flush()
player1.stdin.write("ASSIGN_PLAYER: 1\n")
player1.stdin.write("GAMESTATE: ---------\n")
player1.stdin.flush()

# Print the game header and start the game...
print "%s(%s) -  %s(X) vs %s(O)" % (title, version, sys.argv[1], sys.argv[2])
	
# Process moves until the game is over... 
players  = [player0,player1]
turn	 = 0
endstate = 0
while ( not endstate ):
	# Request a move from the active player
	if DEBUG: print "Requesting move from player%d..." % turn
	players[turn].stdin.write("REQUEST_MOVE\n")
	players[turn].stdin.flush()

	# Receive a move from the active player
	line = players[turn].stdout.readline()
	line.rstrip()
	if DEBUG: print "Got reply form player%d: %s" % (turn,line)
	expr = re.match(r"^(\d)$", line)
	if not expr:	# is a single digit
		print "malformed reply from player%d (%s)" % (turn,line)
		endstate = 3
		continue

	# Process the move	
	move = int(expr.group(1))
	if DEBUG: print "Player%d chooses to move at %d" % (turn,move)
	if (processMove(tokens[turn],move) == 1):
		if DEBUG: print "player%d moved illegally! forfeits!" % turn
		endstate = 3
		continue

	# Draw the game board for logging
	draw_nice_state()

    # game over?
	endstate = endOfGameCheck()
	if endstate: continue

	# Update both players with new game state
	state_xmit = 'GAMESTATE: '
	for i in range(9):
		state_xmit += board[i]
	state_xmit += "\n"
	print "Broadcasting: ", state_xmit
	player0.stdin.write(state_xmit)
	player0.stdin.flush()
	player1.stdin.write(state_xmit)
	player1.stdin.flush()

	# Change active player
	turn = (turn + 1) % 2

# close pipes, subprocesses
player0.kill()
player1.kill()

# Game is over, print the results...
if   endstate == 1: print("OUTCOME: %dW") % (turn)	# Somebody won
elif endstate == 2: print("OUTCOME: 0")			# Tie
elif endstate == 3: print("OUTCOME: %dF") % (turn)	# Tomfoolery
else: print("Somebody crossed the beams...Time to panic!")

