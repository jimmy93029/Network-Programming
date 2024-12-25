# HW intro 
# HW1 雙人連機遊戲 two-player online game
[website](https://bold-bonnet-933.notion.site/HW1-two-player-online-game-10313c7da37780658219d0cb00d30e2f)
10/14 更新評分標準 Update homework ranking

### Introduction

The goal of this assignment is to write programs that can communicate using both TCP and UDP, you are tasked to implement a simple two-player online game. The assignment is divided into two parts. The first part is the game invitation:  Player A should send an invitation to Player B using UDP. Player B should then inform Player A that they have received and accepted the invitation. After receiving Player B's response, Player A should send their port information back (the entire invitation process must be done using UDP communication). The second part is the online game. Once Player B knows Player A's IP address and port number, Player B should connect to Player A using TCP, and they can play a game together through TCP (the type of game is not restricted, as long as it is a two-player game, e.g., rock-paper-scissors, chess, etc.).


## HW2-雙人連機遊戲 Part 2 (two-player online game part 2)
[website](https://hackmd.io/@wei0107/rk0gAJWkkl)
Demo Deadline 2024/11/11(一) or 2024/11/14(四) 視教學進度而定

### Introduction
The goal of this assignment is to modify the connection method between players from HW1. Instead of having two players connect directly via TCP/UDP in a peer-to-peer manner, the connection should now be coordinated through a central lobby server before the game starts in a peer-to-peer mode. Students are required to complete and demonstrate two programs: a lobby server and a client. The client must support functions for registration, login, and logout, and users should operate using a username and password. After a client logs in, the lobby server should display the current status of online players and allow players to create game rooms or join other players' rooms to start the game.

## Congratulations, everyone! Welcome to Two-Player Online Game Part 3.

[website](https://bedecked-griffin-98f.notion.site/Network-Programming-HW3-Two-Player-Online-Game-Part-3-13dd3aba0aea808abffdebe55ef6b81c)
In this assignment, you will build upon the two-player online battle game developed in Part 2, enhancing its functionality by adding features such as an invitation list, lobby broadcasting, and basic database recording.

The game lobby in this assignment should support multiple games for players (clients) to choose from. Players can upload and manage their games independently, and when creating or joining a room, they will be prompted to download the corresponding game files.

### The goals of this assignment are:

1.	**Enhance and optimize the lobby functionality to significantly improve the user experience.**

2.	**Use sockets to Implement basic file upload/download capabilities and read/write management.**

Beyond meeting the basic requirements, we encourage students to make their projects resemble a real-world game server. Additionally, consider implementing design patterns, data structures, and algorithms to enhance your code's readability, maintainability, flexibility, and scalability.