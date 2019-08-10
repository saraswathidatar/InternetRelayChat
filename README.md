# InternetRelayChat
Copyright (c) 2019 Saraswathi Govind Datar NA

This project is licensed under the "MIT License". Please see the file LICENSE in this distribution for license terms.
https://github.com/saraswathidatar/InternetRelayChat/blob/master/LICENSE

Introduction:
IRC is an open protocol that uses TCP and, optionally, TLS. An IRC server can connect to other IRC servers to expand the IRC network. Users access IRC networks by connecting a client to a server. The standard structure of a network of IRC servers is a tree. Messages are routed along only necessary branches of the tree but network state is sent to every server and there is generally a high degree of implicit trust between servers.

Server: The server is the central point to which clients may connect and talk to each other. The traditional IRC protocol supports multiple servers in a spanning tree configuration. However, for the purpose of this project we will limit the number of servers to one. This single server will act as the backbone of our IRC network, providing a unique point for clients to connect to and talk to one another.

Client: Client is anything that connects to our single server. Each client is identified by a unique username. In this version of our IRC protocol, there is no registered user database, no persistent clients. Users connect to the server by providing a username at the beginning of every session and the end of the session all of the user’s information is erased.

Chatrooms: The basic means of communicating to a group of users in IRC session is through chat rooms. Channels on a network can be displayed using the IRC command LIST, which lists all currently available channels that do not have the modes +s or +p set, on that particular network. Users can join a channel using the JOIN command, in most clients available as /join #channelname. Messages sent to the joined channels are then relayed to all other users.

