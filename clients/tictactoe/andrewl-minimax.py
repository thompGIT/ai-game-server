#!/usr/bin/python

# textbook (no major optimization) minimax algorithm
# since final game state is reachable in 8! = 40320 nodes, we'll evaluate only at leafs
# leaf node evaluation is simple: {-1,0,1} for {loss,tie,win}
# minor optimizations:
#  you don't need to descend below wins
#  you don't need to descend below non-winnable positions
#  you don't need to descend if a win is already found at the current branch

# to do:
#
# --X-O---- met with 7 means that if O makes any threat, he can draw
#           met with 6, however, means that 2/6 of 0's threats are met with loss
# ...somehow incorporate this - favor paths that have this property
from sys import stdin, stdout
import random
import re

# globals
# current state
g_state = ''
# our player id
g_player_id_us = 0
# their player id
g_player_id_them = 1

class state_possibility:
    def __init__(self, start_state, current_player):
        self.root_state = list(start_state)
        self.player = current_player
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        try:
            while self.root_state[self.index] != '-':
                self.index = self.index + 1
        except:
                raise StopIteration
        possibility = list(self.root_state)
        possibility[self.index] = ['X','O'][self.player]
        self.index = self.index+1
        return possibility

def state_print(state):
    print state[0:3]
    print state[3:6]
    print state[6:9]

def state_test_win(state, player):
    symbol = ['X','O'][player]
    if state[0]==symbol and state[1]==symbol and state[2]==symbol: return 1 # horiz
    if state[3]==symbol and state[4]==symbol and state[5]==symbol: return 1
    if state[6]==symbol and state[7]==symbol and state[8]==symbol: return 1
    if state[0]==symbol and state[3]==symbol and state[6]==symbol: return 1 # vert
    if state[1]==symbol and state[4]==symbol and state[7]==symbol: return 1
    if state[2]==symbol and state[5]==symbol and state[8]==symbol: return 1
    if state[0]==symbol and state[4]==symbol and state[8]==symbol: return 1 # diag
    if state[2]==symbol and state[4]==symbol and state[6]==symbol: return 1
    return 0
   
def state_test_winnable(state):
    # horizontal cases
    seen = {}
    seen[state[0]]=1; seen[state[1]]=1; seen[state[2]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    seen = {}
    seen[state[3]]=1; seen[state[4]]=1; seen[state[5]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    seen = {}
    seen[state[6]]=1; seen[state[7]]=1; seen[state[8]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    # vertical cases
    seen = {}
    seen[state[0]]=1; seen[state[3]]=1; seen[state[6]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    seen = {}
    seen[state[1]]=1; seen[state[4]]=1; seen[state[7]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    seen = {}
    seen[state[2]]=1; seen[state[5]]=1; seen[state[8]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    # diagonal cases
    seen = {}
    seen[state[0]]=1; seen[state[4]]=1; seen[state[8]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    seen = {}
    seen[state[2]]=1; seen[state[4]]=1; seen[state[6]]=1; 
    if '-' in seen: del seen['-']
    if len(seen)==1: return 1
    # else
    return 0
 
def state_eval(state):
    win_us = state_test_win(state, g_player_id_us)
    win_them = state_test_win(state, g_player_id_them)
    if win_us and win_them:
        state_print(state)
        raise Exception("evaluating double-win game state? impossible!")
    if win_us: return 1
    if win_them: return -1
    return 0

def state_test_done(state):
    for i in state:
        if i=='-': return 0
    return 1

def minimax(state, depth):
    global g_player_id_us
    global g_player_id_them

    #for i in range(depth): print ' ',
    #print "minimax(d=%d) " % depth,
    #print "state: ", ''.join(state),

    record_init = 0
    record_score = 0
 
    # win position? leaf node
    pre_eval = state_eval(state)
    if pre_eval != 0:
        record_score = pre_eval
        #print "win, returning ", pre_eval
    # otherwise search
    elif state_test_winnable(state):
        #print ''

        # on even depths (0, 2, 4, ...) it is our turn (maximizing player)
        # on odd depths (1, 3, 5, ...) it is their turn (minimizing player)
        player = [g_player_id_us, g_player_id_them][depth%2]
        func = [max,min][depth%2]
        func_strs = ['max','min']

        # note: tied (fully occupied board) is a leaf node
        for possibility in state_possibility(state, player):
            score = minimax(possibility, depth+1)
            if not record_init:
                record_score = score
                record_init = 1
            else:
                record_score = func(record_score, score)
                
    #for i in range(depth): print ' ',
    #print "minimax(d=%d) done, propogating up %d" % (depth, record_score)
 
    return record_score
   
def calculate_move(state):
    random.seed()
    
    # on opening move, avoid doing a full game tree search...
    if ''.join(state) == '---------':
        return [0, 2, 4, 6, 8][random.randint(0,4)]

    # score all possible moves using minimax
    state_to_score = {}
    for candidate_state in state_possibility(state, g_player_id_us):
        score = minimax(candidate_state, 1)
        state_to_score[''.join(candidate_state)] = score

    # filter states which aren't top scorers
    record_score = max(state_to_score.values())
    for key in state_to_score.keys():
        if state_to_score[key] < record_score:
            del state_to_score[key]

    # note here that a winning move is scored equally to a move that definitely leads to a win
    # rather than make the distinction, let's leave this in so that randomly it will look like
    # the bot is "toying" with the opponent :P

    # pick a random state among the best
    record_states = state_to_score.keys()
    record_state = list(record_states[random.randint(0, len(record_states)-1)])

    # diff the best state vs. the current state to extract the move
    for i in range(9):
        if state[i] != record_state[i]:
            return i

while 1:
    # Read message from the game server
    line = stdin.readline()
    line.rstrip()

    # Message: assign player
    expr = re.match(r"ASSIGN_PLAYER: (\d+)", line)
    if expr:
        g_player_id_us = int(expr.group(1))
        g_player_id_them = (g_player_id_us+1)%2
        continue

    # Message: game state update
    expr = re.match(r"GAMESTATE: ([-XO]{9})", line)
    if expr:
        g_state = expr.group(1)
        continue

    # Message: Move Request
    expr = re.match(r"REQUEST_MOVE", line)
    if expr:
        move = calculate_move(g_state)
        print move
        stdout.flush()
        continue

    # Unknown Message
    print "ERROR: unknown message from server:", line


