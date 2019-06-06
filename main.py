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

bot_id_request = {'get_team_id_for': team_name}
client_socket = None

ourMap = [['X ' for i in range(100)] for j in range(100)]
midMap = 50
ourX = 50
ourY = 50


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
        data = '{:03x}'.format(len(json.dumps(bot_id_request))) + json.dumps(bot_id_request) + '\0'
        print data
        client_socket.send(data)
        response = client_socket.recv(buf)
        response = response[3:-1]
        response = json.loads(response)
        return response['bot_id']
    except:
        print 'Exception in get bot id'


def updateMap(map, movement):
    global ourX
    global ourY
    if (movement == -1):
        for i in range(5):
            for j in range(5):
                ourMap[midMap - 2 + j][midMap + 2 - i] = map[i][j]

    if (movement == 0):
        ourY = ourY + 1
        tempX = ourX - 2
        for i in range(5):
            ourMap[tempX + i][ourY+2] = map[0][i]

    if (movement == 1):
        ourY = ourY - 1
        tempX = ourX -2
        for i in range(5):
            ourMap[tempX+i][ourY-2] = map[4][i]

    if (movement == 3):
        ourX = ourX - 1
        tempY = ourY + 2
        for i in range(5):
            ourMap[ourX - 2][tempY - i] = map[i][0]

    if (movement == 4):
        ourX = ourX + 1
        tempY = ourY + 2
        for i in range(5):
            ourMap[ourX + 2][tempY - i] = map[i][4]

    currentMap = ""
    for i in range(20):
        for j in range(20):
            currentMap+= str(ourMap[40+j][60-i])
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


def main():
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
        response = client_socket.recv(buf)
        response = response[3:-1]
        response = json.loads(response)

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
