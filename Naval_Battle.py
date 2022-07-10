from random import randint

#ОПРЕДЕЛЕНИЕ ТОЧКИ НА ПОЛЕ
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
        # сравнение координат

    def __repr__(self):
        return f"({self.x}, {self.y})"
        # описание координат

#ПРОВЕРКИ НА ОШИБКИ
class GameException(Exception):
    pass

class OutOfBorders(GameException):
    def __str__(self):
        return "Вы выстрелили за пределы игрового поля, попробуйте другую точку в рамках доски"

class Occupied(GameException):
    def __str__(self):
        return "Вы уже стреляли в эту точку, попробуйте другую"

class WrongShip(GameException):
    pass

#КОРАБЛИ И ИХ АТРИБУТЫ
class Ship:
    def __init__(self, head, length, direction):
        self.head = head #граница
        self.length = length #длина
        self.direction = direction #направление корабля
        self.lives = length

    #РАСПОЛОЖЕНИЕ КОРАБЛЕЙ
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.head.x 
            cur_y = self.head.y
            
            if self.direction == 0:
                cur_x += i
            
            elif self.direction == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def hit(self, shot):
        return shot in self.dots

#ОПРЕДЕЛЕНИЕ ДОСКИ
class Board:
    def __init__(self, hidden = False, size = 6):
        self.size = size #размер корабля
        self.hidden = hidden #видимость клетки
        self.count = 0 #кол-во
        self.field = [ ["O"]*size for _ in range(size) ] #сетка состояний
        self.busy = [] #занятость клетки
        self.ships = [] #список кораблей
    
    #ПРОСТАВЛЕНИЕ КОРАБЛЕЙ
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise WrongShip() #проверка на ошибки
        for d in ship.dots:
            self.field[d.x][d.y] = "■" #визуальное заполнение поля
            self.busy.append(d)
        
        self.ships.append(ship)
        self.around(ship)

    #АВТОМАТИЧЕСКАЯ БЛОКИРОВКА КЛЕТОК ВОКРУГ КОРАБЛЯ
    def around(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1), #
            (0, -1), (0, 0) , (0 , 1), # окружение
            (1, -1), (1, 0) , (1, 1) #
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    
    def __str__(self): #вызов доски
        show  = ""
        show += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field): # вывод строк
            show += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hidden: #функционал скрытых кораблей
            show = show.replace("■", "O")
        return show
    
    def out(self, d): #проверка координаты на корректность в доске
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d):  #цикл стрельбы с проверками на корректность
        if self.out(d):
            raise OutOfBorders()
        
        if d in self.busy:
            raise Occupied.exception()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.around(ship, verb = True)
                    print("Убил!")
                    return False
                else:
                    print("Ранил!")
                    return True
        
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    
    def begin(self):
        self.busy = [] #для простреленных точек

#КЛАССЫ ИГРОКОВ
class Player:
    def __init__(self, board, enemy):
        self.board = board #доска игрока
        self.enemy = enemy #доска противника

    def ask(self):
        raise NotImplementedError() #для наследуемости
    
    def move(self):
        while True:
            try:
                target = self.ask() #запрос координат
                repeat = self.enemy.shot(target)
                return repeat
            except GameException as e:
                print(e)

class AI(Player): #компьютер
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5)) #рандомизация хода компьютера
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player): #для пользователя
    def ask(self):
        while True:
            cords = input("Введите 2 координаты хода в пределах поля через пробел ").split()
            x, y = cords
            x, y = int(x), int(y)
            return Dot(x-1, y-1) #корректировка на вывод


#ИГРОВОЙ ЦИКЛ
class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.rambord()
        co = self.rambord()
        co.hidden = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    # генерация досок
    def rambord(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    #бесконечная генерация кораблей
    def random_place(self):
        lens = [ 3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShip:
                    pass
        board.begin()
        return board

    # Приветствие игрока
    def greetings(self):
        print("  Сегодня играем в  ");
        print("    Морской бой!    ");
        print();
        print(" Цель: поразить все ");
        print(" корабли противника ");
        print("      1х ■ ■ ■      ");
        print("      2х ■ ■        ");
        print("      3х ■          ");
        print()
        print(" Ввод:              ")
        print(" x - номер строки   ")
        print(" y - номер столбца  ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска игрока:")
            print(self.us.board)
            print("-"*20)
            print("Доска противника:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ваш ход")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит противника")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print("-"*20)
                print("Победа за вами!")
                break
            
            if self.us.board.count == 7:
                print("-"*20)
                print("Вы проиграли")
                break
            num += 1
            
    def start(self):
        self.greetings()
        self.loop()

g = Game()
g.start()