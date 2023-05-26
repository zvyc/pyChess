import pygame
import time
import sys

def render_squares():
  screen.fill((100, 100, 100))
  for i in range(4):
    for j in range(4):
      pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*160, j*160, 80, 80))
      pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*160 + 80, j*160 + 80, 80, 80))

def render_recent_move(square_1, square_2):
  if square_1 != [-1, -1] and square_2 != [-1, -1]:
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(square_1[1]*80, square_1[0]*80, 80, 80))
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(square_2[1]*80, square_2[0]*80, 80, 80))

def render_game():
  for row_index in range(len(board)):
    for column_index in range(len(board[row_index])):
      piece = board[row_index][column_index]
      if piece != '  ':
        screen.blit(pieces[piece], (column_index*80, row_index*80))

def safe_for_own_king(active_piece, hovering_piece):
  # Copy nested list without reference
  new_board = [row[:] for row in board]

  # Make the move on the copied board 
  new_board[active_piece[0]][active_piece[1]] = '  '
  new_board[hovering_piece[0]][hovering_piece[1]] = active_piece[2]

  # Move rooks if the move is a castling
  if active_piece[2] == 'wK':
    # Castling short
    if active_piece[1] - hovering_piece[1] == -2:
      new_board[7][7] = '  '
      new_board[7][5] = 'wR'
    # Castling long
    elif active_piece[1] - hovering_piece[1] == 2:
      new_board[7][0] = '  '
      new_board[7][3] = 'wR'
  elif active_piece[2] == 'bK':
    # Castling short
    if active_piece[1] - hovering_piece[1] == -2:
      new_board[0][7] = '  '
      new_board[0][5] = 'bR'
    # Castling long
    elif active_piece[1] - hovering_piece[1] == 2:
      new_board[0][0] = '  '
      new_board[0][3] = 'bR'

  king_row = None
  king_column = None

  if active_piece[2][0] == 'w':
    # Find the row and column of the king
    for row_index in range(len(new_board)):
      for column_index in range(len(new_board[row_index])):
        if new_board[row_index][column_index] == 'wK':
          king_row = row_index
          king_column = column_index
          break

    # Check if any enemy piece can capture your king after your move, if so your move is illegal
    for row_index in range(len(new_board)):
      for column_index in range(len(new_board[row_index])):
        piece = [row_index, column_index, new_board[row_index][column_index]]
        if piece[2][0] == 'b' and possible_move(piece, [king_row, king_column, 'wK'], new_board):
          return False

  else:
    # Find the row and column of the king
    for row_index in range(len(new_board)):
      for column_index in range(len(new_board[row_index])):
        if new_board[row_index][column_index] == 'bK':
          king_row = row_index
          king_column = column_index
          break

    # Check if any enemy piece can capture your king after your move, if so your move is illegal
    for row_index in range(len(new_board)):
      for column_index in range(len(new_board[row_index])):
        piece = [row_index, column_index, new_board[row_index][column_index]]
        if piece[2][0] == 'w' and possible_move(piece, [king_row, king_column, 'bK'], new_board):
          return False

  return True

