#**********************************************************
# N-Puzzle using Pygame (N = 3)
# Created By: Huang ChenTing
# Contact: huang.chenting<AT>gmail.com
# Date: March 2022
#**********************************************************

import pygame
import random
import math
from enum import Enum
from enum import IntEnum
import os.path

# colours for drawing
c_red = (255, 0, 0)
c_green = (0, 255, 0)
c_blue = (0, 0, 255)
c_yellow = (255, 255, 0)
c_gray = (100, 100, 100)
c_darkblue = (0, 0, 150)
c_black = (0, 0, 0)
c_white = (255, 255, 255)

# for knowing which direction the tile should move
class MoveDirection(Enum):
    NO_MOVE = -1
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

# for fps purposes
clock = pygame.time.Clock()

# class Node used for graphs and A Star search
# kept as simple as possible
# heuristic used should be changeable
class Node:
    move_speed = 500

    def __init__(self, state, heuristic):
        self.state = state          # for eg [0,1,2,3,4,5,6,7,8]
        self.visited = False        # for A star search
        self.global_goal = math.inf
        self.local_goal = math.inf
        self.parent_node = None
        self.parent_move = None     # for the solution steps
        self.heuristic = heuristic

    # less than, for sorting <
    def __lt__(self, other):
        return self.global_goal < other.global_goal

    # as long as state is the same, node1 == node2
    def __eq__(self, other):
        if (other != None):
            return self.state == other.state
        return False






