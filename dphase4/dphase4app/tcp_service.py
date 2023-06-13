import graphLibrary as gl

import socket
import threading
import argparse
import base64
import json
import io
import time

from PIL import Image
from cryptography.fernet import Fernet

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=1234)
args = parser.parse_args()

# Define the host and port
HOST = '127.0.0.1'
PORT = args.port

RECV_SIZE = 4096

# Create a TCP socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
sock.bind((HOST, PORT))
print("Port: " + str(PORT))
# Listen for incoming connections
sock.listen()

# Create a Fernet cipher object using a key (will be used to decrypt password)
key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg=' # Random key, but same on all clients and server
cipher_suite = Fernet(key)

current_graphs_of_users = {}
clients = []
availableTid = 0
client_threads = {}
client_list_lock = threading.Lock()

# Multi-instance support
graphs = {}
nextGraphId = 0
graphListLock = threading.Lock()
graphLocks = {}

# Client management
def add_client(client):
    with client_list_lock:
        clients.append(client)
def remove_client(client):
    with client_list_lock:
        clients.remove(client)
def print_clients():
    with client_list_lock:
        print("Current clients: ", end="")
        print(clients)

##### Commands

### Multi-instance commands
# newgraph                                                              { "action": "newgraph" }
# listgraphs                                                            { "action": "listgraphs" }
# open <graph_id>                                                       { "action": "open", "graph_id": 0 }
# close <graph_id>                                                      { "action": "close", "graph_id": 0 }

### Graph specific commands
# newnode <node_type>                                                   { "action": "newnode", "node_type": "GetString" }
# deletenode <node_id>                                                  { "action": "deletenode", "node_id": 0 }
# connect <node1_id> <node1_outport> <node2_id> <node2_inport>          { "action": "connect", "node1_id": 0, "node1_outport": 0, "node2_id": 1, "node2_inport": 0 }
# disconnect <node1_id> <node1_outport> <node2_id> <node2_inport>       { "action": "disconnect", "node1_id": 0, "node1_outport": 0, "node2_id": 1, "node2_inport": 0 }
# set <node_id>                                                         { "action": "set", "node_id": 0, "node_data": "Node will be here" }
# uploadimage <image_name> <image_size>                                 { "action": "uploadimage", "image_name": "ImageName.png" "image_size": 1024 }
# execute                                                               { "action": "execute" }

### Other commands
# adduser <username>                                                    { "action": "adduser", "username": "efe" }

