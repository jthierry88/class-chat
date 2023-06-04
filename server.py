import socket
import threading
import json

serverHost = '127.0.0.1'
serverPort = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((serverHost, serverPort))
server.listen()

clients = []
usernames = []
users = {}

# Send messages to all clients
def broadcast(message):
    for client in users.values():
        client.send(message)

# Proccess client messages
def processclientMessage(message):
    clientdata = json.loads(message)
    outgoingmessage = clientdata["from"].encode('utf-8') + \
            ": ".encode('utf-8') + \
            clientdata["message"].encode('utf-8')
    if clientdata["user"] == "all":
        broadcast(outgoingmessage)
    else:
        users[clientdata["user"]].send(
            outgoingmessage
        )
    
# Handle function
def handle(client, user):
    while True:
        try:
            # Broadcast messages
            message = client.recv(1024)
            processclientMessage(message)
        except Exception as e:
            # Delete and close down clients
            del users[user]
            client.close()
            broadcast('{} has left the chat!'.format(user).encode('utf-8'))
            #print(e)
            break
    
# Receive/Listen
def receive():
    while True:
        # Accept the connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Get and store username
        client.send('USER'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        users[username] = client

        # Print and show username
        print("Username is {}".format(username))
        broadcast("{} has joined the chat!".format(username).encode('utf-8'))
        #users = {}
        #users[username] = client
        client.send('Connected to server! \n'.encode('utf-8'))

        # Start thread for client
        thread = threading.Thread(target=handle, args=(client, username))
        thread.start()

print("Server is up and listening for incoming connections!")
receive()
