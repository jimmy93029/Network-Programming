import socket
import random  
import subprocess


def connect_with_udp(tcp_port, hostname):

    invite_message = "INVITE_Game, from hywu"
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    portA = int(input("Which port do you want on server A (port > 10000) (avoid available ports)"))
    Address_A = ('0.0.0.0', portA)
    udp_socket.bind(Address_A)

    while True:
        # Step 1: send the game invitation
        portB = int(input("choose one port that you want to send to (include avaiable ports)"))
        udp_socket.sendto(invite_message.encode(), (hostname, portB))
        print(f"Waiting for Player B {portB}'s response...")

        # Step 2: Wait for Player B's response on the same UDP port
        data, client_address = udp_socket.recvfrom(4096)
        response_message = data.decode()
        if response_message.lower() in ['yes', 'y']:
            print(f"Received response from {client_address}: {response_message}")
            break;
    
    # Step 3: Send back Player A's TCP port to Player B for establishing the game connection
    tcp_info_message = f"{tcp_port}"
    udp_socket.sendto(tcp_info_message.encode(), client_address)
    print(f"Sent TCP port info to Player B: {tcp_port}")

    udp_socket.close()


def connect_with_tcp(tcp_port, hostname):

    # Step1: create tcp socket and listening 
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((hostname, tcp_port))

    tcp_socket.listen(1) 
    print(f"Waiting for Player B to join the game via TCP on port {tcp_port}...")

    # Step 2: Accept the incoming TCP connection from Player B
    connection, client_address = tcp_socket.accept()  # Wait for Player B's connection
    print(f"TCP connection established with {client_address}")

    # Step 3: Start gaming
    sendA = gameA(start=True)
    connection.sendall(sendA.encode())  # Send initial move
    ThrowA = sendA.split()[1]

    while True:
        responseB = connection.recv(1024).decode()  # Decode response
        sendA = gameA(ThrowA, responseB)
        connection.sendall(sendA.encode())

        if sendA.split()[0] == "Over":
            break

        # Update ThrowA after each turn
        ThrowA = sendA.split()[1]

    connection.close()


def search_ports(hostname):

    host_ip = socket.gethostbyname(hostname)

    # do 'ss' command to find available ports
    result = subprocess.run(['ss', '-u', '-l'], capture_output=True, text=True)

    ports = [
        int(part.split(':')[-1])
        for line in result.stdout.splitlines() if host_ip in line
        for part in line.split() if ':' in part and host_ip in part
    ]

    print(f"Available ports: {ports}")
    return ports


def gameA(ThrowA="", dataB="", start=False):
    options = ["paper", "scissor", "stone", "paper"]

    if start:
        choose = input("Please choose paper, scissor or stone : ")
        message = f"A {choose}"
        print(message)
        return message

    ThrowB = dataB.split()[1]
    indexB = options.index(ThrowB)

    if ThrowA == options[indexB + 1]:
        print("-------------Game over: A_win-------------")
        return "Over A_win"
    elif ThrowA == ThrowB:
        choose = input("Input : paper, scissor, stone")
        message = f"A {choose}"
        print(message)
        return message
    else:
        print("-------------Game over: B_win-----------")
        return "Over B_win"


if __name__ == "__main__":
    # hostname, port info
    hostname = '140.113.235.154'
    tcp_port = 12234
    search_ports(hostname)

    # Step 1: Send UDP invite and wait for Player B
    connect_with_udp(tcp_port, hostname)

    # Step 2: Establish TCP connection and play the game
    connect_with_tcp(tcp_port, hostname)
