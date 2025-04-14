import random
import pygame
import numpy as np
import math
from connect4 import connect4
from copy import deepcopy
import sys

class connect4Player(object):
	def __init__(self, position, seed=0, CVDMode=False):
		self.position = position
		self.opponent = None
		self.seed = seed
		random.seed(seed)
		if CVDMode:
			global P1COLOR
			global P2COLOR
			P1COLOR = (227, 60, 239)
			P2COLOR = (0, 255, 0)

	def play(self, env: connect4, move_dict: dict) -> None:
		move_dict["move"] = -1

class humanConsole(connect4Player):
	'''
	Human player where input is collected from the console
	'''
	def play(self, env: connect4, move_dict: dict) -> None:
		move_dict['move'] = int(input('Select next move: '))
		while True:
			if int(move_dict['move']) >= 0 and int(move_dict['move']) <= 6 and env.topPosition[int(move_dict['move'])] >= 0:
				break
			move_dict['move'] = int(input('Index invalid. Select next move: '))

class humanGUI(connect4Player):
	'''
	Human player where input is collected from the GUI
	'''

	def play(self, env: connect4, move_dict: dict) -> None:
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, P1COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, P2COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move_dict['move'] = col
					done = True

class randomAI(connect4Player):
	'''
	connect4Player that elects a random playable column as its move
	'''

	def play(self, env: connect4, move_dict: dict) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move_dict['move'] = random.choice(indices)

class stupidAI(connect4Player):
	'''
	connect4Player that will play the same strategy every time
	Tries to fill specific columns in a specific order 
	'''
	def play(self, env: connect4, move_dict: dict) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if 3 in indices:
			move_dict['move'] = 3
		elif 2 in indices:
			move_dict['move'] = 2
		elif 1 in indices:
			move_dict['move'] = 1
		elif 5 in indices:
			move_dict['move'] = 5
		elif 6 in indices:
			move_dict['move'] = 6
		else:
			move_dict['move'] = 0

