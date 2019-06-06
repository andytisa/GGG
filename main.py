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

ourMap = [['X' for i in range(100)] for j in range(100)]
midMap = 50
ourX = 50
ourY = 50
initialMapPassed = False
goingTop = True
XPositionOnWorldMap = 0
YPositionOnWorldMap = 0
DoubleSpeed = False

class Moves:
    up = 0
    down = 1
    left = 2
    right = 3


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


Priority = {
     'Name': '',
     'Priority': 1,
     'Status': '',
     'Position': (0, 0)
}
Priority_List = [{'Name': 'Battery', 'Priority': 0, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Switch1', 'Priority': 1, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Switch2', 'Priority': 2, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Switch3', 'Priority': 3, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Olympus', 'Priority': 4, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Shield', 'Priority': 5, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Laser', 'Priority': 6, 'Status': 'Unknown', 'Position': (-1, -1)},
                 {'Name': 'Life', 'Priority': 7, 'Status': 'Unknown', 'Position': (-1, -1)}]


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
    else:
        data = json.dumps({'act': act, 'bot_id': bot_id})
        
    data = '{:03x}'.format(len(data)) + data + '\0'
    client_socket.send(data)


def getIndexInPriorityList(element):
    if element == 'B':
        index = 0
    elif element == '1':
        index = 1
    elif element == '2':
        index = 2
    elif element == '3':
        index = 3
    elif element == 'Z':
        index = 4
    elif element == 'S':
        index = 5
    elif element == 'L':
        index = 6
    elif element == '+':
        index = 7
    else:
        index = -1
    return index

def updateMap(map, movement):
    global ourX
    global ourY
    global Priority_List
    if (movement == -1):
        for i in range(5):
            for j in range(5):
                ourMap[midMap - 2 + i][midMap - 2 + j] = map[i][j]
                index = getIndexInPriorityList(map[i][j])
                if index != -1:
                    Priority_List[index]['Status'] = 'Known'
                    Priority_List[index]['Position'] = (midMap - 2 + i, midMap - 2 + j)



    if (movement == Moves.up):
        for j in range(5):
            ourMap[ourX - 3][ourY - 2 + j] = map[0][j]
            index = getIndexInPriorityList(map[0][j])
            if index != -1:
                Priority_List[index]['Status'] = 'Known'
                Priority_List[index]['Position'] = (ourX - 3, ourY - 2 + j)

    if (movement == Moves.down):
        for j in range(5):
            ourMap[ourX + 3][ourY - 2 + j] = map[4][j]
            index = getIndexInPriorityList(map[4][j])
            if index != -1:
                Priority_List[index]['Status'] = 'Known'
                Priority_List[index]['Position'] = (ourX + 3, ourY - 2 + j)

    if (movement == Moves.left):
        for i in range(5):
            ourMap[ourX + 2 + i][ourY - 3] = map[i][0]
            index = getIndexInPriorityList(map[i][0])
            if index != -1:
                Priority_List[index]['Status'] = 'Known'
                Priority_List[index]['Position'] = (ourX + 2 + i, ourY - 3)

    if (movement == Moves.right):
        for i in range(5):
            ourMap[ourX - 2 + i][ourY + 3] = map[i][4]
            index = getIndexInPriorityList(map[i][4])
            if index != -1:
                Priority_List[index]['Status'] = 'Known'
                Priority_List[index]['Position'] = (ourX - 2 + i, ourY + 3)

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
            if maze[node_position[0]][node_position[1]] != ' ' and \
                maze[node_position[0]][node_position[1]] != '1' and \
                maze[node_position[0]][node_position[1]] != '2' and \
                maze[node_position[0]][node_position[1]] != '3' and \
                maze[node_position[0]][node_position[1]] != 'Z' and \
                maze[node_position[0]][node_position[1]] != 'L' and \
                maze[node_position[0]][node_position[1]] != 'B' and \
                maze[node_position[0]][node_position[1]] != 'S' and \
                maze[node_position[0]][node_position[1]] != '+' and \
                maze[node_position[0]][node_position[1]] != 0:
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


def choose_direction(x, y):
    if goingTop is True:
        if ourMap[x - 1][y] == ' ':
            return Moves.up
        if ourMap[x - 1][y] == 'b' or ourMap[x - 1][y] == 'p' or ourMap[x - 1][y] == 'R':
            if ourMap[x][y + 1] == ' ':
                return Moves.right
            elif ourMap[x][y - 1] == ' ':
                return Moves.left
            elif ourMap[x + 1][y] == ' ':
                return Moves.down
    else:
        return Moves.down


def choose_speed(x, y):
    if DoubleSpeed is True:
        return Speed.boosted
    else:
        return Speed.normal


def analyzeData(response):
    global initialMapPassed
    global goingTop
    global XPositionOnWorldMap
    global YPositionOnWorldMap
    global ourX
    global ourY
    if initialMapPassed is False:
        updateMap(response['gameBoard'], -1)
        initialMapPassed = True
        XPositionOnWorldMap = response['x']
        YPositionOnWorldMap = response['y']
        direction = choose_direction(ourX, ourY)
        speed = choose_speed(ourX, ourY)
        return direction, speed
    else:
        if response['x'] > XPositionOnWorldMap:
            print 'down'
            updateMap(response['gameBoard'], Moves.down)
            XPositionOnWorldMap = response['x']
            ourX = ourX + 1
        if response['x'] < XPositionOnWorldMap:
            print 'up'
            updateMap(response['gameBoard'], Moves.up)
            XPositionOnWorldMap = response['x']
            ourX = ourX - 1
        if response['y'] > YPositionOnWorldMap:
            print 'right'
            updateMap(response['gameBoard'], Moves.right)
            YPositionOnWorldMap = response['y']
            ourY = ourY + 1
        if response['y'] < YPositionOnWorldMap:
            print 'left'
            updateMap(response['gameBoard'], Moves.left)
            YPositionOnWorldMap = response['y']
            ourY = ourY - 1

        direction = choose_direction(ourX, ourY)
        speed = choose_speed(ourX, ourY)
        return direction, speed

def main():
    global bot_id

    create_connection()
    bot_id = get_bot_id()

    # maze = [[0, 0, 0, 0, 'p', 0, 0, 0, 0, 0],
    #         ['Z', '1', 0, 0, 'b', 0, 0, 0, 0, 0],
    #         [0, '2', '3', 0, 'b', 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 'b', 0, 0, 0, 0, 0],
    #         [0, 0, 0, 'L', 'b', 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 'b', 0, 0, 0, 0, 0],
    #         [0, 0, 0, 'b', 'b', 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 'b', 'S', 0, 0, 0, 0],
    #         [0, 0, 0, '+', 'b', 0, 'b', 0, 0, 0],
    #         [0, 0, 0, 0, 'B', 0, 0, 0, 0, 0]]
    #
    # start = (0, 0)
    # end = (7, 6)
    #
    # path = find_path(maze, start, end)
    # print(path)

    while True:
        response = get_data()
        move, speed = analyzeData(response)
        send_data(move, speed)

        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in ourMap]))
        print Priority_List



if __name__ == '__main__':
    main()
