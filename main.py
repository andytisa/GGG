########################################################################################################################
#                                                   Imports                                                            #
########################################################################################################################
import json
import socket

########################################################################################################################
#                                                   Variables                                                          #
########################################################################################################################
team_name = 'Navodari'
host = 'localhost'
port = 31415
buf = 1024

client_socket = None
bot_id = None

ourMap = [['X ' for i in range(100)] for j in range(100)]
midMap = 50
ourX = 50
ourY = 50
initialMapPassed = False
goingTop = True
XPositionOnWorldMap = 0
YPositionOnWorldMap = 0

class Moves:
    up = 0
    down = 1
    left = 3
    right = 4


class Speed:
    normal = 1
    boosted = 2


class Actions:
    fire_up = 'Fire up'
    fire_down = 'Fire down'
    fire_left = 'Fire left'
    fire_right = 'Fire right'
    pick = 'Pick'
    turn_switch = 'Turn switch'


########################################################################################################################
#                                                   Procedures                                                         #
########################################################################################################################
def create_connection():
    """
    Creates a socket connection to the game server
    """
    global client_socket
    connected = False

    while not connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            connected = True
        except:
            pass


def get_bot_id():
    """
    Register bot with a bot id
    """
    try:
        data = json.dumps({'get_team_id_for': team_name})
        data = '{:03x}'.format(len(data)) + data + '\0'
        client_socket.send(data)

        return get_data()['bot_id']
    except:
        pass


def get_data():
    return json.loads(client_socket.recv(buf)[3:-1])


def send_data(move=None, speed=None, act=None):
    if move is not None:
        data = json.dumps({'move': move, 'speed': speed, 'bot_id': bot_id})
        data = '{:03x}'.format(len(data)) + data + '\0'
        client_socket.send(data)
    else:
        data = json.dumps({'act': act, 'bot_id': bot_id})
        data = '{:03x}'.format(len(data)) + data + '\0'
        client_socket.send(data)


def updateMap(map, movement):
    global ourX
    global ourY
    if (movement == -1):
        for i in range(5):
            for j in range(5):
                ourMap[midMap - 2 + i][midMap - 2 + j] = map[i][j]

    if (movement == Moves.up):
        ourX = ourX - 1
        tempY = ourY - 2
        for j in range(5):
            ourMap[ourX - 2][tempY + j] = map[0][j]

    if (movement == Moves.down):
        ourX = ourX + 1
        tempY = ourY - 2
        for j in range(5):
            ourMap[ourX + 2][tempY + j] = map[4][j]

    if (movement == Moves.left):
        ourY = ourY - 1
        tempX = ourX - 2
        for i in range(5):
            ourMap[tempX + i][ourY - 2] = map[i][0]

    if (movement == Moves.right):
        ourY = ourY + 1
        tempX = ourX - 2
        for i in range(5):
            ourMap[tempX + i][ourY + 2] = map[i][4]

    currentMap = ""
    for i in range(20):
        for j in range(20):
            currentMap += str(ourMap[40 + i][40 + j])
            currentMap += " "
        currentMap += '\n'
    return currentMap


class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def find_path(maze, start, end):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares, up, down, left, right

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (
                    len(maze[len(maze) - 1]) - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                    (child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)

def analyzeData(response):
    global initialMapPassed
    global goingTop
    global XPositionOnWorldMap
    global YPositionOnWorldMap
    if (initialMapPassed == False):
        print updateMap(response['gameBoard'], -1)
        initialMapPassed = True
        XPositionOnWorldMap = response['x']
        YPositionOnWorldMap = response['y']
        return Moves.up

    if response['x'] > XPositionOnWorldMap:
        updateMap(response['gameBoard'], Moves.right)
        XPositionOnWorldMap = response['x']
    if response['x'] < XPositionOnWorldMap:
        updateMap(response['gameBoard'], Moves.left)
        XPositionOnWorldMap = response['x']
    if response['y'] > XPositionOnWorldMap:
        updateMap(response['gameBoard'], Moves.up)
        YPositionOnWorldMap = response['y']
    if response['y'] < XPositionOnWorldMap:
        updateMap(response['gameBoard'], Moves.down)
        YPositionOnWorldMap = response['y']

    if goingTop == True:
        if ourMap[ourX][ourY-1] == ' ':
            return Moves.up
        if (ourMap[ourX][ourY-1] == 'b' or ourMap[ourX][ourY-1] == 'p' or ourMap[ourX][ourY+1] == 'X') and ourMap[ourX+1][ourY-1] == ' ':
            return Moves.right
        if (ourMap[ourX][ourY-1] == 'b' or ourMap[ourX][ourY-1] == 'p' or ourMap[ourX][ourY-1] == 'X') and ourMap[ourX-1][ourY-1] == ' ':
            return Moves.left
        if (ourMap[ourX+1][ourY-1] == 'b' or ourMap[ourX+1][ourY-1] == 'p' or ourMap[ourX+1][ourY-1] == 'X') and ourMap[ourX+2][ourY-1] == ' ':
            return Moves.right
        if (ourMap[ourX-1][ourY-1] == 'b' or ourMap[ourX-1][ourY-1] == 'p' or ourMap[ourX-1][ourY-1] == 'X') and ourMap[ourX-2][ourY-1] == ' ':
            return Moves.left
        for i in range(1,3):
            for j in range(5):
                if ourMap[ourX+j][ourY+i] == 'M':
                    goingTop = False
    if goingTop == False:
        return Moves.down

def main():
    global bot_id

    create_connection()
    bot_id = get_bot_id()

    maze = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    start = (0, 0)
    end = (7, 6)

    path = find_path(maze, start, end)
    print(path)

    while True:
        response = get_data()
        move = analyzeData(response)
        send_data(move, Speed.normal)

        # Example first map and movement
    # firstMap = [
    #                 [10, 20, 30, 40, 50],
    #                 [11, 12, 13, 14, 15],
    #                 [21, 22, 23, 24, 25],
    #                 [31, 32, 33, 34, 35],
    #                 [41, 42, 43, 44, 45]
    #                 ]
    # secondMap = [
    #                 [11, 12, 13, 14, 15],
    #                 [21, 22, 23, 24, 25],
    #                 [31, 32, 33, 34, 35],
    #                 [41, 42, 43, 44, 45],
    #                 [51, 52, 53, 54, 55]
    #                 ]
    # print updateMap(firstMap, -1)
    # print updateMap(secondMap, 1)


if __name__ == '__main__':
    main()