class minimaxAI(connect4Player):

	def __init__(self, position, seed=0, CVDMode=False):
		super().__init__(position, seed, CVDMode)
		self.depth = 3 # the depth of search in miniax

	def play(self, env: connect4, move_dict: dict) -> None: # to decide and return on a move
		env_copy = env.getEnv()
		score, best_move = self.minimax(env_copy, self.depth, True)
		move_dict["move"] = best_move

	def minimax(self, env, depth, maximizingPlayer): # recursively explores the game tree up to depth levels, going from maxmimizing the AI and minimizing the opponent layers.
		if depth == 0 or self.is_terminal_node(env):
			return self.score_position(env.board, self.position), None
		valid_moves = self.get_valid_moves(env)
		if maximizingPlayer:
			value = -math.inf
			best_move = random.choice(valid_moves)
			for move in valid_moves:
				
				row = self.make_move(env, move, self.position)
				score, _ = self.minimax(env, depth - 1, False)
				# self.undo_move 
				if score > value:
					value = score
					best_move = move
			return value, best_move
		else:
			opponent = 1 if self.position == 2 else 2
			value = math.inf
			best_move = random.choice(valid_moves)
			for move in valid_moves:
				row = self.make_move(env, move, opponent)
				score, _ = self.minimax(env, depth - 1, True)
				self.undo_move(env, move, row)
				if score < value:
					value = score
					best_move = move
			return value, best_move

	def get_valid_moves(self, env): # returns a list of column indices that are valid to play
		return [c for c, pos in enumerate(env.topPosition) if pos >= 0]

	def make_move(self, env, move, player): # places a piece for 'player' in the specified 'move' column and decrements the top position so future pieces stack on top
		row = env.topPosition[move]
		env.board[row][move] = player
		env.topPosition[move] -= 1
		return row

	def undo_move(self, env, move, row): # reverts a move in a given columnand increments the top position to allow future pieces to be played there again
		env.topPosition[move] += 1
		env.board[env.topPosition[move]][move] = 0

	def is_terminal_node(self, env):
		return (self.winning_move(env.board, self.position) or
			self.winning_move(env.board, 1 if self.position == 2 else 2) or
			len(self.get_valid_moves(env)) == 0)

	def winning_move(self, board, player): # checks if the player has 4 in a row (horizontally, vertically, or diagonally)
		ROW_COUNT, COL_COUNT = board.shape
		
		# horizontal
  
		for r in range(ROW_COUNT):
			for c in range(COL_COUNT - 3):
				if board[r][c] == player and board[r][c+1] == player and \
					board[r][c+2] == player and board[r][c+3] == player:
					return True
		# vertical
  
		for c in range(COL_COUNT):
			for r in range(ROW_COUNT - 3):
				if board[r][c] == player and board[r+1][c] == player and \
					board[r+2][c] == player and board[r+3][c] == player:
					return True
		# positive diagonal
  
		for r in range(ROW_COUNT - 3):
			for c in range(COL_COUNT - 3):
				if board[r][c] == player and board[r+1][c+1] == player and \
					board[r+2][c+2] == player and board[r+3][c+3] == player:
					return True
		# negative diagonal
  
		for r in range(3, ROW_COUNT):
			for c in range(COL_COUNT - 3):
				if board[r][c] == player and board[r-1][c+1] == player and \
					board[r-2][c+2] == player and board[r-3][c+3] == player:
					return True
		return False

	def score_position(self, board, player):
     
		# if the current board is a terminal winning position for the player,  then it is a huge positive
		if self.winning_move(board, player):
			return 10**9
		# if the current board is a terminal winning position for the opponent, then it is huge negative
		opponent = 1 if player == 2 else 2
		if self.winning_move(board, opponent):
			return -10**9

		ROW_COUNT, COL_COUNT = board.shape
		score = 0
		# additional bonus for center column
		center_col = 3
		if center_col < COL_COUNT: # Only if board has 7 columns
			center_array = [int(board[r][center_col]) for r in range(ROW_COUNT)]
			score += center_array.count(player) * 10
		# Evaluate all 4-cell windows
		# horizontal
		for r in range(ROW_COUNT):
			for c in range(COL_COUNT - 3):
				window = [board[r][c + i] for i in range(4)]
				score += self.evaluate_window(window, player)
		# vertical
		for c in range(COL_COUNT):
			for r in range(ROW_COUNT - 3):
				window = [board[r + i][c] for i in range(4)]
				score += self.evaluate_window(window, player)
		# positive diagonal
		for r in range(ROW_COUNT - 3):
			for c in range(COL_COUNT - 3):
				window = [board[r + i][c + i] for i in range(4)]
				score += self.evaluate_window(window, player)
		# negative diagonal
		for r in range(3, ROW_COUNT):
			for c in range(COL_COUNT - 3):
				window = [board[r - i][c + i] for i in range(4)]
				score += self.evaluate_window(window, player)
		return score

	def evaluate_window(self, window, player):
		opponent = 1 if player == 2 else 2
		window_count = window.count(player)
		opp_count = window.count(opponent)
		empty_count = window.count(0)
		# If 4 in a row, then +100 
		if window_count == 4:
			return 100
		# If 3 in a row + 1 empty, then +5
		elif window_count == 3 and empty_count == 1:
			return 5
		# If 2 in a row + 2 empty, then +2 
		elif window_count == 2 and empty_count == 2:
			return 2
		# If opponent 3 in a row + 1 empty, then -5
		if opp_count == 3 and empty_count == 1:
			return -5
		return 0