def possible_move(active_piece, hovering_piece, game_board, can_white_castle_short=False, can_white_castle_long=False, can_black_castle_short=False, can_black_castle_long=False):
  row_difference = active_piece[0] - hovering_piece[0]
  column_difference = active_piece[1] - hovering_piece[1]

  # For the path clear horizontal when castling. It is different as we need to check more squares than just between the king and where we click. (The function only need index 1 in the list)
  column_castling_short = [None, 7]
  column_castling_long = [None, 0] 

  # White pawn logic
  if active_piece[2] == 'wP':
    # If the square infront is empty
    if (hovering_piece[2] == '  ') and (row_difference == 1) and (column_difference == 0):
      return True

    # If there is a piece available to capture
    elif (hovering_piece[2] != '  ') and (row_difference == 1) and ((column_difference == 1) or (column_difference == -1)):
      return True

    # Starting move, can move two squares once
    elif (hovering_piece[2] == '  ') and (active_piece[0] == 6) and (row_difference == 2) and (column_difference == 0):
      return True
    
    return False

  # Black pawn logic
  elif active_piece[2] == 'bP':
    # If the square infront is empty
    if (hovering_piece[2] == '  ') and (row_difference == -1) and (column_difference == 0):
      return True

    # If there is a piece available to capture
    elif (hovering_piece[2] != '  ') and (row_difference == -1) and ((column_difference == 1) or (column_difference == -1)):
      return True

    # Starting move, can move two squares once
    elif (hovering_piece[2] == '  ') and (active_piece[0] == 1) and (row_difference == -2) and (column_difference == 0):
      return True

    return False

  # Rook logic
  elif active_piece[2][1] == 'R':
    # Check if rook and the target are on the same column and the path between them is clear
    if column_difference == 0 and path_clear_vertical(active_piece, hovering_piece, game_board):
      return True

    # Check if rook and target sqaure are on the same row and the path between them is clear
    elif row_difference == 0 and path_clear_horizontal(active_piece, hovering_piece, game_board):
      return True
    return False

  # Knight logic
  elif active_piece[2][1] == 'N':
    if (abs(row_difference) == 2 and abs(column_difference) == 1) or (abs(row_difference) == 1 and abs(column_difference) == 2):
      return True
    return False

  # Bishop logic
  elif active_piece[2][1] == 'B':
    if abs(row_difference) == abs(column_difference) and path_clear_diagonally(active_piece, hovering_piece, game_board):
      return True
    return False

  # Queen logic
  elif active_piece[2][1] == 'Q':
    # If the path is clear for either a bishop or a rook move, it is legal
    if (column_difference == 0 and path_clear_vertical(active_piece, hovering_piece, game_board)) or (row_difference == 0 and path_clear_horizontal(active_piece, hovering_piece, game_board)) or (abs(row_difference) == abs(column_difference) and path_clear_diagonally(active_piece, hovering_piece, game_board)):
      return True
    return False

  # White king logic
  elif active_piece[2] == 'wK':
    # Normal moves
    if (abs(column_difference) == 1 and abs(row_difference) == 1) or (abs(column_difference) == 1 and abs(row_difference) == 0) or (abs(column_difference) == 0 and abs(row_difference) == 1):
      return True
    # Castling
    elif (row_difference == 0 and column_difference == -2 and can_white_castle_short and path_clear_horizontal(active_piece, column_castling_short, game_board)):
      return True
    elif (row_difference == 0 and column_difference == 2 and can_white_castle_long and path_clear_horizontal(active_piece, column_castling_long, game_board)):
      return True
    return False

  # Black king logic
  elif active_piece[2] == 'bK':
    # Normal moves
    if (abs(column_difference) == 1 and abs(row_difference) == 1) or (abs(column_difference) == 1 and abs(row_difference) == 0) or (abs(column_difference) == 0 and abs(row_difference) == 1):
      return True
    # Castling
    elif (row_difference == 0 and column_difference == -2 and can_black_castle_short and path_clear_horizontal(active_piece, column_castling_short, game_board)):
      return True
    elif (row_difference == 0 and column_difference == 2 and can_black_castle_long and path_clear_horizontal(active_piece, column_castling_long, game_board)):
      return True
    return False

  return False


def path_clear_vertical(active_piece, hovering_piece, game_board):
  # The range loop needs to go from smallest to largest value, add 1 to the start_range to avoid checking the piece of the selected piece itself
  if active_piece[0]+1 < hovering_piece[0]:
    for row_index in range(active_piece[0]+1, hovering_piece[0]):
      if game_board[row_index][active_piece[1]] != '  ':
        return False
  else:
    for row_index in range(hovering_piece[0]+1, active_piece[0]):
      if game_board[row_index][active_piece[1]] != '  ':
        return False
  return True

def path_clear_horizontal(active_piece, hovering_piece, game_board):
  # The range loop needs to go from smallest to largest value, add 1 to the start_range to avoid checking the piece of the selected piece itself
  if active_piece[1]+1 < hovering_piece[1]:
    for column_index in range(active_piece[1]+1, hovering_piece[1]):
      if game_board[active_piece[0]][column_index] != '  ':
        return False
  else:
    for column_index in range(hovering_piece[1]+1, active_piece[1]):
      if game_board[active_piece[0]][column_index] != '  ':
        return False
  return True

