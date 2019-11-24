from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.button import Button
import copy


class Minimax:
    def __init__(self, board):
        self.board = list()
        for i in range(len(board)):
            self.board.append(list())
            for j in range(len(board[i])):
                if isinstance(board[i][j], Square):
                    self.board[i].append(board[i][j].source)
                else:
                    self.board[i].append(board[i][j])
        self.next = list()
        self.value = 0


class Square(ButtonBehavior, Image):
    def __init__(self):
        Image.__init__(self)
        ButtonBehavior.__init__(self)
        self.source = "white.png"


class Board(GridLayout):
    def __init__(self):
        GridLayout.__init__(self)
        self.cols = 3
        self.add_widget(Label())
        self.add_widget(Label(text="Choose starting player", font_size="50sp"))
        self.add_widget(Label())
        x = Square()
        x.source = "x.png"
        o = Square()
        o.source = "o.png"
        x.bind(on_press=self.create_board)
        o.bind(on_press=self.create_board)
        self.add_widget(x)
        self.add_widget(Label())
        self.add_widget(o)
        self.board = list()
        self.tree = None
        self.original_tree = self.tree
        self.first_press = "x"
        self.reset = Button(text="Reset game")
        self.winner = Label(font_size="20sp", color=(1, 0, 0, 1))
        self.reset.bind(on_press=self.reset_game)

    def create_board(self, touch):
        self.clear_widgets()
        for i in range(self.cols):
            self.board.append(list())
            for j in range(self.cols):
                self.board[i].append(Square())
                self.board[i][j].bind(on_press=self.place)
                self.add_widget(self.board[i][j])
        self.add_widget(self.reset)
        self.add_widget(self.winner)
        if touch.source == "o.png":
            self.first_press = "o"
            self.tree = Minimax(self.board)
            self.original_tree = self.tree
            self.create_tree("o.png", self.tree)
            self.generate_response()

    # resets the board and tree
    def reset_game(self, touch):
        self.winner.text = ""
        for i in self.board:
            for j in i:
                j.source = "white.png"
        if self.first_press == "o":
            self.tree = self.original_tree
            self.generate_response()

    # returns whether there is a winner, a tie or if the game is still ongoing
    def check_winner(self, board):
        board = Minimax(board).board
        for i in board:
            if i.count("x.png") == len(i):
                return "X wins"
            elif i.count("o.png") == len(i):
                return "O wins"
        for i in range(len(board)):
            x_count = 0
            o_count = 0
            for j in range(len(board)):
                if board[j][i] == "x.png":
                    x_count += 1
                elif board[j][i] == "o.png":
                    o_count += 1
            if x_count == len(board):
                return "X wins"
            elif o_count == len(board):
                return "O wins"
        x_main = 0
        o_main = 0
        x_secondary = 0
        o_secondary = 0
        for i in range(len(board)):
            if board[i][i] == "x.png":
                x_main += 1
            elif board[i][i] == "o.png":
                o_main += 1
            if board[i][len(board) - 1 - i] == "x.png":
                x_secondary += 1
            elif board[i][len(board) - 1 - i] == "o.png":
                o_secondary += 1
        if x_main == len(board) or x_secondary == len(board):
            return "X wins"
        elif o_main == len(board) or o_secondary == len(board):
            return "O wins"
        for i in board:
            for j in i:
                if j == "white.png":
                    return "playing"
        return "Tie"

    # creates a tree of all possible board situations
    def create_tree(self, turn, current):
        winner = self.check_winner(current.board)
        if winner != "playing":
            if winner == "X wins":
                current.value = -1
            elif winner == "O wins":
                current.value = 1
            elif winner == "Tie":
                current.value = 0
        else:
            count = 0
            for i in range(self.cols):
                for j in range(self.cols):
                    if current.board[i][j] == "white.png":
                        current.board[i][j] = turn
                        current.next.append(Minimax(copy.deepcopy(current.board)))
                        if turn == "x.png":
                            self.create_tree("o.png", current.next[count])
                        else:
                            self.create_tree("x.png", current.next[count])
                        count += 1
                        current.board[i][j] = "white.png"
            first = True
            if turn == "x.png":
                for i in current.next:
                    if first:
                        current.value = i.value
                        first = False
                    elif current.value > i.value:
                        current.value = i.value
            else:
                for i in current.next:
                    if first:
                        current.value = i.value
                        first = False
                    elif current.value < i.value:
                        current.value = i.value

    # handles placement of the user's input, the computer's response and advancing the tree
    def place(self, touch):
        if touch.source == "white.png":
            touch.source = "x.png"
            if self.first_press == "x":
                self.tree = Minimax(self.board)
                self.create_tree("o.png", self.tree)
            for i in self.tree.next:
                if Minimax(self.board).board == i.board:
                    self.tree = i
                    break
            if len(self.tree.next) != 0:
                self.generate_response()
            check = self.check_winner(self.board)
            if check in ["X wins", "O wins", "Tie"]:
                self.winner.text = check

    def generate_response(self):
        first = True
        max_value = None
        for i in self.tree.next:
            if first:
                max_value = i
                first = False
            else:
                if i.value > max_value.value:
                    max_value = i
        self.tree = max_value
        done = False
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j].source != self.tree.board[i][j]:
                    done = True
                    self.board[i][j].source = self.tree.board[i][j]
                    break
            if done:
                break


class Game(App):
    def build(self):
        self.title = "Tic Tac Toe"
        return Board()


Game().run()
