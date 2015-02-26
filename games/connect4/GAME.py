#!/usr/bin/python

# "GO FOR THE BOTTOM! AND GO FOR THE TOP! WATCH FOR THE BLOCK!? FORGET IT! YOU'RE STUCK!
#  GO FOR THE GLORY, GO FOR THE SCORE! GO FOR IT! (I WIN!) CONNECT 4!
# bugs? blame andrewl

from sys import argv, stdin, stdout
import os
import re
import subprocess

state = ''

class dummy_pipe:
    def __init__(self):
        self.stdin = stdout
        self.stdout = stdin
    def kill(x):
        pass

def draw_nice_state():
    global state
    for i in range(8):
        print state[i*8:i*8+8]

if len(argv)==3:
    # argv==3 (2 parameters) always indicates a fight!

    # init player0
    if argv[1] == 'human':
        player0 = dummy_pipe()
    elif os.path.exists(argv[1]):
        player0 = subprocess.Popen([argv[1]], stdout=subprocess.PIPE, stdin=subprocess.PIPE);
    else:  
        raise Exception('unknown player type %s' % argv[1])

    # init player1
    if argv[2] == 'human':
        player1 = dummy_pipe()
    elif os.path.exists(argv[2]):
        player1 = subprocess.Popen([argv[2]], stdout=subprocess.PIPE, stdin=subprocess.PIPE);
    else:
        raise Exception('unknown player type %s' % argv[1])

    # initial messages to players
    player0.stdin.write("ASSIGN_PLAYER: 0\n")
    player0.stdin.write("GAMESTATE: ----------------------------------------------------------------\n")
    player0.stdin.flush()
    player1.stdin.write("ASSIGN_PLAYER: 1\n")
    player1.stdin.write("GAMESTATE: ----------------------------------------------------------------\n")
    player1.stdin.flush()

    # initialize 2d array to represent board
    board = [0]*8
    for i in range(8):
        board[i] = ['-']*8

    # convenience arrays
    players = [player0, player1]
    tokens = ['X', 'O']

    # turn-taking loop
    outcome = 'ERROR'
    turn = 0
    while 1:
        print "requesting move from player%d" % turn
        players[turn].stdin.write("REQUEST_MOVE\n")
        players[turn].stdin.flush()
        legal = 0

        line = players[turn].stdout.readline()
        line.rstrip()
        print "got reply from player%d: %s" % (turn, line)
        expr = re.match(r"^(\d)$", line)
        if expr: # is single digit?
            column = int(expr.group(1))
            if column >= 0 and column <= 7: # is [0,7]?
                if board[0][column] == '-': # does column have room?
                    legal = 1
                    # search bottom-up for empty slot
                    for row in reversed(range(8)):
                        if board[row][column] == '-':
                            board[row][column] = tokens[turn]
                            break
                    print "player%d moves to (%d,%d)\n" % (turn, row, column)

        # illegal move? non-turn player wins
        if not legal:
            print "player%d moved illegally! forfeits!" % turn
            outcome = ((turn + 1)%2)
            break

        # print current board 
        state_xmit = 'GAMESTATE: '
        print "current board:"
        for i in range(8):
            for j in range(8):
                state_xmit += board[i][j]
                print board[i][j],
            print ""
        print ""

        # did connect 4?
        win = 0
        # search for east runs
        for i in range(8):
            for j in range(5):
                if ((board[i][j] == tokens[turn]) and (board[i][j+1] == tokens[turn]) and (board[i][j+2] == tokens[turn]) and (board[i][j+3] == tokens[turn])):
                    win = 1
        # search for south runs 
        for i in range(5):
            for j in range(8):
                if ((board[i][j] == tokens[turn]) and (board[i+1][j] == tokens[turn]) and (board[i+2][j] == tokens[turn]) and (board[i+3][j] == tokens[turn])):
                    win = 1
        # search for south east runs
        for i in range(5):
            for j in range(5):
                if ((board[i][j] == tokens[turn]) and (board[i+1][j+1] == tokens[turn]) and (board[i+2][j+2] == tokens[turn]) and (board[i+3][j+3] == tokens[turn])):
                    win = 1
        # search for north east runs
        for i in reversed(range(4,8)):
            for j in range(5):
                if ((board[i][j] == tokens[turn]) and (board[i-1][j+1] == tokens[turn]) and (board[i-2][j+2] == tokens[turn]) and (board[i-3][j+3] == tokens[turn])):
                    win = 1

        if win:
            print "player%d wins!" % turn
            outcome = turn
            break

        # did tie?
        tie = 1
        for i in range(8):
            if board[0][i] == '-':
                tie = 0
        if tie:
            outcome = 'TIE'
            break

        # inform both dudes about current state
        print "broadcasting:", state_xmit
        state_xmit += "\n"
        players[0].stdin.write(state_xmit)
        players[0].stdin.flush()
        players[1].stdin.write(state_xmit)
        players[1].stdin.flush()

        # swap turns
        turn = (turn+1)%2

    # print outcome
    print "OUTCOME:", outcome

    # kill players, us
    player0.kill()
    player1.kill()
    quit()

elif len(argv)==2:
    if argv[1]=='TYPE':
        print "ONE_ON_ONE\n"
        quit()