# Works for every diagonal
def path_clear_diagonally(active_piece, hovering_piece, game_board):
  # Path goes from NE to SW
  if (active_piece[0]+1 < hovering_piece[0]) and (active_piece[1] > hovering_piece[1]):
    column_index = active_piece[1]
    for row_index in range(active_piece[0]+1, hovering_piece[0]):
      column_index -= 1
      if game_board[row_index][column_index] != '  ':
        return False
  # Path gors from NW to SE
  elif (active_piece[0]+1 < hovering_piece[0]) and (active_piece[1] < hovering_piece[1]):
    column_index = active_piece[1]
    for row_index in range(active_piece[0]+1, hovering_piece[0]):
      column_index += 1
      if game_board[row_index][column_index] != '  ':
        return False
  # Path goes from SE to NW
  elif (active_piece[0]+1 > hovering_piece[0]) and (active_piece[1] > hovering_piece[1]):
    column_index = hovering_piece[1]
    for row_index in range(hovering_piece[0]+1, active_piece[0]):
      column_index += 1
      if game_board[row_index][column_index] != '  ':
        return False
  # Path goes from SW to NE
  elif (active_piece[0]+1 > hovering_piece[0]) and (active_piece[1] < hovering_piece[1]):
    column_index = hovering_piece[1]
    for row_index in range(hovering_piece[0]+1, active_piece[0]):
      column_index -= 1
      if game_board[row_index][column_index] != '  ':
        return False
  return True

def find_diagonal_positions_between(piece1, piece2):
  path_positions = []
  # Path goes from NE to SW
  if (piece1[0]+1 < piece2[0]) and (piece1[1] > piece2[1]):
    column_index = piece1[1]
    for row_index in range(piece1[0]+1, piece2[0]):
      column_index -= 1
      path_positions.append((row_index, column_index))
      
  # Path gors from NW to SE
  elif (piece1[0]+1 < piece2[0]) and (piece1[1] < piece2[1]):
    column_index = piece1[1]
    for row_index in range(piece1[0]+1, piece2[0]):
      column_index += 1
      path_positions.append((row_index, column_index))

  # Path goes from SE to NW
  elif (piece1[0]+1 > piece2[0]) and (piece1[1] > piece2[1]):
    column_index = piece2[1]
    for row_index in range(piece2[0]+1, piece1[0]):
      column_index += 1
      path_positions.append((row_index, column_index))

  # Path goes from SW to NE
  elif (piece1[0]+1 > piece2[0]) and (piece1[1] < piece2[1]):
    column_index = piece2[1]
    for row_index in range(piece2[0]+1, piece1[0]):
      column_index -= 1
      path_positions.append((row_index, column_index))
  return path_positions

def find_straight_positions_between(piece1, piece2):
  path_positions = []
  # Path goes from NE to SW
  if piece1[1] - piece2[1] == 0:
    if piece1[0]+1 < piece2[0]:
      for row_index in range(piece1[0]+1, piece2[0]):
        path_positions.append((row_index, piece1[1]))
    else:
      for row_index in range(piece2[0]+1, piece1[0]):
        path_positions.append((row_index, piece1[1]))
  elif piece1[0] - piece2[0] == 0:
    if piece1[1]+1 < piece2[1]:
      for column_index in range(piece1[1]+1, piece2[1]):
        path_positions.append((piece1[0], column_index))
    else:
      for column_index in range(piece2[1]+1, piece1[1]):
        path_positions.append((piece1[0], column_index))

  return path_positions


