import random

class Dot:
    _x = None
    _y = None
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

    @property
    def okrestnost(self):
        pole = [Dot(i, j) for i in range(6) for j in range(6)]
        okrestnost_ = [Dot(self.x - 1, self.y - 1), Dot(self.x, self.y - 1), Dot(self.x + 1, self.y - 1),
                       Dot(self.x - 1, self.y), Dot(self.x + 1, self.y),
                       Dot(self.x -1, self.y + 1), Dot(self.x, self.y + 1), Dot(self.x + 1, self.y + 1)]
        intersection = [element for element in pole if element in okrestnost_]
        return intersection

class Ship:
    def __init__(self, len, nos, napravlenie):
        self.len = len
        self.nos = nos
        self.napravlenie = napravlenie
        self.life = len

    @property
    def dots(self):
        dots_ = []
        x_sh = self.nos.x
        y_sh = self.nos.y
        for i in range(self.len):
            if self.napravlenie == '|':
                dots_.append(Dot(x_sh + i, y_sh))
                i += 1
            elif self.napravlenie == '-':
                dots_.append(Dot(x_sh, y_sh + i))
                i += 1
        return dots_

class BoardBusyException(BaseException):
    def __str__(self):
        return "Field is occupied"

class BoardOutException(BaseException):
    def __str__(self):
        return "Ship out of field"

class BoardShotOutException(BaseException):
    def __str__(self):
        return "Shot out of field"

class BoardShotRepeatException(BaseException):
    def __str__(self):
        return "You already shot there or shot near sunk ship"

class Board:
    def __init__(self, ownership = 'player'):
        self.ownership = ownership

        self.field = [['o'] * 6 for _ in range(6)]
        self.size = 6
        self.busy = []
        self.ships = []
        self.count = 0

    def __str__(self):
        num = '    0   1   2   3   4   5'
        vyvod = num
        for i, row in enumerate(self.field):
            vyvod += f"\n{i} | " + " | ".join(row) + " |"
        if self.ownership != 'player':
            vyvod = vyvod.replace("■", "o")
        return vyvod

    def contour(self, ship):
        kontur_ = []
        for sh in ship.dots:
            for tochka in sh.okrestnost:
                if tochka not in kontur_:
                    kontur_.append(tochka)
                else:
                    pass
        vychetanie = [element for element in kontur_ if element not in ship.dots]
        return vychetanie

    def add_ship(self, ship):
        for sh in ship.dots:
            if sh in self.busy:
                raise BoardBusyException
        for sh in ship.dots:
            if sh.x not in [0, 1, 2, 3, 4, 5] or sh.y not in [0, 1, 2, 3, 4, 5]:
                raise BoardOutException
        for sh in ship.dots:
            self.field[sh.x][sh.y] = "■"
            self.busy.append(sh)
        for co in self.contour(ship):
            self.busy.append(co)
        self.ships.append(ship)

    def shoot(self, shot):
        if shot.x not in range(6) or shot.y not in range(6):
            raise BoardShotOutException()
        elif self.field[shot.x][shot.y] == '.' or self.field[shot.x][shot.y] == 'X':
            raise BoardShotRepeatException
        elif self.field[shot.x][shot.y] == 'o':
            self.field[shot.x][shot.y] = '.'
            print("Missed!")
            return False
        else:
            for ship in self.ships:
                if shot in ship.dots:
                    self.field[shot.x][shot.y] = 'X'
                    ship.life -= 1
                    if ship.life == 0:
                        self.count += 1
                        for dd in self.contour(ship):
                            self.field[dd.x][dd.y] = "."
                        print("Ship destroyed!")
                        return True
                    else:
                        print("Ship damaged!")
                        return True
    def begin(self):
        self.busy = []

class Player:

    def __init__(self, own_board, enemy_board):
        self.own_board = own_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                hit = self.ask()
                result = self.enemy_board.shoot(hit)
                return result
            except BoardShotRepeatException as e:
                print(e)

class AI(Player):

    def ask(self):
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Computer's shot: {d.x} {d.y}")
        return d

class Human(Player):

    def ask(self):
        while True:
            x = input("Input row from 0 to 5")
            y = input("Input column from 0 to 5")

            if not(x.isdigit()) or not(y.isdigit()):
                print(" Input integer numbers! ")
                continue

            if int(x) < 0 or int(x) > 5 or int(y) < 0 or int(y)> 5:
                print(" Input numbers from 0 to 5! ")
                continue

            return Dot(int(x), int(y))

class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        ai_board = self.random_board()
        ai_board.ownership = 'ai'

        self.ai = AI(ai_board, player_board)
        self.pl = Human(player_board, ai_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                seq = ['|', '-']
                ship = Ship(l, Dot(random.randint(0, 5), random.randint(0, 5)), random.choice(seq))
                try:
                    board.add_ship(ship)
                    break
                except BoardBusyException as e:
                    pass
                except BoardOutException as e:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  The Game Begins  ")
        print("-------------------")
        print(" Input format - x y ")
        print("   x - row number  ")
        print("  y - column number ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Player's board:")
            print(self.pl.own_board)
            print("-" * 20)
            print("Computer's board:")
            print(self.ai.own_board)
            if num % 2 == 0:
                print("-" * 20)
                print("Human's turn!")
                repeat = self.pl.move()
            else:
                print("-" * 20)
                print("Computer's turn!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.own_board.count == 7:
                print("-" * 20)
                print("Human won!")
                break

            if self.pl.own_board.count == 7:
                print("-" * 20)
                print("Computer won!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

