import math
board = [' ' for _ in range(9)]
def print_board():
    print()
    for row in [board[i*3:(i+1)*3] for i in range(3)]:
        print('| ' + ' | '.join(row) + ' |')
    print()
def check_winner(brd, player):
    win_combos = [
        [0,1,2], [3,4,5], [6,7,8],  
        [0,3,6], [1,4,7], [2,5,8],  
        [0,4,8], [2,4,6]            
    ]
    for combo in win_combos:
        if all(brd[i] == player for i in combo):
            return True
    return False
def check_draw(brd):
    return ' ' not in brd
def minimax(brd, is_maximizing):
    if check_winner(brd, 'O'):
        return 1
    elif check_winner(brd, 'X'):
        return -1
    elif check_draw(brd):
        return 0
    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if brd[i] == ' ':
                brd[i] = 'O'
                score = minimax(brd, False)
                brd[i] = ' '
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if brd[i] == ' ':
                brd[i] = 'X'
                score = minimax(brd, True)
                brd[i] = ' '
                best_score = min(score, best_score)
        return best_score
def ai_move():
    best_score = -math.inf
    move = 0
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            score = minimax(board, False)
            board[i] = ' '
            if score > best_score:
                best_score = score
                move = i
    board[move] = 'O'
def player_move():
    while True:
        try:
            move = int(input("Enter your move (1-9): ")) - 1
            if move < 0 or move > 8 or board[move] != ' ':
                print("Invalid move. Try again.")
            else:
                board[move] = 'X'
                break
        except ValueError:
            print("Please enter a valid number between 1 and 9.")
def play_game():
    print("Welcome to Tic-Tac-Toe! You are 'X'. The AI is 'O'.")
    print_board()

    while True:
        player_move()
        print_board()
        if check_winner(board, 'X'):
            print("You win! 🎉")
            break
        if check_draw(board):
            print("It's a draw!")
            break

        print("AI is making a move...")
        ai_move()
        print_board()
        if check_winner(board, 'O'):
            print("AI wins!")
            break
        if check_draw(board):
            print("It's a draw!")
            break

play_game()
