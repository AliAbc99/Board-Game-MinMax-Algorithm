#Ali Abbasi Dolatabadi 
import copy
import random

# Constants
EMPTY = '.'
T_COLOR = 'T'  # Player 1 (AI) pieces
O_COLOR = 'O'  # Player 2 (Human) pieces
MAX_MOVES = 50
rows, cols = 7, 7
ai_locked = False # if true, AI will lose the game in the next move. what ever it does.
ai_depth = 2 # AI search depth


# normal game board
player1_pieces = [(0, 0), (2, 0), (4, 6), (6, 6)]  # Initial positions for AI
player2_pieces = [(0, 6), (2, 6), (4, 0), (6, 0)]  # Initial positions for Human

board = [[EMPTY for _ in range(cols)] for _ in range(rows)]
for r, c in player1_pieces:
    board[r][c] = T_COLOR
for r, c in player2_pieces:
    board[r][c] = O_COLOR

# Helper function to print the board
def print_board():
    print("   " + " ".join(str(i) for i in range(cols)))
    for i, row in enumerate(board):
        print(f"{i}  " + " ".join(row))
    print("\n")


# Heuristic Function
def evaluate_board(board):
    AI_pieces = sum(row.count(T_COLOR) for row in board)
    Human_pieces = sum(row.count(O_COLOR) for row in board)
   
    # Mobility scores
    mobility_ai = len(generate_moves(board, T_COLOR))
    mobility_human = len(generate_moves(board, O_COLOR))
        
    # Calculate the final heuristic score
    heuristic = 5 * (AI_pieces - Human_pieces)  + \
                1 * (mobility_ai - mobility_human) 

    return heuristic

# Generate all possible moves for a player
def generate_moves(board , player):
    moves = []
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == player:
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < rows and 0 <= new_c < cols and board[new_r][new_c] == EMPTY:
                        moves.append(((r, c), (new_r, new_c)))
    return moves

# Simulate a move on the board. returns a new board after the move.
def make_temp_move(board_state, move, player):
    start, end = move
    new_board = copy.deepcopy(board_state)
    new_board[start[0]][start[1]] = EMPTY
    new_board[end[0]][end[1]] = player
    new_board = capture_temp_board(new_board, player , end[0] , end[1])
    return new_board

# checks for captured pieces and returns the new board. 
# it is same as check_capture but it does not modify the main board. it takes a temp board and returns a temp board.
def capture_temp_board(board, player , r, c):
    opponent = O_COLOR if player == T_COLOR else T_COLOR

    list_of_capture = []

    def check_col(r,c,opponent):
        next = r + 1
        prev = r - 1
        
        while ( next < rows ) :
            if board[next][c] == opponent : break
            if board[next][c] == EMPTY  : return
            next += 1
        
        while ( prev >= 0 ) :
            if board[prev][c] == opponent : break
            if board[prev][c] == EMPTY : return
            prev -= 1

        for i in range(prev+1, next):
            list_of_capture.append((i,c))

    def check_row(r,c,opponent):
        next = c + 1
        prev = c - 1
        
        while ( next < cols ) :
            if board[r][next] == opponent : break
            if board[r][next] == EMPTY : return
            next += 1
      
        while ( prev >= 0 ) :
            if board[r][prev] == opponent : break
            if board[r][prev] == EMPTY : return
            prev -= 1

        for i in range(prev+1, next):
            list_of_capture.append((r,i))
    
    check_row(r,c , opponent = opponent)
    check_col(r,c , opponent = opponent)

    if c > 0 :
        if board[r][c-1] == opponent:
            check_row(r,c-1, opponent = player)

    if c < cols - 1:
        if board[r][c+1] == opponent:
            check_row(r,c+1, opponent = player)
               
    if r > 0:
        if board[r-1][c] == opponent:
            check_col(r-1,c, opponent = player)

    if r < rows - 1:
        if board[r+1][c] == opponent:
            check_col(r+1,c, opponent = player)


    for r,c in list_of_capture:
        board[r][c] = EMPTY    

    return board

# Minimax Algorithm
def minimax(board_state, depth, is_maximizing, alpha, beta):
    if depth == 0:
        return evaluate_board(board_state)

    player = T_COLOR if is_maximizing else O_COLOR
    best_score = float('-inf') if is_maximizing else float('inf')

    for move in generate_moves(board_state, player):
        new_board = make_temp_move(board_state, move, player)
        score = minimax(new_board, depth - 1, not is_maximizing, alpha, beta)
        if is_maximizing:
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
        else:
            best_score = min(best_score, score)
            beta = min(beta, best_score)
        if beta <= alpha:
            break

    return best_score

# AI Move Logic (with two-move rule).
def ai_make_move():
    moves = generate_moves(board,T_COLOR)
    #print(f"AI available moves: {moves}")  # Debugging
    if len(moves) == 0:
        print("AI has no valid moves.")
        return

    best_score = float('-inf')
    best_move = None
    selected_moves = []

    # AI makes two moves if it has more than one piece
    move_count = 2 if sum(row.count(T_COLOR) for row in board) > 1 else 1

    
    for _ in range(move_count):
        random.shuffle(moves)
        best_move = None
        best_score = float('-inf')
        for move in moves:
            new_board = make_temp_move(board, move, T_COLOR)
            score = minimax(new_board, depth=ai_depth, is_maximizing=False, alpha=float('-inf'), beta=float('inf'))
            #print(f"Evaluating move {move} with score {score}")  # Debugging
            if score > best_score:
                best_score = score
                best_move = move

        if best_move:
            #print(f"AI selects move: {best_move} with score: {best_score}")  # Debugging
            start, end = best_move
            board[start[0]][start[1]] = EMPTY
            board[end[0]][end[1]] = T_COLOR
            check_capture(T_COLOR , end[0] , end[1])
            selected_moves.append(best_move)
            moves = generate_moves(board, T_COLOR)
            moves = remove_moves_with_start(moves, end)  # Remove all moves with the same start
        else:
            print("AI could not find a valid move.")  # Debugging
            lock_ai()          

    print(f"AI selects moves: {['>>'.join(map(str, move)) for move in selected_moves]}")
    #print(f"AI selects moves: { selected_moves }")  # Debuggin

