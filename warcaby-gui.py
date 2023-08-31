################################################
import pygame
import pygame.image
import time
import os
from PIL import Image

# Define the colors
LIGHT_SQUARE_COLOR = (245, 222, 179)
DARK_SQUARE_COLOR = (139, 69, 19)
WHITE_PAWN_COLOR = (255, 255, 255)
BLACK_PAWN_COLOR = (0, 0, 0)
GREY_PAWN_COLOR = (128, 128, 128)
PINK_PAWN_Color = (255, 192, 203)

# Define the dimensions of the game board
BOARD_WIDTH = 8
BOARD_HEIGHT = 8

# Define the size of each square on the game board
SQUARE_SIZE = 80

def visualize_game_board(board, turn_number, display_time):
    # Calculate the width and height of the window
    window_width = BOARD_WIDTH * SQUARE_SIZE
    window_height = BOARD_HEIGHT * SQUARE_SIZE

    # Initialize the Pygame library
    pygame.init()

    # Create the game window
    window = pygame.display.set_mode((window_width, window_height))

    # Set the window title
    pygame.display.set_caption('Checkers Game')

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the game board
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                square_color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
                pygame.draw.rect(window, square_color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                if board[row][col] != ' ':
                    if board[row][col] == 'O' :
                        pawn_color = WHITE_PAWN_COLOR
                    if board[row][col] == 'X' :
                        pawn_color = BLACK_PAWN_COLOR
                    if board[row][col] == 'KO' :
                        pawn_color = PINK_PAWN_Color
                    if board[row][col] == 'KX' :
                        pawn_color = GREY_PAWN_COLOR


                    pygame.draw.circle(window, pawn_color, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 5)

        # Update the display
        pygame.display.flip()

        time.sleep(display_time)
        running = False

    # Quit the Pygame library
    pygame.image.save(window, f'jpg_from_checkers/turn_{turn_number}.jpg')
    pygame.quit()

def create_gif_from_folder(folder_path, gif_path, duration=200):
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jpg')])

    images = []
    for file_name in image_files:
        file_path = os.path.join(folder_path, file_name)
        img = Image.open(file_path)
        images.append(img)

    # Save the images as an animated GIF
    images[0].save(gif_path, save_all=True, append_images=images[1:], optimize=False, duration=duration, loop=0)

################################################


# tworzę tablice Qlearningowe dla obu kolorów
Qtable_X = {}
Qtable_O = {}
nr_rozgrywki = 1

# tworzymy początkowy stan planszy
board = [[' ' for _ in range(8)] for _ in range(8)]

def reset_board():
    global board
    board = [[' ' for _ in range(8)] for _ in range(8)]

    counter = 0
    for row in board:
        if counter < 3 :
            for i in range(8):
                if counter % 2 == 0:
                    if i % 2 == 0:
                        row[i] = 'O'
                if counter % 2 != 0:
                    if i % 2 != 0:
                        row[i] = 'O'

        if counter > 4 :
            for i in range(8):
                if counter % 2 == 0:
                    if i % 2 == 0:
                        row[i] = 'X'
                if counter % 2 != 0:
                    if i % 2 != 0:
                        row[i] = 'X'

        counter += 1

reset_board()

def flatten_board(board):
    key = ""
    for i in board:
        for j in i:
            key += j
    return key

# wyświetlamy stan planszy (wizualizacja
def print_board():
    print("   A B C D E F G H")
    print("  -----------------")
    for i in range(8):
        print(i+1, "|", end=" ")
        for j in range(8):
            print(board[i][j], end=" ")
        print("|", i+1)
    print("  -----------------")
    print("   A B C D E F G H")


# sprawdzamy czy ruch jest możliwy do wykonania
def is_valid_move(start, end, player, bicie = False):
    y1, x1 = start
    y2, x2 = end
    #print(start, end)
    #print(board[x1][y1])
    if bicie == False:
        # sprawdź czy ruch zmieści się na planszy
        if not (0 <= x1 < 8) or not (0 <= y1 < 8) or not (0 <= x2 < 8) or not (0 <= y2 < 8):
            return False

        # sprawdź czy końcowa pozycja pionka jest pusta
        if board[x2][y2] != ' ':
            return False

        # sprawdź czy gracz rusza swoim własnym pionkiem
        if player == 'X' and (board[x1][y1] != 'X' and board[x1][y1] != 'KX'):
            return False
        if player == 'O' and (board[x1][y1] != 'O' and board[x1][y1] != 'KO'):
            return False

        # sprawdź czy ruch jest po diagonali
        if abs(x2 - x1) != 1 or abs(y2 - y1) != 1:
            return False

        # sprawdź czy pionek nie jest damką i jeśli nie jest to nie pozwalaj mu się cofać.
        # Funkcja równocześnie pozwala na dowolne poruszanie się damkom
        if board[x1][y1] == 'X':
            if x2 > x1:
                return False
        if board[x1][y1] == 'O':
            if x2 < x1:
                return False
    if bicie == True:
        bity_x, bity_y = int((x1 + x2) / 2), int((y1 + y2) / 2)
        # sprawdź czy ruch zmieści się na planszy
        if not (0 <= x1 < 8) or not (0 <= y1 < 8) or not (0 <= x2 < 8) or not (0 <= y2 < 8):
            return False

        # sprawdź czy końcowa pozycja pionka jest pusta
        if board[x2][y2] != ' ':
            return False

        # sprawdź czy gracz rusza swoim własnym pionkiem
        if player == 'X' and board[x1][y1] != 'X':
            return False
        if player == 'O' and board[x1][y1] != 'O':
            return False

        # sprawdź, czy zbijamy pionek przeciwnika
        if player == 'X':
            if board[bity_x][bity_y] != 'O' and board[bity_x][bity_y] != 'KO':
                return False
        if player == 'O':
            if board[bity_x][bity_y] != 'X' and board[bity_x][bity_y] != 'KX':
                return False

        if board[x1][y1] == 'KX' or board[x1][y1] == 'KO':
            if abs(x2 - x1) == 1 or abs(y2 - y1) == 1:
                pass
            elif abs(x2 - x1) == 2 or abs(y2 - y1) == 2:
                pass
            elif abs(x2 - x1) == 3 or abs(y2 - y1) == 3:
                pass
            elif abs(x2 - x1) == 4 or abs(y2 - y1) == 4:
                pass
            elif abs(x2 - x1) == 5 or abs(y2 - y1) == 5:
                pass
            elif abs(x2 - x1) == 6 or abs(y2 - y1) == 6:
                pass
            elif abs(x2 - x1) == 7 or abs(y2 - y1) == 7:
                pass
            elif abs(x2 - x1) == 8 or abs(y2 - y1) == 8:
                pass

        # sprawdź czy ruch jest po diagonali i nie pozwala pionką skakać dalej niż o jedno pole
        # tutaj trzeba ter zrobić wyjątek dla damek
        if abs(x2 - x1) != 2 or abs(y2 - y1) != 2 and board[x1][y1] != 'KX' and board[x1][y1] != 'KO':
            return False


    return True

# funkcja odpowiedzialna za wykonanie ruchu
def make_move(ruch):
    pos, endpos = str_to_pos(ruch)
    y1, x1 = pos
    y2, x2 = endpos
    bicie = False
    typ_pionka = board[x1][y1]

    # Update the board with the new move
    board[x1][y1] = ' '
    board[x2][y2] = typ_pionka

    # Check if the piece has reached the opponent's side to become a king
    if typ_pionka == 'X' and x2 == 0:
        board[x2][y2] = 'KX'
    if typ_pionka == 'O' and x2 == 7:
        board[x2][y2] = 'KO'

    if abs(x2 - x1) > 1: #jeżeli bijemy pionek, to ruch idzie o dwa pola
        board[int((x1 + x2)/2)][int((y1 + y2)/2)] = ' '
        bicie = True

    return bicie

def pos_to_str(start, end):
    x1, y1 = start
    x2, y2 = end

    text = str(x1) + str(y1) + str(x2) + str(y2)
    return text

def str_to_pos(str):
    pos = list(str)
    pos = [eval(i) for i in pos]
    start = pos[0:2]
    end = pos[-2:]

    return start, end

def generate_move_list(player):
    lista_ruchów = {}
    #definiujemy, jakich damek lub pionków szukamy
    pionek = ''
    damka = ''
    kierunek = 1
    if player == 'X':
        pionek = 'X'
        damka = 'KX'
        kierunek = -1
    else:
        pionek = 'O'
        damka = 'KO'
    y_pos = 0
    for i in board:
        x_pos = 0
        for j in i:
            pos = [x_pos, y_pos]
            endpos_to_check = []
            if j == pionek:
                endpos_to_check = [[[x_pos - 1, y_pos + kierunek], False], [[x_pos + 1, y_pos + kierunek], False], #ruch lewo/prawo
                                   [[x_pos - 2, y_pos + kierunek * 2], True], [[x_pos + 2, y_pos + kierunek * 2], True]] #bicie lewo/prawo
            elif j == damka:
                endpos_to_check = [[[x_pos - 1, y_pos + 1], False], [[x_pos + 1, y_pos + 1], False],  # ruch lewo/prawo do przodu
                                   [[x_pos - 1, y_pos - 1], False], [[x_pos + 1, y_pos - 1], False],  # ruch lewo/prawo do tyłu
                                   [[x_pos - 2, y_pos + 2], True], [[x_pos + 2, y_pos + 2], True],   # bicie lewo/prawo do przodu
                                   [[x_pos - 2, y_pos - 2], True], [[x_pos + 2, y_pos - 2], True]]  # bicie lewo/prawo do tyłu
            # sprawdamy czy dane ruchy są możliwe
            for endposlist in endpos_to_check:
                endpos, bicie = endposlist
                if(is_valid_move(pos, endpos, player, bicie)):
                    lista_ruchów[pos_to_str(pos, endpos)] = 0
            x_pos += 1
        y_pos += 1
    return lista_ruchów


# funkcja do sprawdzania czy ktoś nie wygrał już
def check_win(player):
    # Check if the opponent has no pieces left
    for row in board:
        if player in row or f'K{player}' in row:
            return False
    return True

# Funkcja do zbierania informacji odnośnie ruchu gracza
def get_move(player):
    global Qtable_O, Qtable_X
    qtable = {}
    if(player == 'X'):
        qtable = Qtable_X
    else:
        qtable = Qtable_O

    if flatten_board(board) in qtable:
        lista_ruchow = qtable[flatten_board(board)]
        print(lista_ruchow)
        if not lista_ruchow:
            return 'lose'
        ruch = max(lista_ruchow, key=lista_ruchow.get)

        return ruch

    else:
        #dodajemy listę ruchów (z wagami zerowymi) do odpowiedniego Qtable
        if player == 'X':
            Qtable_X[flatten_board(board)] = generate_move_list(player)
            lista_ruchow = list(Qtable_X[flatten_board(board)])
            if not lista_ruchow:
                return 'lose'
            return lista_ruchow[0]
        else:
            Qtable_O[flatten_board(board)] = generate_move_list(player)
            lista_ruchow = list(Qtable_O[flatten_board(board)])
            if not lista_ruchow:
                return 'lose'
            return lista_ruchow[0]



# wiadomość w której będzie wysyłana informacja zwrotna do bota
def info_dla_bota(board, player, win = None):
    # nie wiem co ty ma być
    # zwracamy mu stan planszy, kogo jest teraz runda, czy ktoś wygrał
    return None

#sprawdza, kto prowadzi rozgrywkę
def check_winning():
    counter_O = 0
    counter_X = 0
    for i in board:
        for j in i:
            if j == 'X' or j == 'KX':
                counter_X += 1
            if j == 'O' or j == 'KO':
                counter_O += 1
    if counter_O > counter_X:
        return 'O'
    elif counter_O < counter_X:
        return 'X'
    else:
        return 'nobody'


def restart_match(winner, ruchy_X, ruchy_O):
    global nr_rozgrywki
    reset_board()
    print('%s wins!' % winner)
    print('Gra numer %s:' % nr_rozgrywki)
    nr_rozgrywki += 1
    global Qtable_O, Qtable_X
    """
    #pozbawiamy się duplikatów ruchów, żeby nie nagradzać powtarzających się ruchów wiele razy
    ruchy_X_no_dup = []
    for elem in ruchy_X:
        if elem not in ruchy_X_no_dup:
            ruchy_X_no_dup.append(elem)
    ruchy_O_no_dup = []
    for elem in ruchy_O:
        if elem not in ruchy_O_no_dup:
            ruchy_O_no_dup.append(elem)
    """
    if (winner == 'X'):
        """
        for i in ruchy_X_no_dup: #nagradzamy wszystkie wykonane ruchy o 2
            qt = Qtable_X[i[0]]
            qt[i[1]] += 1
            Qtable_X[i[0]] = qt
        """
        return 'O'
    else:
        """
        for i in ruchy_O_no_dup:  # nagradzamy wszystkie wykonane ruchy o 2
            qt = Qtable_O[i[0]]
            qt[i[1]] += 1
            Qtable_O[i[0]] = qt
        """
        return 'X'


# główna pętla gry
def play_checkers():
    global Qtable_O, Qtable_X, nr_rozgrywki
    ruchy_X = []
    ruchy_O = []
    turn = 0

    print_board()
    player = 'X'
    while True:
        if (nr_rozgrywki == 100):
            turn += 1
            visualize_game_board(board, turn, 1)
            create_gif_from_folder('jpg_from_checkers', 'output_gif.gif', duration=1)
        elif nr_rozgrywki > 100:
            return
        print_board()
        print(f"Teraz jest ruch gracza {player}")


        if check_win('O'):
            player = restart_match('O', ruchy_X, ruchy_O)
            ruchy_X = []
            ruchy_O = []
        if check_win('X'):
            player = restart_match('X', ruchy_X, ruchy_O)
            ruchy_X = []
            ruchy_O = []

        ruch = get_move(player)
        if ruch == 'lose': #jesli nie ma zadnych pozostalych ruchow
            if player == "X":
                player = restart_match('O', ruchy_X, ruchy_O)
            else:
                player = restart_match('X', ruchy_X, ruchy_O)
            continue


        #zapisujemy wykonane ruchy na przyszłość
        if player == 'X':
            ruchy_X.append([flatten_board(board), ruch])
        else:
            ruchy_O.append([flatten_board(board), ruch])

        boardkey = flatten_board(board) #zapisujemy stan planszy
        print(ruch)
        bicie = make_move(ruch) #make_move zwraca True, jesli w ruchu zostal zbity pionek
        print('nowa tura')
        if player == 'X':
            reward = -5
            if bicie:
                reward += 2 #nagradzamy bicie

                #karzemy poprzedni ruch przeciwnika
                move_to_penalize = ruchy_O[-1]
                qt_to_update = Qtable_O[move_to_penalize[0]]
                qt_to_update[move_to_penalize[1]] -= 10
                Qtable_O[move_to_penalize[0]] = qt_to_update
            if check_winning() == 'O':
                reward -= 4
            print(reward)
            table_moves = Qtable_X[boardkey]  # pobieramy słownik
            table_moves[ruch] += reward  # zmieniamy żądaną wartość
            Qtable_X[boardkey] = table_moves  # update'ujemy tablicę
        else:
            reward = -5
            if bicie:
                reward += 2

                # karzemy poprzedni ruch przeciwnika
                move_to_penalize = ruchy_X[-1]
                qt_to_update = Qtable_X[move_to_penalize[0]]
                qt_to_update[move_to_penalize[1]] -= 10
                Qtable_X[move_to_penalize[0]] = qt_to_update
            if check_winning() == 'X':
                reward -= 4

            table_moves = Qtable_O[boardkey]  # pobieramy słownik
            print(reward)
            table_moves[ruch] += reward  # zmieniamy żądaną wartość
            Qtable_O[boardkey] = table_moves  # update'ujemy tablicę

        if not bicie: #zmieniamy turę gracza
            player = 'O' if player == 'X' else 'X'




# Start the game
play_checkers()