class alphaBetaAI(connect4Player):

	# def __init__(self, position, seed=0, CVDMode=False):
	# 	super().__init__(position, seed, CVDMode)

	def play(self, env: connect4, move_dict: dict) -> None:
		env_copy = env.getEnv()
		depth = 4
		score, best_move = self.minimax(env_copy, depth, -math.inf, math.inf, True)
		move_dict["move"] = best_move

	def minimax(self, env, depth, alpha, beta, maximizingPlayer): # minimax search with the alpha-beta pruning
		if depth == 0 or self.is_terminal_node(env):
			return self.score_position(env.board, self.position), None
		valid_moves = self.get_valid_moves(env)

		if maximizingPlayer:
			value = -math.inf
			best_move = random.choice(valid_moves)
			for move in valid_moves:
				row = self.make_move(env, move, self.position)
				score, _ = self.minimax(env, depth - 1, alpha, beta, False)
				self.undo_move(env, move, row)
				if score > value:
					value = score
					best_move = move
				alpha = max(alpha, value)
				if alpha >= beta:
					break # the beta's cutoff
			return value, best_move
		else:
			opponent = 1 if self.position == 2 else 2
			value = math.inf
			best_move = random.choice(valid_moves)
			for move in valid_moves:
				row = self.make_move(env, move, opponent)
				score, _ = self.minimax(env, depth - 1, alpha, beta, True)
				self.undo_move(env, move, row)
				if score < value:
					value = score
					best_move = move
				beta = min(beta, value)
				if alpha >= beta:
					break # the alpha's cutoff
			return value, best_move

	def get_valid_moves(self, env): # returns the columns that are not filled yet
		return [c for c, pos in enumerate(env.topPosition) if pos >= 0]

	def make_move(self, env, move, player): # this places a piece for the player in the given column to move
		row = env.topPosition[move]
		env.board[row][move] = player
		env.topPosition[move] -= 1
		return row

	def undo_move(self, env, move, row):
		env.topPosition[move] += 1
		env.board[env.topPosition[move]][move] = 0

	def is_terminal_node(self, env):
		return (self.winning_move(env.board, self.position) or
			self.winning_move(env.board, 1 if self.position == 2 else 2) or
			len(self.get_valid_moves(env)) == 0)

	def winning_move(self, board, player):
		ROW_COUNT, COL_COUNT = board.shape
		for r in range(ROW_COUNT):
			for c in range(COL_COUNT - 3):
				if board[r][c] == player and board[r][c+1] == player and \
					board[r][c+2] == player and board[r][c+3] == player:
					return True
		for c in range(COL_COUNT):
			for r in range(ROW_COUNT - 3):
				if board[r][c] == player and board[r+1][c] == player and \
					board[r+2][c] == player and board[r+3][c] == player:
					return True
		for r in range(ROW_COUNT - 3):
			for c in range(COL_COUNT - 3):
				if board[r][c] == player and board[r+1][c+1] == player and \
					board[r+2][c+2] == player and board[r+3][c+3] == player:
					return True
		for r in range(3, ROW_COUNT):
			for c in range(COL_COUNT - 3):
				if board[r][c] == player and board[r-1][c+1] == player and \
					board[r-2][c+2] == player and board[r-3][c+3] == player:
					return True
		return False

	def score_position(self, board, player):
		if self.winning_move(board, player):
			return 10**9
		opponent = 1 if player == 2 else 2
		if self.winning_move(board, opponent):
			return -10**9
		ROW_COUNT, COL_COUNT = board.shape
		score = 0
		# bonus for the center column
		center_col = 3
		if center_col < COL_COUNT:
			center_array = [int(board[r][center_col]) for r in range(ROW_COUNT)]
			score += center_array.count(player) * 10
		# Now evaluate all 4-cell windows
		# horizontal
		for r in range(ROW_COUNT):
			for c in range(COL_COUNT - 3):
				window = [board[r][c + i] for i in range(4)]
				score += self.evaluate_window(window, player)
		# vertical
		for c in range(COL_COUNT):
			for r in range(ROW_COUNT - 3):
				window = [board[r + i][c] for i in range(4)]
				score += self.evaluate_window(window, player)
		# positive diagonal
		for r in range(ROW_COUNT - 3):
			for c in range(COL_COUNT - 3):
				window = [board[r + i][c + i] for i in range(4)]
				score += self.evaluate_window(window, player)
		# negative diagonal
		for r in range(3, ROW_COUNT):
			for c in range(COL_COUNT - 3):
				window = [board[r - i][c + i] for i in range(4)]
				score += self.evaluate_window(window, player)
		return score

	def evaluate_window(self, window, player): # evaluates a group of 4 cells and returns a small score that indicates how good or bad this window is for the player
		opponent = 1 if player == 2 else 2 # to set player values accurately 
		window_count = window.count(player)

		opp_count = window.count(opponent)
		empty_count = window.count(0)
		if window_count == 4:
			return 100
		elif window_count == 3 and empty_count == 1:
			return 5
		elif window_count == 2 and empty_count == 2:
			return 2
		if opp_count == 3 and empty_count == 1:
			return -5
		return 0

		

# Defining Constants
SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
P1COLOR = (255,0,0)
P2COLOR = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)





