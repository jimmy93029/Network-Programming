import socket
import random
import subprocess
import time


def connect_with_udp(hostname):

    # Step 1: Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    B_address = (hostname, 0)  # set port = 0, letting os dispatch port  

    udp_socket.bind(B_address)  # Bind the socket to the specified port
    udp_port = udp_socket.getsockname()[1]
    print(f"B is connected on port {udp_port}")

    # Step 2: Find games from broadcasts and return Player A's IP and UDP Port
    client_b_discover_games(udp_socket)

    # Step 3: Wait for Player A to send TCP connection information (TCP IP and Port)
    tcp_port, _ = udp_socket.recvfrom(4096)
    tcp_port = int(tcp_port.decode())
    print(f"Received TCP info from Player A: {tcp_port}")

    udp_socket.close()

    return tcp_port


def client_b_discover_games(udp_socket):
    # No need to create a new socket here since we are using the one passed from connect_with_udp
    print("Waiting to discover available games...")

    while True:
        data, server_address = udp_socket.recvfrom(4096)
        invite_message = data.decode()
        print(f"Discovered game from {server_address}: {invite_message}")

        # Ask the user to choose a game or continue
        choose = input("Do you want to join ? (no or yes)")
        
        if choose.lower() in ["yes", "y"]:
            udp_socket.sendto(choose.encode(), server_address)
            break


def connect_with_tcp(tcp_port, hostname):

    # Step 6: Wait until playerA open its tcp pocket and connect
    time.sleep(4) 
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((hostname, tcp_port))  # Connect to Player A

    while True:
        responseA = tcp_socket.recv(1024).decode()
        send = gameB(responseA)

        if send == "over":
            break
        else:
            tcp_socket.sendall(send.encode())

    tcp_socket.close()


def gameB(dataA):
    datas = dataA.split()

    if datas[0] == "Over":
        print(f"----------------Game over: {datas[1]}------------")
        return "over"
    else:
        choose = input("Please choose paper, scissor or stone : ")
        message = f"B {choose}"
        print(message)
        return message


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


if __name__ == "__main__":
    hostname = '140.113.235.154'

    # Step 1: Use connect_with_udp to handle all UDP communication and get the TCP connection info
    a_tcp_port = connect_with_udp(hostname)

    # Step 2: Establish TCP connection and play the game
    connect_with_tcp(a_tcp_port, hostname)