def receive_command_send_result(sock, client_address, userid):
    global nextGraphId
    global graphs
    global graphLocks
    global graphListLock
    
    json_data = sock.recv(RECV_SIZE).decode()
    if json_data == "" or json_data == None:
        return
    cmd_dict = json.loads(json_data)

    if cmd_dict["action"] == "newgraph":
        print(f"Received \"newgraph\" command from {client_address}.")
        with graphListLock:
            graphs[nextGraphId] = gl.Graph("Graph of " + userid, gl.User(userid))
            graphLocks[nextGraphId] = threading.Lock()
            message = str(nextGraphId)
            sock.sendall(message.encode())
            nextGraphId += 1
    elif cmd_dict["action"] == "listgraphs":
        print("Received \"listgraphs\" command.")
        with graphListLock:
            graphIDs = { "list": list(graphs.keys()) }
            sock.sendall(json.dumps(graphIDs).encode())
    elif cmd_dict["action"] == "open":
        print(f"Received \"open\" command from {client_address} for graph " + str(cmd_dict["graph_id"]) + ".")
        if current_graphs_of_users[userid] == -1 and cmd_dict["graph_id"] in graphs.keys():
            print(f"{client_address} is waiting for the lock of graph " + str(cmd_dict["graph_id"]) + " to be available...")
            graphLocks[cmd_dict["graph_id"]].acquire()
            print(f"{client_address} acquired the lock of graph " + str(cmd_dict["graph_id"]) + ".")
            current_graphs_of_users[userid] = cmd_dict["graph_id"]
            graphDict = graphs[current_graphs_of_users[userid]].getDict()
            graphData = json.dumps(graphDict).encode()
            dataSize = len(graphData)
            dict_message = { "result": 1, "data_size": dataSize }
            j_data = json.dumps(dict_message)
            # Send result and data size to django
            sock.sendall(j_data.encode())
            # Receive "1" from django
            sock.recv(RECV_SIZE)
            # Send data to django
            sock.sendall(graphData)
        else:
            dict_message = { "result": 0, "data_size": 0 }
            j_data = json.dumps(dict_message)
            # Send result and data size to django
            sock.sendall(j_data.encode())
    elif cmd_dict["action"] == "close":
        print(f"Received \"close\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            graphLocks[cmd_dict["graph_id"]].release()
            current_graphs_of_users[userid] = -1
            message = "1"
            sock.sendall(message.encode())
        else:
            message = "0"
            sock.sendall(message.encode())
    elif cmd_dict["action"] == "newnode":
        print(f"Received \"newnode\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            node = graphs[current_graphs_of_users[userid]].newnode(cmd_dict["node_type"])
            message = str(node.id)
            sock.sendall(message.encode())
        else:
            j_data = json.dumps({ "node_id": -1 })
            sock.sendall(j_data.encode())
    elif cmd_dict["action"] == "updatenode":
        print(f"Received \"updatenode\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
         if current_graphs_of_users[userid] != -1:
            node = graphs[current_graphs_of_users[userid]].nodes[cmd_dict["node_id"]]
            node.position = cmd_dict["position"]
            j_data = json.dumps({"node_id":cmd_dict["node_id"], "position":node.position})
            sock.sendall(j_data.encode())
        else:
            message = "-1"
            sock.sendall(message.encode())
    elif cmd_dict["action"] == "deletenode":
        print(f"Received \"deletenode\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            graphs[current_graphs_of_users[userid]].deletenode(cmd_dict["node_id"])
            j_data = json.dumps({ "connections": graphs[current_graphs_of_users[userid]].connections })
            sock.sendall(j_data.encode())
        else:
            j_data = json.dumps({ "connections": -1 })
            sock.sendall(j_data.encode())

    elif cmd_dict["action"] == "connect":
        print(f"Received \"connect\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            graphs[current_graphs_of_users[userid]].connect(cmd_dict["node1_id"], cmd_dict["node1_outport"], cmd_dict["node2_id"], cmd_dict["node2_inport"])
            message = "1"
            sock.sendall(message.encode())
        else:
            message = "0"
            sock.sendall(message.encode())
    elif cmd_dict["action"] == "disconnect":
        print(f"Received \"disconnect\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            graphs[current_graphs_of_users[userid]].disconnect(cmd_dict["node1_id"], cmd_dict["node1_outport"], cmd_dict["node2_id"], cmd_dict["node2_inport"])
            message = "1"
            sock.sendall(message.encode())
        else:
            message = "0"
            sock.sendall(message.encode())
    elif cmd_dict["action"] == "set":
        print(f"Received \"set\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            node = graphs[current_graphs_of_users[userid]].nodes[cmd_dict["node_id"]]
            node.inportValues[0] = cmd_dict["value"]
            message = "1"
            sock.sendall(message.encode())
        else:
            message = "0"
            sock.sendall(message.encode())
    elif cmd_dict["action"] == "uploadimage":
        print(f"Received \"uploadimage\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        message = "1"
        sock.sendall(message.encode())
        dataSize = int(cmd_dict["image_size"])
        receivedSize = 0
        receivedData = b""
        while True:
            if receivedSize == dataSize:
                break
            received_data_part = sock.recv(RECV_SIZE)
            receivedSize += len(received_data_part)
            receivedData += received_data_part
        img_data = base64.b64decode(receivedData)
        img = Image.open(io.BytesIO(img_data))
        filename = cmd_dict["image_name"]
        image_path = './serverimages/' + filename
        img.save(image_path, 'PNG')
        sock.sendall(message.encode())
    elif cmd_dict["action"] == "execute":
        print(f"Received \"execute\" command from {client_address} for graph {current_graphs_of_users[userid]}.")
        if current_graphs_of_users[userid] != -1:
            executionResult = graphs[current_graphs_of_users[userid]].execute([])
            if executionResult == None:
                sock.sendall("0".encode())
                print("Nothing obtained from execution.")
                return
            print("Sending execution results to django...")
            # Send output count
            sock.sendall(str(len(executionResult)).encode())
            # Receive "1" from django
            sock.recv(RECV_SIZE)
            # Send all results one by one
            for elem in executionResult:
                # Send node id
                sock.sendall(str(elem[0]).encode())
                # Receive "1" from django
                sock.recv(RECV_SIZE)
                # Send outport value
                buffer = io.BytesIO()
                elem[1].save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                image_base64 = base64.b64encode(img_bytes)
                dataSize = len(image_base64)
                # Send image size
                sock.sendall(str(dataSize).encode())
                # Receive "1" from django
                sock.recv(RECV_SIZE)
                # Send image
                sock.sendall(image_base64)
                # Receive "1" from django
                sock.recv(RECV_SIZE)
            print("Sent all execution results to django.")
        else:
            message = "0"
            sock.sendall(message.encode())
    elif cmd_dict["action"] == "adduser":
        print(f"Received \"adduser\" command from {client_address}.")
        if cmd_dict["username"] not in list(current_graphs_of_users.keys()):
            current_graphs_of_users[cmd_dict["username"]] = -1
            message = "1"
            sock.sendall(message.encode())
        else:
            message = "0"
            sock.sendall(message.encode())

# Define a function to handle a client connection
def handle_client(client_socket, client_address, tid):
    print(f'Connected by {client_address}')
    print_clients()

    try:
        # Receive userid
        userid = client_socket.recv(RECV_SIZE).decode()
        # Send "1"
        client_socket.sendall("1".encode())
        # Receive command
        receive_command_send_result(client_socket, client_address, userid)
    except ConnectionResetError:
        print('Connection reset error occured.')
    except json.decoder.JSONDecodeError:
        print('JSON decode error occured.')
    finally:
        print(f'Client {client_address} closed connection.')
        client_socket.close()
        remove_client(client_address)
        client_threads[tid][1] = True

done = False

def thread_cleaner():
    global done
    while True:
        if done:
            break
        time.sleep(0.1)
        ctList = list(client_threads.values())
        i = 0
        while i < len(ctList):
            if ctList[i][1]:
                key = list(client_threads.keys())[i]
                client_threads[key][0].join()
                del client_threads[key]
            i += 1

def exit_input():
    global done
    while True:
        inp = input()
        if inp == "exit" or inp == "quit":
            done = True
            sock.close()
            return

ei = threading.Thread(target=exit_input, args=())
ei.start()

tc = threading.Thread(target=thread_cleaner, args=())
tc.start()

print("Waiting for connections...")

# Handle incoming connections in separate threads
while True:
    try:
        # Accept a new client connection
        conn, addr = sock.accept()
    except OSError:
        break

    # Check exit condition
    if done:
        break

    # Add address to client list
    add_client(addr)

    # Start a new thread to handle the connection
    t = threading.Thread(target=handle_client, args=(conn, addr, availableTid))
    client_threads[availableTid] = [t, False]
    availableTid += 1
    t.start()

ei.join()
tc.join()
