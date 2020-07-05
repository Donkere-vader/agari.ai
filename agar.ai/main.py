from config import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH, FULLSCREEN, SCREEN_PART_WIDTH, PLAYER_START_SCORE, PLAYER_START_SPEED, PLAYERS, MAX_SCORE, MULTI_FAC, UPDATE_TICKS
from math import sqrt
import arcade
import random
import datetime

def calculate_distance(pos_1: tuple, pos_2: tuple):
    delta_x = abs(pos_1[0] - pos_2[0])
    delta_y = abs(pos_1[1] - pos_2[1])
    return sqrt(delta_x**2 + delta_y**2)

class Player(arcade.Sprite):
    def __init__(self, parent_game):
        super().__init__(filename='sprites/player_sprite.PNG')

        self.parent_game = parent_game
        self.center_x = random.randint(0, self.parent_game.width)
        self.center_y = random.randint(0, self.parent_game.height)
        self.score = random.randint(PLAYER_START_SCORE[0], PLAYER_START_SCORE[1])
        self.width = self.score
        self.height = self.score
        self.screen_part = None  # with coords
        self.closest = None
        self.speed = random.randint(PLAYER_START_SPEED[0], PLAYER_START_SPEED[1])
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.ticks = random.randint(0, UPDATE_TICKS)
        
        self._set_color(self.color)
        self.random_go_to()

    def on_update(self, delta_time):
        self.ticks += 1
        if self.ticks % UPDATE_TICKS == 0:
            

            self.set_screen_part()
            self.neighbours = []
            for y in [1, -1, 0]:
                for x in [1, -1, 0]:
                    if self.screen_part[0] + x < 0 or self.screen_part[0] + x > len(self.parent_game.screen_parts) - 1:
                        continue
                    if self.screen_part[1] + y < 0 or self.screen_part[1] + y > len(self.parent_game.screen_parts[0]) - 1:
                        continue
                    self.neighbours += self.parent_game.screen_parts[self.screen_part[1] + y][self.screen_part[0] + x]
            try:
                self.neighbours.remove(self)
            except ValueError:
                pass

            self.closest = None
            self.closest_distance = None
            for n in self.neighbours:
                distance = calculate_distance((self.center_x, self.center_y), (n.center_x, n.center_y))
                if self.closest == None or distance < self.closest_distance:
                    self.closest = n
                    self.closest_distance = distance
            
        if self.closest and self.closest_distance + self.closest.score < self.score:
            self.closest.die()
            self.new_score(increment=self.closest.score * MULTI_FAC)
            self.closest = None


        if self.closest and self.closest.score > self.score:
            self.go_to((self.closest.center_x, self.closest.center_y), away=True)
        elif self.closest and self.closest.score < self.score:
            self.go_to((self.closest.center_x, self.closest.center_y))

        if self.center_x + self.change_x > self.parent_game.width or self.center_x + self.change_x < 0:
            self.change_x = self.change_x * -1
        if self.center_y + self.change_y > self.parent_game.height or self.center_y + self.change_y < 0:
            self.change_y = self.change_y * -1

        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if self.score > MAX_SCORE:
            p = Player(self.parent_game)
            p2 = Player(self.parent_game)
            p.new_score(set=self.score // 2)
            p2.new_score(set=self.score // 2)
            p.center_x = self.center_x
            p.center_y = self.center_y
            p2.center_x = self.center_x
            p2.center_y = self.center_y
            self.parent_game.players.append(p)
            self.parent_game.players.append(p2)
            self.die()

    def set_screen_part(self):
        x = int((self.center_x - 1) // SCREEN_PART_WIDTH)
        y = int((self.center_y - 1) // SCREEN_PART_WIDTH)
        if self.screen_part != [x, y]:
            if self.screen_part:
                self.parent_game.screen_parts[self.screen_part[1]][self.screen_part[0]].remove(self)
            self.parent_game.screen_parts[y][x].append(self)
            self.screen_part = [x, y]
    
    def go_to(self, pos, away=False):
        #print(f'{self} Going to: {pos}')
        delta_x = self.center_x - pos[0]
        delta_y = self.center_y - pos[1]
        distance = calculate_distance((self.center_x, self.center_y), pos)

        try:
            num = self.speed / distance
        except ZeroDivisionError:
            return
        self.change_x = delta_x * num
        self.change_y = delta_y * num

        if not away:
            self.change_x = self.change_x * -1
            self.change_y = self.change_y * -1
    
    def random_go_to(self):
        self.go_to((random.randint(-self.parent_game.width, self.parent_game.width), random.randint(-self.parent_game.height, self.parent_game.height)))

    def new_score(self, increment=0, set=None):
        if set != None:
            self.score = set
        self.score += increment
        self.width = self.score
        self.height = self.score

    def die(self):
        self.parent_game.players.remove(self)
        if self.screen_part:
            self.parent_game.screen_parts[self.screen_part[1]][self.screen_part[0]].remove(self)

    def __repr__(self):
        return f"<Player @ ({self.center_x}, {self.center_y})>"

class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=FULLSCREEN)
        self.setup()

    def setup(self):
        self.ticks = 0
        self.start_time = datetime.datetime.now()
        self.players = arcade.SpriteList()
        self.screen_parts = [[[] for i in range(self.width // SCREEN_PART_WIDTH)] for i in range(self.height // SCREEN_PART_WIDTH)]

        for i in range(PLAYERS):
            del i
            self.players.append(Player(self))

        #p = Player(self)
        #p2 = Player(self)
        #p.center_x = 500
        #p.center_y = 400
        #p.height = p.score
        #p2.center_x = 500
        #p2.center_y = 600
        #p.go_to((500, 500))
        #p2.go_to((500, 500))

        #self.players.append(p)
        #self.players.append(p2)

    def on_update(self, delta_time):
        self.ticks += 1
        try:
            print(f"AVG FPS: {self.ticks // (datetime.datetime.now() -self.start_time).seconds}")
        except ZeroDivisionError:
            print(f"AVG FPS: ?")
        self.players.on_update(delta_time=delta_time)

    def on_draw(self):
        arcade.start_render()
        self.players.draw()

        #for player in self.players:
            #arcade.draw_line(player.center_x, player.center_y, player.screen_part[0] * SCREEN_PART_WIDTH + 25, player.screen_part[1] * SCREEN_PART_WIDTH  + 25, player.color)
            #for neighbour in player.neighbours:
            #    arcade.draw_line(player.center_x, player.center_y, neighbour.center_x, neighbour.center_y, player.color)
            #if player.closest:
            #    arcade.draw_line(player.center_x, player.center_y, player.closest.center_x, player.closest.center_y, player.color)
            #else:
            #    arcade.draw_rectangle_outline(player.center_x, player.center_y, player.score + 10, player.score + 10, player.color)

        #for y in range(self.height // SCREEN_PART_WIDTH):
        #    for x in range(self.width // SCREEN_PART_WIDTH):
        #        arcade.draw_rectangle_outline(x * SCREEN_PART_WIDTH + SCREEN_PART_WIDTH / 2, y * SCREEN_PART_WIDTH + SCREEN_PART_WIDTH / 2, SCREEN_PART_WIDTH, SCREEN_PART_WIDTH, (255, 255, 255))

def main():
    global game
    game = Game()
    arcade.run()