# NPuzzle class for playing the sliding puzzle game
class NPuzzle:
    def __init__(self, gs, ts, bs):
        self.grid_size = gs     # grid_size works for 2 and 3, 4 will take too long (need IDA*, A* not enough)
        self.tile_size = ts     # how big tiles should be on screen
        self.border = bs        # margin
        self.tile_len = gs * gs # includes the blank
        self.tiles = []         # most important part, shows arrangement of tiles
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.tiles.append(i * gs + j)
        self.tile_position = []
        for i in range(self.grid_size):
            y = i * self.tile_size + self.border * 2
            for j in range(self.grid_size):
                x = j * self.tile_size + self.border * 2
                self.tile_position.append((x,y))

        # fixed and tile_POSITION are for displaying purposes
        self.tile_POSITION = self.tile_position.copy()
        self.fixed_POSITION = self.tile_position.copy()

        # variables for A star and animation sliding
        self.solution = []
        self.animate_a_star = False
        self.animating = False
        self.current_frame = 0
        self.end_frame = 0
        self.moving = False

        # for drawing the tiles
        image_load = True
        self.rect = pygame.Rect(0,0, gs * (ts + bs) + bs, gs * (ts + bs) + bs)

        if os.path.isfile('image.jpg'):
            pic = pygame.image.load('image.jpg')
            pic = pygame.transform.smoothscale(pic, self.rect.size)
        else:
            image_load = False


        self.images = []

        font = pygame.font.Font('freesansbold.ttf', 50)

        for i in range(self.tile_len):
            x,y = self.tile_position[self.tiles[i]]
            if image_load == False:
                image = pygame.Surface((self.tile_size - self.border, self.tile_size - self.border))
                image.fill(c_green)
                text = font.render(str(self.tiles[i]), 2, c_black)
            else:
                image = pic.subsurface(x,y, ts - bs, ts - bs)
                text = font.render(str(self.tiles[i]), 2, c_white)

            w, h = text.get_size()
            image.blit(text, ((self.tile_size - w)/2, (self.tile_size - h)/2))
            self.images += [image]

    # for drawing tiles
    def draw(self, screen):
        for t in self.tiles:
            if t != 0:
                x, y = self.tile_position[t]
                screen.blit(self.images[t], (x, y))

    # update positions to POSITIONS (when animation stops)
    def update_tile_positions(self):
        count = 0
        for t in self.tiles:
            self.tile_position[t] = self.fixed_POSITION[count]
            self.tile_POSITION[t] = self.fixed_POSITION[count]
            count += 1

    # for shuffling tiles, have to check legal placements
    def shuffle_tiles(self):
        random.shuffle(self.tiles)
        self.update_tile_positions()
        while not self.check_legal_tiles():
            random.shuffle(self.tiles)
            self.update_tile_positions()

    # for checking legal placement of tiles
    def check_legal_tiles(self):
        solution = 0
        for i in range(self.tile_len):
            check = self.tiles[i]

            for j in range(self.tile_len):
                if j <= i:
                    continue
                if self.tiles[j] < check and self.tiles[j] != 0:
                    solution += 1

        return not (solution%2)


    # returns an array containing neighbouring tiles of the blank tile
    def find_neighbours_of_zero(self, state):
        # first, find position of zero
        zero_pos = -1
        for i in state:
            if state[i] == 0:
                zero_pos = i;

        grid_size = self.grid_size
        # ok establish zero_pos, depending on zero_pos, neighbors will be different

        neighbours = []
        # left neighbour is i - 1
        if (zero_pos - 1 < len(state) and (zero_pos - 1) % grid_size < (zero_pos) % grid_size ):
            neighbours.append(state[zero_pos - 1])
        # right neighbour is i + 1
        if (zero_pos + 1 < len(state) and (zero_pos + 1) % grid_size != 0):
            neighbours.append(state[zero_pos + 1])
        # top neighbor is i - grid_size
        if (zero_pos - grid_size >= 0):
            neighbours.append(state[zero_pos - grid_size])
        # bottom neighbour is i + grid_size
        if (zero_pos + grid_size < len(state)):
            neighbours.append(state[zero_pos + grid_size])

        return neighbours

    # always move to 0 position
    def move_tile(self, state, pos):
        moved_state = state.copy()
        grid_size = self.grid_size

        if pos == -1:
            return moved_state

        neighbours = self.find_neighbours_of_zero(moved_state)

        # now, if pos is in neighbours, then move is valid, otherwise move is invalid
        if pos not in neighbours:
            return moved_state

        # ok so here pos is possible
        # do the no animation switch
        # instantaneous, so only do this AFTER animation
        index_pos = moved_state.index(pos)
        index_zero = moved_state.index(0)

        moved_state[index_pos] = 0
        moved_state[index_zero] = pos

        return moved_state

    # updates position (where to draw) to move towards POSITION (where it should be)
    def update(self, dt):
        s = Node.move_speed*dt
        self.moving = False

        for t in self.tiles:
            x, y = self.tile_position[t]
            X, Y = self.tile_POSITION[t]

            dx, dy = X-x, Y-y

            x = X if abs(dx) < s else x+s if dx > 0 else x-s
            y = Y if abs(dy) < s else y+s if dy > 0 else y-s

            self.tile_position[t] = x, y

            if x != X or y != Y:
                self.moving = True

        # once not moving, update POSITION to position, since reached
        if not self.moving:
            self.tile_POSITION = self.tile_position.copy()

    # returns UP DOWN LEFT or RIGHT, determines how tile should move
    def determine_move_direction(self, tile):
        neighbours = self.find_neighbours_of_zero(self.tiles)

        if tile not in neighbours:
            return MoveDirection.NO_MOVE
        else:
            index_pos = self.tiles.index(tile)
            zero_pos = self.tiles.index(0)

            # either left or right
            if abs(index_pos - zero_pos) <= 1:
                if index_pos > zero_pos:
                    return MoveDirection.LEFT
                else:
                    return MoveDirection.RIGHT
            else:
                if zero_pos < index_pos:
                    return MoveDirection.UP
                else:
                    return MoveDirection.DOWN


    # for moving with arrow buttons, if cannot go UP, try DOWN
    # for smoother UX
    def try_to_move_in_dir(self, dir):
        zero_pos = -1
        for i in range(self.tile_len):
            if self.tiles[i] == 0:
                zero_pos = i;
                break
        grid_size = self.grid_size

        if dir == MoveDirection.UP:
            if zero_pos - grid_size >= 0:
                self.move_with_animation(self.tiles[zero_pos - self.grid_size])
            elif zero_pos + grid_size < self.tile_len:
                self.move_with_animation(self.tiles[zero_pos + self.grid_size])
        elif dir == MoveDirection.DOWN:
            if zero_pos + grid_size < self.tile_len:
                self.move_with_animation(self.tiles[zero_pos + self.grid_size])
            elif zero_pos - grid_size >= 0:
                self.move_with_animation(self.tiles[zero_pos - self.grid_size])

        elif dir == MoveDirection.LEFT:
            if (zero_pos - 1 < self.tile_len and (zero_pos - 1) % grid_size < (zero_pos) % grid_size ):
                self.move_with_animation(self.tiles[zero_pos - 1])
            elif (zero_pos + 1 < self.tile_len and (zero_pos + 1) % grid_size != 0):
                    self.move_with_animation(self.tiles[zero_pos + 1])
        elif dir == MoveDirection.RIGHT:
            if (zero_pos + 1 < self.tile_len and (zero_pos + 1) % grid_size != 0):
                self.move_with_animation(self.tiles[zero_pos + 1])
            elif (zero_pos - 1 < self.tile_len and (zero_pos - 1) % grid_size < (zero_pos) % grid_size ):
                self.move_with_animation(self.tiles[zero_pos - 1])

    # moving with animation, sliding, by updating POSITION
    def move_with_animation(self, t):
        X, Y = self.tile_POSITION[t]

        dir = self.determine_move_direction(t)

        if dir == MoveDirection.UP:
            self.tile_POSITION[t] = X, Y - self.tile_size
        elif dir == MoveDirection.DOWN:
            self.tile_POSITION[t] = X, Y + self.tile_size
        elif dir == MoveDirection.LEFT:
            self.tile_POSITION[t] = X - self.tile_size, Y
        elif dir == MoveDirection.RIGHT:
            self.tile_POSITION[t] = X + self.tile_size, Y

        self.tiles = self.move_tile(self.tiles, t)
        #print("tiles: " + str(self.tiles))

    # animate solution, when animating, user should not be able to interrupt with actions
    def animate_solution(self):
        if len(self.solution) == 0:
            self.animating = False
            return False

        self.end_frame = len(self.solution)

        # only can move when nothing else is moving
        if self.moving == False:
            self.move_with_animation(self.solution[self.current_frame])
            self.current_frame += 1
            if self.current_frame == self.end_frame:
                self.animating = False
                self.current_frame = 0



