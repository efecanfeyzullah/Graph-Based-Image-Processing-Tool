from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from dphase4app import graphLibrary as gl
from PIL import Image
import socket
import base64
import json
import io
import os
from cryptography.fernet import Fernet

# define the host and port
HOST = '127.0.0.1'
PORT = 1234

RECV_SIZE = 2 * 1024 * 1024

current_graphs_of_users = { "makcay": -1, "ecf": -1 }
graphs = {}

outputNumber = 0

# Commands

# Multi-instance commands
# newgraph                                                              { "action": "newgraph" }
# listgraphs                                                            { "action": "listgraphs" }
# open <graph_id>                                                       { "action": "open", "graph_id": 0, "present": 0 }
# close <graph_id>                                                      { "action": "close", "graph_id": 0 }

# Graph specific commands
# newnode <node_type>                                                   { "action": "newnode", "node_type": "GetString" }
# connect <node1_id> <node1_outport> <node2_id> <node2_inport>          { "action": "connect", "node1_id": 0, "node1_outport": 0, "node2_id": 1, "node2_inport": 0 }
# disconnect <node1_id> <node1_outport> <node2_id> <node2_inport>       { "action": "disconnect", "node1_id": 0, "node1_outport": 0, "node2_id": 1, "node2_inport": 0 }
# set <node_id> <value>                                                 { "action": "set", "node_id": 0, "value": "Value will be here", "node_data": "Node will be here" }
# execute                                                               { "action": "execute" }

def command_to_dict(cmd):
    if cmd[0] == "newgraph":
        return { "action": "newgraph" }
    elif cmd[0] == "listgraphs":
        return { "action": "listgraphs" }
    elif cmd[0] == "open":
        return { "action": "open", "graph_id": int(cmd[1]) }
    elif cmd[0] == "close":
        return { "action": "close", "graph_id": int(cmd[1]) }
    elif cmd[0] == "newnode":
        return { "action": "newnode", "node_type": cmd[1] }
    elif cmd[0] == "connect":
        return { "action": "connect", "node1_id": int(cmd[1]), "node1_outport": int(cmd[2]), "node2_id": int(cmd[3]), "node2_inport": int(cmd[4]) }
    elif cmd[0] == "disconnect":
        return { "action": "disconnect", "node1_id": int(cmd[1]), "node1_outport": int(cmd[2]), "node2_id": int(cmd[3]), "node2_inport": int(cmd[4]) }
    elif cmd[0] == "set":
        return { "action": "set", "node_id": int(cmd[1]), "value": cmd[2], "node_data": None }
    elif cmd[0] == "execute":
        return { "action": "execute" }