#Function to Remove Moves with the Same Start as the "start" input
def remove_moves_with_start(moves, start):
    """Remove all moves from the list that start at the given position."""
    return [move for move in moves if move[0] != start]

#Function to Remove Moves with the Same end as the "end" input
def remove_moves_with_end(moves, end):
    """Remove all moves from the list that end at the given position."""
    return [move for move in moves if move[1] != end]

#Function to Check Captured pieces. it modifies the main board.
def check_capture(player , r, c):
    opponent = O_COLOR if player == T_COLOR else T_COLOR

    list_of_capture = []

    def check_col(r,c,opponent):
        next = r + 1
        prev = r - 1
        
        while ( next < rows ) :
            if board[next][c] == opponent : break
            if board[next][c] == EMPTY  : return
            next += 1
        
        while ( prev >= 0 ) :
            if board[prev][c] == opponent : break
            if board[prev][c] == EMPTY : return
            prev -= 1

        for i in range(prev+1, next):
            list_of_capture.append((i,c))

    def check_row(r,c,opponent):
        next = c + 1
        prev = c - 1
        
        while ( next < cols ) :
            if board[r][next] == opponent : break
            if board[r][next] == EMPTY : return
            next += 1
      
        while ( prev >= 0 ) :
            if board[r][prev] == opponent : break
            if board[r][prev] == EMPTY : return
            prev -= 1

        for i in range(prev+1, next):
            list_of_capture.append((r,i))
    
    check_row(r,c , opponent = opponent)
    check_col(r,c , opponent = opponent)

    if c > 0 :
        if board[r][c-1] == opponent:
            check_row(r,c-1, opponent = player)

    if c < cols - 1:
        if board[r][c+1] == opponent:
            check_row(r,c+1, opponent = player)
               
    if r > 0:
        if board[r-1][c] == opponent:
            check_col(r-1,c, opponent = player)

    if r < rows - 1:
        if board[r+1][c] == opponent:
            check_col(r+1,c, opponent = player)


    for r,c in list_of_capture:
        board[r][c] = EMPTY    

    if len(list_of_capture) == 0:
        return False
    return True

# Check if the game has ended
def check_game_end(move_count):
    p1_count = sum(row.count(T_COLOR) for row in board)
    p2_count = sum(row.count(O_COLOR) for row in board)
    if p1_count == 0 and p2_count == 0:
        return True, "Draw"
    elif p1_count == 0:
        return True, "Player 2 (Human) wins"
    elif p2_count == 0:
        return True, "Player 1 (AI) wins"
    elif move_count >= MAX_MOVES:
        if p1_count == p2_count:
            return True, "Draw"
        return True, "Player 1 (AI) wins" if p1_count > p2_count else "Player 2 (Human) wins"
    return False, ""

# Lock the AI if it will lose the game in the next move
def lock_ai():
    global ai_locked
    ai_locked = True


# Main game loop
def main():
    print("Welcome to the Strategic Board Game!")
    print("Player 1: AI (Triangles - T)")
    print("Player 2: Human (Circles - O)")
    print("Guid: Your move should be in this format: (start_row start_col end_row end_col). For example: 4 0 4 1")
    print("Type 'exit' to quit the game.\n")
    

    current_player = T_COLOR  # AI starts first
    move_count = 0

    while True:
        print_board()
        print(f"Current Player: {'Player 1 (AI)' if current_player == T_COLOR else 'Player 2 (Human)'}")

        if current_player == T_COLOR:
            print("AI is making its moves...")
            ai_make_move()

        else:
            # Human makes two moves if they have more than one piece
            moves = generate_moves(board, O_COLOR)

            for _ in range(2 if sum(row.count(O_COLOR) for row in board) > 1 else 1):                                
                while True:
                    move = input(f"Enter your {'NEXT ' if _ == 1 else ''}move (start_row start_col end_row end_col). For example 4 0 4 1: \n").strip()
                    if move.lower() == "exit":
                        return
                    try:
                        start_row, start_col, end_row, end_col = map(int, move.split())
                        if ((start_row, start_col), (end_row, end_col)) in moves:
                            board[start_row][start_col] = EMPTY
                            board[end_row][end_col] = O_COLOR
                            check_capture(O_COLOR , end_row , end_col)
                            moves = generate_moves(board, O_COLOR)
                            moves = remove_moves_with_start(moves, (end_row, end_col))  # Remove all moves with the same start
                            break  # Exit the loop after a valid move
                        else:
                            print("Invalid move! Try again.")
                    except ValueError:
                        print("Invalid input! Please use the format: start_row start_col end_row end_col")
                print(f" Human move number: {_+1}") 
                if _ <1 : print_board()

        if ai_locked:
            print("AI is locked. it will lose the game in the next move. where ever it moves :( ")
            break
            

        move_count += 1
        game_end, message = check_game_end(move_count)
        if game_end:
            print_board()
            print(message)
            break

        current_player = T_COLOR if current_player == O_COLOR else O_COLOR

    print("Thank you for playing!")

if __name__ == "__main__":
    main()
