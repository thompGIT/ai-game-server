#!/usr/bin/python

# This bot follows the strategy of attempting only vertical wins, ignoring everything else.


from sys import stdin, stdout
import re
import random

state = ''
board = [0]*8
for i in range(8): board[i] = [0]*8

player = 0
tokens = ["X","O"]

def draw_nice_state():
    global state
    for i in range(8):
        print state[i*8:i*8+8]

while 1:
    line = stdin.readline()
    line.rstrip()

    # GAME -> US : assign player
    expr = re.match(r"ASSIGN_PLAYER: (\d+)", line)
    if expr:
        player = int(expr.group(1))
        #print "I'm player %d!\n" % player
        continue

    # GAME -> US : game state update!
    #
    # '-' == empty slot
    # 'X' == first player token in slot
    # 'O' == second player has token in slot
    # example starting position before any players:
    # GAMESTATE: ----------------------------------------------------------------
    expr = re.match(r"GAMESTATE: ([-XO]{64})", line)
    if expr:
        state = expr.group(1)
        #print "set new state:", state
        #draw_nice_state()
        continue

    # GAME -> US : request a move!
    #
    expr = re.match(r"REQUEST_MOVE", line)
    if expr:
        # parse state characters into 2d array, but arrange based on columns instead of rows
        for i in range(8):
            for j in range(8):
                board[i][j] = state[i+8*j]

        # find the column with the longest sequence of our tokens at the top
        scores = [-25]*8
        for i in range(8):

            # First, make sure it's legal to move here...
            if not ("-" in board[i]): scores[i] = -100; continue

            # If our token is on top...
            if not(tokens[player] in board[i]): continue
            p1Index = board[i].index(tokens[player])
            p2Index = 100 
            if tokens[(player+1)%2] in board[i]: 
                p2Index = board[i].index(tokens[(player+1)%2])
            if p1Index >= p2Index:

                # Count the length of the sequence and increment the score...
                scores[i] = 0
                for j in range(board[i].index(tokens[player]),8):
                    if board[i][j] == tokens[player]: scores[i] += 1
                    else: break

                # If we are about to win, DO IT!
                if (scores[i] == 3) and ("-" in board[i]): scores[i] = 50

                # If there is not enough room to finish, abandon ship
                if scores[i] + board[i].count("-") < 4: scores[i] = -50

            # print board[i]

        #print scores

        # Determine a move based on the best score
        move = scores.index(max(scores))

        # US -> GAME : send move back!
        #
        print "%d\n" % move,
        stdout.flush()

        continue

    print "unrecognized shit from GAME:", line