def send_command_receive_result(sock, com, username):
    global current_graphs_of_users
    global graphs
    global outputNumber

    commandstr = com
    command = commandstr.split(' ')
    command_dict = command_to_dict(command)

    response = None

    if command_dict["action"] == "newgraph":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        result = sock.recv(RECV_SIZE)
        if int(result.decode()) < 0:
            response = "Failed to create a graph."
            print("Failed to create a graph.")
        else:
            response = "Created a new graph with id: " + result.decode() + "."
            print("Created a new graph with id: " + result.decode() + ".")
            graphs[int(result.decode())] = gl.Graph("Local graph " + result.decode(), username)
    elif command_dict["action"] == "listgraphs":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        j_data = sock.recv(RECV_SIZE).decode()
        result_dict = json.loads(j_data)
        response = result_dict["list"]
        print(result_dict["list"])
    elif command_dict["action"] == "open":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        j_data = sock.recv(RECV_SIZE).decode()
        result_dict = json.loads(j_data)
        if result_dict["result"] == 1:
            current_graphs_of_users[username] = command_dict["graph_id"]
            if current_graphs_of_users[username] not in graphs.keys():
                graphs[current_graphs_of_users[username]] = gl.Graph("", username)
            graphs[current_graphs_of_users[username]].setWithDict(result_dict["graph"])
            graphs[current_graphs_of_users[username]].name = "Local graph " + str(current_graphs_of_users[username])
            response = "Opened graph " + str(command_dict["graph_id"]) + f". (Owner: {graphs[current_graphs_of_users[username]].user.name})"
            print("Opened graph " + str(command_dict["graph_id"]) + ".")
        else:
            response = "Failed to open graph " + str(command_dict["graph_id"]) + "."
            print("Failed to open graph " + str(command_dict["graph_id"]) + ".")
    elif command_dict["action"] == "close":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        result = sock.recv(RECV_SIZE)
        if int(result.decode()) == 1:
            current_graphs_of_users[username] = -1
            response = "Closed graph " + str(command_dict["graph_id"]) + "."
            print("Closed graph " + str(command_dict["graph_id"]) + ".")
        else:
            response = "Failed to close graph " + str(command_dict["graph_id"]) + "."
            print("Failed to close graph " + str(command_dict["graph_id"]) + ".")

    elif command_dict["action"] == "newnode":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        result = sock.recv(RECV_SIZE)
        if int(result.decode()) < 0:
            response = "Failed to create a node."
            print("Failed to create a node.")
        else:
            response = "Created a new node with id: " + result.decode() + "."
            print("Created a new node with id: " + result.decode() + ".")
            graphs[current_graphs_of_users[username]].newnode(command_dict["node_type"], int(result.decode()))
    elif command_dict["action"] == "connect":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        result = sock.recv(RECV_SIZE)
        if int(result.decode()) == 1:
            graphs[current_graphs_of_users[username]].connect(command_dict["node1_id"], command_dict["node1_outport"], command_dict["node2_id"], command_dict["node2_inport"])
            response = "Connected outport " + str(command_dict["node1_outport"]) + " of node " + str(command_dict["node1_id"]) + " to inport " + str(command_dict["node2_inport"]) + " of node " + str(command_dict["node2_id"]) + "."
            print("Connected outport " + str(command_dict["node1_outport"]) + " of node " + str(command_dict["node1_id"]) + " to inport " + str(command_dict["node2_inport"]) + " of node " + str(command_dict["node2_id"]) + ".")
        else:
            response = "Failed to connect."
            print("Failed to connect.")
    elif command_dict["action"] == "disconnect":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        result = sock.recv(RECV_SIZE)
        if int(result.decode()) == 1:
            graphs[current_graphs_of_users[username]].disconnect(command_dict["node1_id"], command_dict["node1_outport"], command_dict["node2_id"], command_dict["node2_inport"])
            response = "Disconnected outport " + str(command_dict["node1_outport"]) + " of node " + str(command_dict["node1_id"]) + " from inport " + str(command_dict["node2_inport"]) + " of node " + str(command_dict["node2_id"]) + "."
            print("Disconnected outport " + str(command_dict["node1_outport"]) + " of node " + str(command_dict["node1_id"]) + " from inport " + str(command_dict["node2_inport"]) + " of node " + str(command_dict["node2_id"]) + ".")
        else:
            response = "Failed to disconnect."
            print("Failed to disconnect.")
    elif command_dict["action"] == "set":
        node = graphs[current_graphs_of_users[username]].nodes[command_dict["node_id"]]
        if node.componenttype == "LoadImage":
            if os.path.exists("./static/" + command_dict["value"]):
                node.inportValues[0] = "./static/" + command_dict["value"]
            else:
                return "Failed to set image, file does not exist."
        else:
            node.inportValues[0] = command_dict["value"]
        exec_result = node.execute()[0]
        nodedata = { "value": exec_result }
        command_dict["node_data"] = nodedata
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        result = sock.recv(RECV_SIZE)
        if int(result.decode()) == 0:
            response = "Failed to set."
            print("Failed to set.")
    elif command_dict["action"] == "execute":
        json_data = json.dumps(command_dict)
        sock.sendall(json_data.encode())
        
        json_data = sock.recv(RECV_SIZE).decode()
        json_dict = json.loads(json_data)
        img_str = json_dict["image"]
        if img_str != None:
            img_data = base64.b64decode(img_str)
            img = Image.open(io.BytesIO(img_data))
            filename = 'output' + str(outputNumber) + '.png'
            outputNumber += 1
            image_path = './static/' + filename
            img.save(image_path, 'PNG')
        
            response = {'message':"Received the final image from server. Image saved to " + image_path + ".", 'image_path': image_path}
            print("Received the final image from server.")
            print("Image saved to " + image_path + ".")
        else:
            response = {'message':"Failed to receive the final image from server. Validation failed.", 'image_path': None}
            print("Failed to receive the final image from server. Validation failed.")

    return response

# Create a Fernet cipher object using a key
key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg=' # Random key, but same on all clients and server
cipher_suite = Fernet(key)


# Create your views here.

# 127.0.0.1:8000
def viewindex(request):
    exists = User.objects.filter(username="makcay").exists()
    if not exists:
        user = User.objects.create_user(username="makcay", password="1234")
    exists = User.objects.filter(username="ecf").exists()
    if not exists:
        user = User.objects.create_user(username="ecf", password="1231")

    print("Registered usernames:")
    for u in User.objects.all():
        print(str(u.username))

    # Go to 127.0.0.1:8000/login/
    return HttpResponseRedirect('/login/')

# 127.0.0.1:8000/login/
def viewlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Go to 127.0.0.1:8000/sendcommand/
            return HttpResponseRedirect('/sendcommand/')
        else:
            # Handle invalid credentials
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')
   

# 127.0.0.1:8000/sendcommand/
def viewsendcommand(request):
    context = {}

    username = request.user.username

    # Get uploaded image
    if 'uploadedimage' in request.FILES:
        if not request.user.is_authenticated:
            return render(request, 'sendcommand.html', { "serverresponse": "Please login before uploading an image." })
        image_file = request.FILES['uploadedimage']
        image = Image.open(image_file)
        image.save("./static/" + image_file.name, 'PNG')

    # Get command
    command = request.POST.get('command')
    if command != None and command != '':
        print(f'Received command from \"{username}\" -> {command}')

        if not request.user.is_authenticated:
            return render(request, 'sendcommand.html', { "serverresponse": "Please login before sending commands." })

        # Create a TCP socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        sock.connect((HOST, PORT))

        serverResponse = None
        try:
            # Send user id to server
            sock.sendall(username.encode())
            # Recieve "1" from server
            sock.recv(RECV_SIZE)
            # Send the command to server
            serverResponse = send_command_receive_result(sock, command, username)
        except ConnectionResetError:
            print("Server closed connection.")
        finally:
            # Close the socket
            sock.close()

        if command == 'execute':
            if serverResponse["image_path"] == None:
                if "resultimage" in context:
                    del context["resultimage"]
                context["image_path"] = ""
            else:
                context["resultimage"] = "true"
                context["image_path"] = serverResponse["image_path"][1:]
            context["serverresponse"] = f'Server response: {serverResponse["message"]}'
        elif serverResponse != None:
            context["serverresponse"] = f'Server response: {serverResponse}'

    # Render sendcommand.html
    response = render(request, 'sendcommand.html', context)
    return response