# def is_checkmate(attacking_pos, attacking_piece_type):
def is_checkmate(attacking_piece_type):
  if attacking_piece_type[0] == 'w':
    defending_color = 'b'
  else:
    defending_color = 'w'

  # Find King
  king_row = None
  king_column = None

  for row_index in range(len(board)):
      for column_index in range(len(board[row_index])):
        if board[row_index][column_index] == defending_color + 'K':
          king_row = row_index
          king_column = column_index
          break

  king_piece = [king_row, king_column, defending_color + 'K']
  
  # Check if king is in check
  king_in_check = False
  for row_index in range(len(board)):
      for column_index in range(len(board[row_index])):
        piece = [row_index, column_index, board[row_index][column_index]]
        if piece[2][0] == attacking_piece_type[0] and possible_move(piece, king_piece, board):
          king_in_check = True
          break
  if not king_in_check:
    return False

  ## Check if king can move to any possible position without check
  possible_king_moves = [(king_row+1, king_column),(king_row-1, king_column),(king_row, king_column+1),(king_row, king_column-1),(king_row+1, king_column+1),(king_row-1, king_column-1),(king_row+1, king_column-1),(king_row-1, king_column+1)]
  for row_move, column_move in possible_king_moves:
    if row_move < 0 or row_move > 7 or column_move < 0 or column_move > 7 or board[row_move][column_move][0] == defending_color:
      continue
    king = [king_row, king_column, defending_color + 'K']
    attacker = [row_move, column_move, board[row_move][column_move]]
    if possible_move(king, attacker, board) and safe_for_own_king(king, attacker):
      print("King can move safely!!")
      return False

  # Find the attacker position (have to do this because the moved piece is not always the attacker, see discoverad attack i.e)
  for row_index in range(len(board)):
      for column_index in range(len(board[row_index])):
        attacking_piece = [row_index, column_index, board[row_index][column_index]]
        if attacking_piece[2][0] == attacking_piece_type[0] and possible_move(attacking_piece, [king_row, king_column, 'wK'], board):
          
          # Check for bishop
          if attacking_piece_type[1] == 'B':
            path_positions = find_diagonal_positions_between(attacking_piece, king_piece)

            for pos in path_positions:
              for row_index in range(len(board)):
                for column_index in range(len(board[row_index])):
                  # See if every piece can capture
                  piece = [row_index, column_index, board[row_index][column_index]]
                  if piece[2][0] == defending_color and possible_move(piece, [pos[0], pos[1], board[pos[0]][pos[1]]], board) and safe_for_own_king(piece, [pos[0], pos[1], board[pos[0]][pos[1]]]):
                    print("Can block attacker!")
                    return False

          # Check for rook
          elif attacking_piece_type[1] == 'R':
            path_positions = find_straight_positions_between(attacking_piece, king_piece)

            for pos in path_positions:
              for row_index in range(len(board)):
                for column_index in range(len(board[row_index])):
                  # See if every piece can capture
                  piece = [row_index, column_index, board[row_index][column_index]]
                  if piece[2][0] == defending_color and possible_move(piece, [pos[0], pos[1], board[pos[0]][pos[1]]], board) and safe_for_own_king(piece, [pos[0], pos[1], board[pos[0]][pos[1]]]):
                    print("Can block attacker!")
                    return False

          # Check for queen (All other pieces attacks cant be blocked)
          elif attacking_piece_type[1] == 'Q':
            # If the queen is not horizontally or vertically aligned with the king it has to be attacking from the diagonal
            path_positions = find_straight_positions_between(attacking_piece, king_piece)
            if path_positions == []:
              path_positions = find_diagonal_positions_between(attacking_piece, king_piece)

            for pos in path_positions:
              for row_index in range(len(board)):
                for column_index in range(len(board[row_index])):
                  # See if every piece can capture
                  piece = [row_index, column_index, board[row_index][column_index]]
                  if piece[2][0] == defending_color and possible_move(piece, [pos[0], pos[1], board[pos[0]][pos[1]]], board) and safe_for_own_king(piece, [pos[0], pos[1], board[pos[0]][pos[1]]]):
                    print("Can block attacker!")
                    return False


          ## See if the attacker can be captured
          for row_index in range(len(board)):
              for column_index in range(len(board[row_index])):
                # See if every piece can capture
                piece = [row_index, column_index, board[row_index][column_index]]
                if piece[2][0] == defending_color and possible_move(piece, attacking_piece, board) and safe_for_own_king(piece, attacking_piece):
                  print("Can capture attacker!")
                  return False
          break # Safe (Only one attacker needs to be checked)

  ## Otherwise checkmate
  print("CHECKMATE")
  return True
  
