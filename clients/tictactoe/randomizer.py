#!/usr/bin/python

from sys import stdin, stdout
import re
import random

random.seed()
state = ['-']*9 

while 1:
	# Read message from the game server
	line = stdin.readline()
	line.rstrip()

	# Message: assign player
	expr = re.match(r"ASSIGN_PLAYER: (\d+)", line)
	if expr:
		#print "I am player %d!\n" % player
		continue

	# Message: game state update
	expr = re.match(r"GAMESTATE: ([-XO]{9})", line)
	if expr:
		#print "New Game State: %s" % expr.group(1)
		state = expr.group(1)
		continue

	# Message: Move Request
	expr = re.match(r"REQUEST_MOVE", line)
	if expr:
		while(1):
			move = random.randint(0,8)
			if state[move] == '-' : break
		print "%d" % move
		stdout.flush()
		continue

	# Unknown Message
	print "Unknown message from server:", line


