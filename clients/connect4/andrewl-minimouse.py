#!/usr/bin/python

from sys import stdin, stdout
import random
import re

# globals
g_max_depth = 5
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
        self.empty_slots = []
        for i in range(8):
            if start_state[i] == '-':
                self.empty_slots.append(i);
    def __iter__(self):
        return self
    def next(self):
        if not self.empty_slots:
            raise StopIteration
        slot = self.empty_slots.pop()
        state = list(self.root_state)
        for row in reversed(range(8)):
            if state[slot + row*8] == '-':
                state[slot + row*8] = ['X','O'][self.player]
                break
        return state

def state_print(state):
    for i in range(8):
        print state[8*i:8*i+8]

def state_test_win(state, player):
    symbol = ['X','O'][player]

    # search for east runs
    for i in range(8):
        for j in range(5):
            if ((state[8*(i)+(j)] == symbol) and (state[8*(i)+(j+1)] == symbol) and (state[8*(i)+(j+2)] == symbol) and (state[8*(i)+(j+3)] == symbol)):
                return 1
    # search for south runs 
    for i in range(5):
        for j in range(8):
            if ((state[8*(i)+(j)] == symbol) and (state[8*(i+1)+(j)] == symbol) and (state[8*(i+2)+(j)] == symbol) and (state[8*(i+3)+(j)] == symbol)):
                return 1
    # search for south east runs
    for i in range(5):
        for j in range(5):
            if ((state[8*(i)+(j)] == symbol) and (state[8*(i+1)+(j+1)] == symbol) and (state[8*(i+2)+(j+2)] == symbol) and (state[8*(i+3)+(j+3)] == symbol)):
                return 1
    # search for north east runs
    for i in reversed(range(4,8)):
        for j in range(5):
            if ((state[8*(i)+(j)] == symbol) and (state[8*(i-1)+(j+1)] == symbol) and (state[8*(i-2)+(j+2)] == symbol) and (state[8*(i-3)+(j+3)] == symbol)):
                return 1

    return 0
   
def state_test_winnable(state):
    return 1
 
def state_eval(state):
    return 0

def state_test_done(state):
    for i in state:
        if i=='-': return 0
    return 1

def minimax(state, depth, limit):
    global g_player_id_us
    global g_player_id_them

    #for i in range(depth): print ' ',
    #print "minimax(d=%d) " % depth,
    #print "state: ", ''.join(state),
    player = [g_player_id_us, g_player_id_them][depth%2]

    record_init = 0
    record_score = 0

    # preempt further descent by detecting a win state right here
    if state_test_win(state, g_player_id_us):
        record_init = 1
        record_score = 100
    elif state_test_win(state, g_player_id_them):
        record_init = 1
        record_score = -100
    # else if we've reached the depth limit, evaluate this state
    elif depth == limit:
        record_init = 1
        record_score = state_eval(state)
    # else keep descending
    else:
        # on even depths (0, 2, 4, ...) it is our turn (maximizing player) (opponent has just moved)
        # on odd depths (1, 3, 5, ...) it is their turn (minimizing player) (we have just moved)
        func = [max,min][depth%2]
        func_strs = ['max','min']

        # note: tied (fully occupied board) is a leaf node
        for possibility in state_possibility(state, player):
            score = minimax(possibility, depth+1, limit)
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
    
    # score all possible moves using minimax
    state_to_score = {}
    for candidate_state in state_possibility(state, g_player_id_us):
        # immediate wins skip further processing (don't appear cocky :P)
        if state_test_win(candidate_state, g_player_id_us):
            state_to_score = { ''.join(candidate_state) : score }
            break
        score = minimax(candidate_state, 1, g_max_depth)
        state_to_score[''.join(candidate_state)] = score

    # filter states which aren't top scorers
    record_score = max(state_to_score.values())
    for key in state_to_score.keys():
        if state_to_score[key] < record_score:
            del state_to_score[key]

    # pick a random state among the best
    record_states = state_to_score.keys()
    record_state = list(record_states[random.randint(0, len(record_states)-1)])

    # diff the best state vs. the current state to extract the move
    for i in range(8):
        for j in range(8):
            if state[8*i+j] != record_state[8*i+j]:
                return j

#derp = state_possibility('----------------------------------------OO------XO------XO-X-XX-', 0)
#for poss in derp:
#    state_print(poss)
#    print "\n"
#quit()

#
# MAIN GAME LOOP
#
while 1:
    # Read message from the game server
    line = stdin.readline()
    line.rstrip()

    # Message: assign player
    expr = re.match(r"^ASSIGN_PLAYER: (\d+)$", line)
    if expr:
        g_player_id_us = int(expr.group(1))
        g_player_id_them = (g_player_id_us+1)%2
        continue

    # Message: game state update
    expr = re.match(r"^GAMESTATE: ([-XO]{64})$", line)
    if expr:
        g_state = expr.group(1)
        continue

    # Message: Move Request
    expr = re.match(r"^REQUEST_MOVE$", line)
    if expr:
        move = calculate_move(g_state)
        print move
        stdout.flush()
        continue

    # Unknown Message
    print "ERROR: unknown message from server:", line