def game_loop():
  fps = 10
  fpsClock = pygame.time.Clock()

  # Clicked piece that is active [board_row, board_column, piece_notation]
  active_piece = [-1, -1, '  ']
  white_to_play = True

  can_white_castle_short = True
  can_white_castle_long = True
  can_black_castle_short = True
  can_black_castle_long = True

  highlight_square_1 = [-1, -1]
  highlight_square_2 = [-1, -1]

  while True:
    mousex, mousey = pygame.mouse.get_pos()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Hovering piece is the piece/square that you've clicked on
        hovering_piece = [mousey//80, mousex//80, board[mousey//80][mousex//80]]

        legal_move = possible_move(active_piece, hovering_piece, board, can_white_castle_short, can_white_castle_long, can_black_castle_short, can_black_castle_long)

        if white_to_play:
          # If you've clicked on one of your own pieces (white), change it to your active piece
          if hovering_piece[2][0] == 'w':
            active_piece = hovering_piece
          # Try to move the piece to your clicked on square if it is a possible move
        
          elif legal_move:
            if safe_for_own_king(active_piece, hovering_piece):
              if active_piece[2] == 'wK':
                # Castling short
                if active_piece[1] - hovering_piece[1] == -2 and can_white_castle_short:
                  board[7][7] = '  '
                  board[7][5] = 'wR'
                # Castling long
                elif active_piece[1] - hovering_piece[1] == 2 and can_white_castle_long:
                  board[7][0] = '  '
                  board[7][3] = 'wR'

                can_white_castle_short = False
                can_white_castle_long = False
              # Disable castling short/long depending on which rooks move (if a piece moves from the rooks original squares we know that castling is disabled)
              elif active_piece[0] == 7 and active_piece[1] == 7:
                can_white_castle_short = False
              elif active_piece[0] == 7 and active_piece[1] == 0:
                can_white_castle_long = False

              # If there is a promotion, make a queen
              if active_piece[2] == 'wP' and hovering_piece[0] == 0:
                active_piece[2] = 'wQ'

              board[active_piece[0]][active_piece[1]] = '  '
              board[hovering_piece[0]][hovering_piece[1]] = active_piece[2]
              highlight_square_1 = active_piece
              highlight_square_2 = hovering_piece
              white_to_play = False
              print("VALID")
              #            attacking pos, attacking piece type
              is_checkmate(active_piece[2])
              active_piece = [-1, -1, '  ']
            else:
              print("KING IS NOT SAFE")
        else:
          # If you've clicked on one of your own pieces (black), change it to your active piece
          if hovering_piece[2][0] == 'b':
            active_piece = hovering_piece
          # Try to move the piece to your clicked on square if it is a possible move
          elif legal_move:
            if safe_for_own_king(active_piece, hovering_piece):
              if active_piece[2] == 'bK':
                # Castling short
                if active_piece[1] - hovering_piece[1] == -2 and can_black_castle_short:
                  board[0][7] = '  '
                  board[0][5] = 'bR'
                # Castling long
                elif active_piece[1] - hovering_piece[1] == 2 and can_black_castle_long:
                  board[0][0] = '  '
                  board[0][3] = 'bR'

                can_black_castle_short = False
                can_black_castle_long = False
              # Disable castling short/long depending on which rooks move (if a piece moves from the rooks original squares we know that castling is disabled)
              elif active_piece[0] == 0 and active_piece[1] == 7:
                can_black_castle_short = False
              elif active_piece[0] == 0 and active_piece[1] == 0:
                can_black_castle_long = False

              # If there is a promotion, make a queen
              if active_piece[2] == 'bP' and hovering_piece[0] == 7:
                active_piece[2] = 'bQ'

              board[active_piece[0]][active_piece[1]] = '  '
              board[hovering_piece[0]][hovering_piece[1]] = active_piece[2]
              highlight_square_1 = [active_piece[0], active_piece[1]]
              highlight_square_2 = [hovering_piece[0], hovering_piece[1]]
              white_to_play = True
              print("VALID")
              # is_checkmate(hovering_piece, active_piece[2])
              is_checkmate(active_piece[2])
              active_piece = [-1, -1, '  ']
            else:
              print("KING IS NOT SAFE")
  
    # Update display
    render_squares()
    render_recent_move(highlight_square_1, highlight_square_2)
    render_game()

    # Draw
    pygame.display.flip()
    fpsClock.tick(fps)


if __name__ == '__main__':
  pygame.init()
  pygame.display.set_caption('Chess')
  width, height = 640, 640
  screen = pygame.display.set_mode((width, height))
  
  # First letter is the color, second letter is the piece
  pieces = {'bP': pygame.image.load('pieces/bP.png'),
            'bR': pygame.image.load('pieces/bR.png'),
            'bB': pygame.image.load('pieces/bB.png'),
            'bK': pygame.image.load('pieces/bK.png'),
            'bQ': pygame.image.load('pieces/bQ.png'),
            'bN': pygame.image.load('pieces/bN.png'),
            'wP': pygame.image.load('pieces/wP.png'),
            'wR': pygame.image.load('pieces/wR.png'),
            'wB': pygame.image.load('pieces/wB.png'),
            'wK': pygame.image.load('pieces/wK.png'),
            'wQ': pygame.image.load('pieces/wQ.png'),
            'wN': pygame.image.load('pieces/wN.png')}

  board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
           ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
           ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
           ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
           ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
           ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
           ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
           ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

  game_loop()

# Add en pessant