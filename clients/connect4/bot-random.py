#!/usr/bin/python

from sys import stdin, stdout
import re
import random

state = ''

player = 0

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
        # create 2d arrray to represent board
        board = [0]*8
        for i in range(8):
            board[i] = [0]*8
        # parse state characters into 2d array
        for i in range(8):
            for j in range(8):
                board[i][j] = state[i*8+j]
        # generate random column to move until column is empty (ie legal move!)
        move = 0
        while 1:
            move = random.randint(0,7)
            if board[0][move] == '-':
                break
        # US -> GAME : send move back!
        #
        print "%d\n" % move,
        stdout.flush()

        continue

    print "unrecognized shit from GAME:", line
