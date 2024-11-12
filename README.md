# HW intro 
# HW1 雙人連機遊戲 two-player online game
[website](https://bold-bonnet-933.notion.site/HW1-two-player-online-game-10313c7da37780658219d0cb00d30e2f)
10/14 更新評分標準 Update homework ranking

### Introduction

本次作業的目標是要讓同學實作能透過 TCP 以及 UDP 溝通的程式，本作業要求同學實作一個簡單的雙人連機遊戲。本作業將會分為兩個部分，第一部分是玩家發送遊戲邀請：玩家 A 要能夠透過 UDP 發送邀請給玩家 B，玩家 B 要能夠告訴玩家 B 他接收邀請，玩家 A 收到玩家 B 的回覆後要再次發送自己 Port（整個發送遊戲邀請的部分皆是透過 UDP 溝通）。第二部分是連機遊戲，玩家 B 在得知玩家 A 的 IP 與 port 後，玩家 B 要能夠透過 TCP 與玩家 A 建立連線，並透過 TCP 玩遊戲（遊戲類型不限，只要是雙人遊戲即可，例如猜拳、西洋棋⋯⋯）。


## HW2-雙人連機遊戲 Part 2 (two-player online game part 2)
[website](https://hackmd.io/@wei0107/rk0gAJWkkl)
Demo Deadline 2024/11/11(一) or 2024/11/14(四) 視教學進度而定

### Introduction
這次作業的目標是改變HW1玩家之間的連線方式，從原本兩名玩家透過 TCP/UDP 直接進行點對點連線，改為透過中央的 lobby server 溝通協調後，再以點對點方式開始遊戲。學生需要完成並Demo兩個程式：lobby server 和 client。client 端必須具備註冊、登入及登出的功能，並且使用者須透過一組 username 和 password 進行操作。當 client 登入後，lobby server 需要顯示當前線上玩家的狀況，並允許玩家建立遊戲房間或加入其他玩家的房間，進而開始遊戲。