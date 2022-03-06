#**********************************************************
# A Star Pathfinding Algorithm using Pygame
# Created By: Huang ChenTing
# Contact: huang.chenting<AT>gmail.com
# Date: March 2022
#**********************************************************


import pygame
import random
import math


# global variables
map_width = 30
map_height = 25
node_size = 20
node_border = 5

# class Node used for graphs
class Node:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = y*map_width + x
        self.obstacle = False
        self.visited = False
        self.global_goal = math.inf
        self.local_goal = math.inf
        self.neighbours_list = []
        self.parent_node = None

    # less than, for sorting <
    def __lt__(self, other):
        return self.global_goal < other.global_goal


def main():

    # variables to help with UI
    dijkstra = False
    display_nodes = True
    display_numbers = False
    total_distance = 0

    # init for pygame'
    pygame.init()

    # create screen
    screen = pygame.display.set_mode((800, 600))

    # title and icon
    pygame.display.set_caption("Pathfinding using Pygame")
    font = pygame.font.Font('freesansbold.ttf', 10)

    # init nodes
    node_list = []

    # note that j and i are reversed here instead of the usual loop due to the way python instantiates nodelist
    for j in range(map_height):
        for i in range(map_width):
            node = Node(i,j)
            node_list.append(node)  # i and j flipped in this case to maintain j*map_width + i sequence

    # show numbers
    def show_num(x,y, num):
        score = font.render(str(num), True, (255, 255, 255))
        screen.blit(score, (x, y) )

    # display basic UI info
    def show_UI(x,y):
        if dijkstra:
            word = "Currently using Dijkstra's Algorithm"
        else:
            word = "Currently using A Star Algorithm"

        words = font.render(str(word), True, (255, 255, 255))
        screen.blit(words, (x, y) )

        distance_text = "Distance to target: " + str(round(total_distance, 2))
        dtext = font.render(str(distance_text), True, (255, 255, 255))
        screen.blit(dtext, (x, y + 20) )

    # reset node before each search
    def reset_nodes():
        for n in node_list:
            n.visited = False
            n.global_goal = math.inf
            n.local_goal = math.inf
            n.parent_node = None

    # calculate actual distance
    def calc_distance(a, b):
        dist_sqrt = (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y)
        return math.sqrt(dist_sqrt)
        
        
    # A Star solver
    def solve_astar():

        reset_nodes()
        total_distance = 0

        # SQUARED distance! not actual distance
        def distance(a, b):
            dist_sqrt = (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y)
            #return math.sqrt(dist_sqrt)
            return dist_sqrt

        # heuristic returns 1 if dijkstra (no heuristic)
        def heuristic(a, b):
            if dijkstra:
                return 1
            return distance(a, b)   # otherwise returns squared distance (overestimates)

        # set starting conditions
        node_current = node_start
        node_current.local_goal = 0
        node_current.global_goal = heuristic(node_start, node_end)

        list_not_tested = []
        list_not_tested.append(node_start)

        #print("start a star")

        # while not found end node yet
        while(len(list_not_tested) > 0 and node_current != node_end):

            # sort by global goal
            list_not_tested.sort()

            # if already visited, then just pop
            while(len(list_not_tested) > 0 and list_not_tested[0].visited):
                list_not_tested.pop(0)

            # if empty list, then break
            if len(list_not_tested) == 0:
                break

            # set node current to front
            node_current = list_not_tested[0]
            node_current.visited = True

            for nb in node_current.neighbours_list:
                # if not visited yet and not obstacle, add to list
                if nb.visited == False and nb.obstacle == False:
                    list_not_tested.append(nb)

                # calculate possible lower goal distance
                possibly_lower_goal = node_current.local_goal + distance(node_current, nb)

                # if possibly lower goal, means best path found *so far*, set as parent
                if possibly_lower_goal < nb.local_goal:
                    nb.parent_node = node_current
                    nb.local_goal = possibly_lower_goal
                    nb.global_goal = nb.local_goal + heuristic(nb, node_end)


        #print("end")


    # set neighbours
    for i in range(map_width):
        for j in range(map_height):
            current_pos = j * map_width + i
            
            if j > 0:
                north = (j - 1) * map_width + i
                node_list[current_pos].neighbours_list.append(node_list[north])
                
            if j < map_height - 1:
                south = (j + 1) * map_width + i
                node_list[current_pos].neighbours_list.append(node_list[south])
                
            if i > 0:
                east = j * map_width + i - 1
                node_list[current_pos].neighbours_list.append(node_list[east])
                
            if i < map_width - 1:
                west = j * map_width + i + 1
                node_list[current_pos].neighbours_list.append(node_list[west])
                
            # diagonal connections
            if j > 0 and i > 0:
                nw = (j - 1) * map_width + i - 1
                node_list[current_pos].neighbours_list.append(node_list[nw])
            if j < map_height - 1 and i > 0:
                sw = (j + 1) * map_width + i - 1
                node_list[current_pos].neighbours_list.append(node_list[sw])
            if j > 0 and i < map_width - 1:
                ne = (j - 1) * map_width + i + 1
                node_list[current_pos].neighbours_list.append(node_list[ne])
            if j < map_height - 1 and i < map_width - 1:
                se = (j + 1) * map_width + i + 1
                node_list[current_pos].neighbours_list.append(node_list[se])

    node_start = node_list[int(map_height/2) * map_width + 1]
    node_end = node_list[int(map_height/2) * map_width + map_width - 2]

    # colours for drawing
    c_red = (255, 0, 0)
    c_green = (0, 255, 0)
    c_blue = (0, 0, 255)
    c_yellow = (255, 255, 0)
    c_gray = (100, 100, 100)
    c_darkblue = (0, 0, 150)

    # game loop
    running = True
    while running:

        # see mouse select which node
        selected_node_x, selected_node_y = pygame.mouse.get_pos()

        selected_node_x = int(selected_node_x/node_size)
        selected_node_y = int(selected_node_y/node_size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # check which node selected
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    if selected_node_x >= 0 and selected_node_x < map_width:
                        if selected_node_y >= 0 and selected_node_y < map_height:
                            npos = selected_node_y * map_width + selected_node_x

                            #if shift_is_held, set start position
                            keys = pygame.key.get_pressed()
                            if keys[pygame.K_LSHIFT]:
                                node_start = node_list[npos]
                            # if ctrl held, set end position
                            elif keys[pygame.K_LCTRL]:
                                node_end = node_list[npos]
                            else: # toggle obstacle
                                if node_list[npos].id != node_end.id:
                                    node_list[npos].obstacle = not node_list[npos].obstacle
                    
                    # everytime there is a mouse press, auto solve
                    solve_astar()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_q]:
                    dijkstra = not dijkstra
                    solve_astar()
                if keys[pygame.K_a]:
                    display_nodes = not display_nodes
                if keys[pygame.K_z]:
                    display_numbers = not display_numbers

        # drawing
        # RGB, red green blue
        screen.fill( ( 0, 0, 0) )

        # draw lines connecting nodes
        # have to be two separate loops so wont overlap with nodes
        if display_nodes:
            for i in range(map_width):
                for j in range(map_height):
                    c_colour = c_blue

                    x = node_list[j * map_width + i].x
                    y = node_list[j * map_width + i].y

                    start_x = i * node_size + node_size / 2
                    start_y = j * node_size + node_size / 2

                    for nb in node_list[j * map_width + i].neighbours_list:
                        end_x = nb.x * node_size + node_size / 2
                        end_y = nb.y * node_size + node_size / 2
                        pygame.draw.line(screen, c_colour, (start_x, start_y), (end_x, end_y), 3)


        # draw nodes
        for i in range(map_width):
            for j in range(map_height):
                
                # change colour depending on what kind of node it is
                c_colour = c_blue

                if node_list[j * map_width + i].obstacle == True:
                    c_colour = c_gray
                    pygame.draw.rect(screen, c_colour, pygame.Rect(i*node_size + node_border, j*node_size + node_border, node_size-node_border, node_size-node_border))
                elif node_list[j * map_width + i].visited == True:
                    c_colour = c_darkblue
                else:
                    c_colour = c_blue

                if node_list[j * map_width + i] == node_start:
                    c_colour = c_green
                    pygame.draw.rect(screen, c_colour, pygame.Rect(i*node_size + node_border, j*node_size + node_border, node_size-node_border, node_size-node_border))

                if node_list[j * map_width + i] == node_end:
                    c_colour = c_red
                    pygame.draw.rect(screen, c_colour, pygame.Rect(i*node_size + node_border, j*node_size + node_border, node_size-node_border, node_size-node_border))

                # if there is a node_end, draw path back to starting node, if there is one
                if node_end != None:
                    total_distance = 0
                    trace_node = node_end
                    while trace_node.parent_node != None:
                        x = trace_node.x
                        y = trace_node.y

                        total_distance += calc_distance(trace_node, trace_node.parent_node)

                        start_x = x * node_size + node_size / 2
                        start_y = y * node_size + node_size / 2

                        end_x = trace_node.parent_node.x * node_size + node_size / 2
                        end_y = trace_node.parent_node.y * node_size + node_size / 2

                        pygame.draw.line(screen, c_yellow, (start_x, start_y), (end_x, end_y), 3)
                        trace_node = trace_node.parent_node


                if display_nodes:
                    pygame.draw.rect(screen, c_colour, pygame.Rect(i*node_size + node_border, j*node_size + node_border, node_size-node_border, node_size-node_border))

                if display_numbers:
                    show_num(i*node_size + node_border, j*node_size + node_border, node_list[j * map_width + i].id)

        show_UI(20,550)
        pygame.display.update()
        
if __name__ == '__main__':
    main()
