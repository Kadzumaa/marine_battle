from random import randint


class Input:
    """Класс ввода данных и проверки"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Input({self.x}, {self.y})"


class BoardException(Exception):
    """Исключения при неккоретных действиях. Родительский класс"""
    pass


class BoardOutException(BoardException):
    """Виды исключений при неккоретных действиях"""

    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    """Построение кораблей"""
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Input(cur_x, cur_y))

        return ship_dots

    def shooten_ship(self, shot):
        return shot in self.dots


class Game_Board:
    """Построение игровой доски"""

    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for i in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Input(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("КОРАБЛЬ УНИЧТОЖЕН!!!")
                    return False
                else:
                    print("ПОПАДАНИЕ!!!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    """Шаблон запроса ввода данных"""
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Input(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def __init__(self, board, enemy):
        super().__init__(board, enemy)
        self.count = None

    def ask(self):
        while True:
            print()
            cords = input("ВВЕДИТЕ КООРДИНАТЫ ЧЕРЕЗ ПРОБЕЛ: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты! ")
                continue
            x, y = cords


            x, y = int(x), int(y)
            return Input(x - 1, y - 1)


class Game(Ship):
    """Запуск игры с построением кораблей на доске"""
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Game_Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Input(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print()
        print("ДОБРО ПОЖАЛОВАТЬ В ИГРУ")
        print("ВВЕДИТЕ КООРДИНАТЫ В СЛЕДУЮЩЕМ ФОРМАТЕ")
        print("X - КООРДИНАТА СТРОКИ")
        print("Y - КООРДИНАТА СТОЛБЦА")

    def loop(self):
        num = 0
        while True:
            print()
            print("ПОЛЬЗОВАТЕЛЬ: ")
            print(self.us.board)
            print()
            print()
            print("КОМПЬЮТЕР: ")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("ХОД ИГРОКА: ")
                repeat = self.us.move()
            else:
                print("ХОД ИИ: ")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("ИГРОК ВЫИГРАЛ")
                break

            if self.us.count == 7:
                print("-" * 20)
                print("ИИ ВЫИГРАЛ")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()






q = Game()
q.start()