def main():

    # show UI, does not appear for 4x4 and above
    def show_ui(x,y):
        font_size = 25
        font = pygame.font.Font('freesansbold.ttf', font_size)

        instructions = []

        instructions.append("Use mouse or arrow buttons to move tile.")
        instructions.append("Press A for Solution. Press H for hints!")
        instructions.append("Mouse right-click to reshuffle tiles!")

        for i in range(len(instructions)):
            words = font.render(str(instructions[i]), True, (255, 255, 255))
            screen.blit(words, (x, y + i * font_size) )

    # set target state to be default [0,1,2,3,4 ....]
    def set_target_state():
        target_list = []
        for i in range(npuzzle.tile_len):
            target_list.append(i)
        return target_list

    # for heuristic
    def manhattan_distance(state, grid_size):

        accumulated_cost = 0
        curr_x = 0
        curr_y = 0
        fixed_x = 0
        fixed_y = 0

        for i in range(len(state)):
            curr_x = state[i] % grid_size

            if state[i] < grid_size:
                curr_y = 0
            elif state[i] >= grid_size * 2:
                curr_y = 2
            else:
                curr_y = 1

            fixed_x = i % grid_size
            if i < grid_size:
                fixed_y = 0
            elif i >= 2 * grid_size:
                fixed_y = 2
            else:
                fixed_y = 1

            accumulated_cost += abs(curr_x - fixed_x) + abs(curr_y - fixed_y)
            #print (str(i) + " accumulated_cost so far: " + str(accumulated_cost))

        return round(accumulated_cost)

    # should be able to change type of heuristic used via Node init function
    def heuristic(node):
        return node.heuristic

    # A* implementation
    def solve_astar():
        node_start = Node(npuzzle.tiles, manhattan_distance(npuzzle.tiles, npuzzle.grid_size))

        # assumed to be in order
        target_state = set_target_state()
        node_start.local_goal = 0
        node_start.global_goal = heuristic(node_start)

        list_not_tested = []
        list_not_tested.append(node_start)
        checked_state_list = []

        #print("start_state: " + str(node_start.state))
        while (len(list_not_tested) > 0):

            # sort by global goal
            list_not_tested.sort()

            while (len(list_not_tested) > 0 and list_not_tested[0].visited):
                list_not_tested.pop(0)

            # cannot move_tile
            if len(list_not_tested) == 0:
                break

            node_current = list_not_tested[0]
            node_current.visited = True
            checked_state_list.append(node_current.state);
            o_state = node_current.state

            if node_current.state == target_state:
                #print("path found")
                solution_list = []
                while(node_current.parent_node):
                    solution_list.insert(0, node_current.parent_move)
                    node_current = node_current.parent_node
                #print("solution is: " + str(solution_list))
                return solution_list

            #for nb in node
            neighbour_list = npuzzle.find_neighbours_of_zero(node_current.state)

            for nb in neighbour_list:
                o_state = node_current.state
                nb_state = npuzzle.move_tile(o_state, nb)
                #print("nb_state created: " + str(nb_state))

                nb_node = Node(nb_state, manhattan_distance(nb_state, npuzzle.grid_size))

                if nb_state in checked_state_list:
                    nb_node.visited = True
                else:
                    list_not_tested.append(nb_node)

                possibly_lower_goal = node_current.local_goal + 1

                if possibly_lower_goal < nb_node.local_goal:
                    nb_node.parent_node = node_current
                    nb_node.parent_move = nb
                    nb_node.local_goal = possibly_lower_goal
                    nb_node.global_goal = nb_node.local_goal + heuristic(nb_node)

        # should never happen with legal tile placement
        # if it happens, should output this as a form of error message
        print("path not found")
        return []
        #print("checked_state_list len : " + str(len(checked_state_list)))

    # handling of mouse and keyboard input in game loop
    def handle_input(npuzzle):
        # see mouse select which tile
        selected_x, selected_y = pygame.mouse.get_pos()

        selected_x = int(selected_x/npuzzle.tile_size)
        selected_y = int(selected_y/npuzzle.tile_size)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()

            if mouse_presses[0]:
                if selected_x >= 0 and selected_x < npuzzle.grid_size:
                    if selected_y >= 0 and selected_y < npuzzle.grid_size:
                        t_selected = selected_y * npuzzle.grid_size + selected_x

                        if not npuzzle.animating:
                            npuzzle.move_with_animation(npuzzle.tiles[t_selected])

            elif mouse_presses[2]:
                npuzzle.shuffle_tiles()

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                npuzzle.solution = solve_astar()
                npuzzle.animating = True
            if keys[pygame.K_h]:
                npuzzle.solution = solve_astar()

                if (len(npuzzle.solution) / 4 > 0):
                    limit = math.ceil(len(npuzzle.solution) / 4)
                    npuzzle.solution = npuzzle.solution[:limit]
                    #print("npuzzle solution limited: " + str(npuzzle.solution))

                npuzzle.animating = True

            if keys[pygame.K_UP]:
                npuzzle.try_to_move_in_dir(MoveDirection.DOWN)
            if keys[pygame.K_DOWN]:
                npuzzle.try_to_move_in_dir(MoveDirection.UP)
            if keys[pygame.K_LEFT]:
                npuzzle.try_to_move_in_dir(MoveDirection.RIGHT)
            if keys[pygame.K_RIGHT]:
                npuzzle.try_to_move_in_dir(MoveDirection.LEFT)

    # init for pygame
    pygame.init()

    # create screen
    screen = pygame.display.set_mode((640, 480))
    # title and icon
    pygame.display.set_caption("N-Puzzle using Pygame")
    font = pygame.font.Font('freesansbold.ttf', 10)

    # create N puzzle, only N=2 or N=3 practical for now
    npuzzle = NPuzzle(3, 100, 5)

    # shuffle at the start
    npuzzle.shuffle_tiles()
    #print("tiles: " + str(npuzzle.tiles))

    # game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            handle_input(npuzzle)

        if npuzzle.animating:
            npuzzle.animate_solution()

        npuzzle.update(1/60)

        screen.fill( ( 25, 25, 25) )
        npuzzle.draw(screen)

        show_ui(15, (npuzzle.grid_size+1) * (npuzzle.tile_size));
        pygame.display.update()
        clock.tick(60)



if __name__ == '__main__':
    main()
