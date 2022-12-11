# P2P-Chat
A Peer-to-Peer chatting application created in Python as part of the Computer Networks course in HCMUT.

## Peer
Each peer acts as both a server (to other P2P clients for receving messages along the network), and a client (sender of messages to other P2P clients, also handling interaction with mainserver). Once a client is registered on the room server, it starts to look for a peer in the chat room it is in currently. Once it finds a suitable peer, it initiates a P2P Handshake. If accepted by the peer, both P2P clients are able to communicate with each other using Sockets.  

## Server  
The main server keeps track of the users online, and the chat sessions. Each P2P client must regularly contact the room server to maintain the connection established initially. This establishes rules for connection and authentication from users, also session requests between peers. Major role is to distribute contact address from one requesting peer to another.  

---

* Uses a new protocol created on top of TCP to demostrate creation and use of protocols.
* Uses sockets for bidirectional communication. 
* Uses threading to manage multiple peers on each P2P client.
* Uses a concept called flooding to distribute messages along the network. 
* Has logic to maintain integrity of network in case a peer leaves in order to maintain upkeep of Overlay network
* Separate logics between client and server processes within a peer.
* Has file transfer feature, by chopping up files into chunks and sending using specific format.

