from config import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH, FULLSCREEN, SCREEN_PART_WIDTH, PLAYER_SPEED
from math import sqrt
import arcade
import random

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
        self.score = random.randint(5, 15)
        self.width = self.score
        self.height = self.score
        self.screen_part = None  # with coords
        self.closest = None
        self.speed = PLAYER_SPEED
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        self._set_color(self.color)

    def on_update(self, delta_time):
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
        closest_distance = None
        for n in self.neighbours:
            distance = calculate_distance((self.center_x, self.center_y), (n.center_x, n.center_y))
            if self.closest == None or distance < closest_distance:
                self.closest = n
                closest_distance = distance
        
        if self.closest and self.closest.score > self.score:
            self.go_to((self.closest.center_x, self.closest.center_y), away=True)
        elif self.closest and self.closest.score < self.score:
            self.go_to((self.closest.center_x, self.closest.center_y))

        if self.center_x + self.change_x > self.parent_game.width or self.center_x + self.change_x < 0:
            return
        if self.center_y + self.change_y > self.parent_game.height or self.center_y + self.change_y < 0:
            return

        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

    def set_screen_part(self):
        x = int((self.center_x - 1) // SCREEN_PART_WIDTH)
        y = int((self.center_y - 1) // SCREEN_PART_WIDTH)
        if self.screen_part != [x, y]:
            if self.screen_part:
                self.parent_game.screen_parts[self.screen_part[1]][self.screen_part[0]].remove(self)
            self.parent_game.screen_parts[y][x].append(self)
            self.screen_part = [x, y]
    
    def go_to(self, pos, away=False):
        delta_x = abs(self.center_x - pos[0])
        delta_y = abs(self.center_y - pos[1])
        distance = calculate_distance((self.center_x, self.center_y), pos)

        num = self.speed / distance
        self.change_x = delta_x * num
        self.change_y = delta_y * num

        if away:
            self.change_x = self.change_x * -1
            self.change_y = self.change_y * -1


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=FULLSCREEN)
        self.setup()

    def setup(self):
        self.players = arcade.SpriteList()
        self.screen_parts = [[[] for i in range(self.width // SCREEN_PART_WIDTH)] for i in range(self.height // SCREEN_PART_WIDTH)]

        #for i in range(100):
        #    del i
        #    self.players.append(Player(self))

        p = Player(self)
        p2 = Player(self)
        p.center_x = 500
        p.center_y = 500
        p.score = 50
        p.width = p.score
        p.height = p.score
        p2.center_x = 460
        p2.center_y = 500

        self.players.append(p)
        self.players.append(p2)

    def on_update(self, delta_time):
        for player in self.players:
            player.on_update(delta_time)

    def on_draw(self):
        arcade.start_render()
        self.players.draw()

        for player in self.players:
            #arcade.draw_line(player.center_x, player.center_y, player.screen_part[0] * SCREEN_PART_WIDTH + 25, player.screen_part[1] * SCREEN_PART_WIDTH  + 25, player.color)
            #for neighbour in player.neighbours:
            #    arcade.draw_line(player.center_x, player.center_y, neighbour.center_x, neighbour.center_y, player.color)
            if player.closest:
                arcade.draw_line(player.center_x, player.center_y, player.closest.center_x, player.closest.center_y, player.color)
            else:
                arcade.draw_rectangle_outline(player.center_x, player.center_y, player.score + 10, player.score + 10, player.color)

        #for y in range(self.height // SCREEN_PART_WIDTH):
        #    for x in range(self.width // SCREEN_PART_WIDTH):
        #        arcade.draw_rectangle_outline(x * SCREEN_PART_WIDTH + SCREEN_PART_WIDTH / 2, y * SCREEN_PART_WIDTH + SCREEN_PART_WIDTH / 2, SCREEN_PART_WIDTH, SCREEN_PART_WIDTH, (255, 255, 255))

def main():
    global game
    game = Game()
    arcade.run()