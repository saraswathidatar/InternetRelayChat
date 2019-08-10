import socket
import select
import logging
import signal
import sys 
import random

def broadcast(sock, message):
    """This function broadcats data to all users
    :param sock: socket object
    :param message: message to send
    """
    #Non Empty sockets
    valid_users = []

    # Iterate connection list
    for s in CONNECTIONS:
        if s != server_socket and s != sock:
            # find sockets with non empty group
            if accounts[s]['current'] != '':
                valid_users.append(s)

    for s in valid_users:
        if accounts[s]['current'] == accounts[sock]['current']:
            try:
                s.send('\n<Group message in current group %s by:\r\n' % accounts[s]['current'])
                s.send(message)
            except:
                logoff(socket)

def dataparsing(sock, message):
    """This function parses data and calls appropriate operations
    :param sock: socket object
    :param message: message to parse
    """

    if message.find('@groupmsg') == 0:

		# Splitting message for Error check
        check_msg = message.split()

        # Ensuring minimum arguments
        if len(check_msg) >= 3:
            groupmsg(sock, message)
        else:
            sock.send('\nInvalid command. Use @help for list of valid commands\r\n')

    elif message.find('@privatemsg') == 0:

        # Splitting message for Error check
        check_msg = message.split()

        # Ensuring minimum arguments
        if len(check_msg) >= 3:
            privatemsg(sock, message)
        else:
            sock.send('\nInvalid command. Use @help for list of valid commands\r\n')

    else:
        # All other Commands' parsing
        message = message.split()
        cmdparsing(sock, message)


def cmdparsing(sock, message):
    """This function parses all the commands that are used to perform specific operations
    :param sock: socket object
    :param message: speific message type
    """

    # If message length is 1, then no additional messages are sent
    if len(message) == 1:

        # @help
        if message[0] == '@help':
            # This @help will list all commands
            help(sock, command=None)

        # @membersinfo
        elif message[0] == '@membersinfo':
            membersinfo(sock, group=None)

        # @list
        elif message[0] == '@listgroups':
            listgroups(sock)

        # @exit
        elif message[0] == '@exit':
            logoff(sock)

        # If no match, then Invalid
        else:
            sock.send('\n Invalid command. Use @help for list of valid commands \r\n')

    # If message length is 2, additional commands and messages are sent
    elif len(message) == 2:

        # @help
        if message[0] == '@help':
            command = message[1]
            help(sock, command)

        # @userinfo
        elif message[0] == '@userinfo':
            username = message[1]
            userinfo(sock, username)

        # @membersinfo
        elif message[0] == '@membersinfo':
            group = message[1]
            membersinfo(sock, group)

        # @join
        elif message[0] == '@join':
            group = message[1]
            joingroup(sock, group)

        # @quitgroup
        elif message[0] == '@quitgroup':
            group = message[1]
            quitgroupfun(sock, group)

        # If no match, then Invalid
        else:
            sock.send('\n Invalid command. Use @help for list of valid commands \r\n')

    # If no match, then Invalid
    else:
        sock.send('\n Invalid command. Use @help for list of valid commands \r\n')


def help(sock, command):
    """This functions shows user the list of commands tha can be used on command line
    If command is supplied, specific info about command is sent to client
    :param sock: socket object
    :param command: option argument shows specific info for command
    """

    if command is None:
        sock.send('\n ~~~~List of valid command line options~~~~ \n')
        sock.send('@help               : Display all valid command line options \n')
        sock.send('@listgroups         : List all groups on the server\n')
        sock.send('@userinfo username  : Provides list of groups user is present \n')
        sock.send('@membersinfo #group : Displays all other users in group\n')
        sock.send('@join #group        : Join a group (It Creates one if not present) \n')
        sock.send('@quitgroup #group   : Quit from a group \n')
        sock.send('@groupmsg group <message>  : send a particular group a message\n')
        sock.send('@privatemsg user <message> : send user private message\n')
        sock.send('@help <command>     : Type specific command for more information \r\n')
        sock.send('@exit               : Logoff from server \n')

    else:
        if command == 'membersinfo':
            sock.send('\n ~~~~@membersinfo~~~~ \n')
            sock.send('The membersinfo command will display all the users on the server if no group is provided\n')
            sock.send(', and if group info is provided it displays the users in that group\r\n')

        elif command == 'listgroups':
            sock.send('\n ~~~~@listgroups~~~~ \n')
            sock.send('The listgroups command will display a list of all the groups on the server\r\n')

        elif command == 'exit':
            sock.send('\n ~~~~@exit~~~~ \n')
            sock.send('The exit command will log you off the server\r\n')

        elif command == 'userinfo':
            sock.send('\n ~~~~@userinfo~~~~ \n')
            sock.send('The userinfo command will display  information  about the specific user with <username>\n')
            sock.send('Ex: @userinfo username \r\n')

        elif command == 'join':
            sock.send('\n ~~~~join~~~~ \n')
            sock.send('The join command will make you part of a specific #group\n')
            sock.send('If no such group exists, then it will be created\n')
            sock.send('Please begin the name of the group with # and include no spaces in the groupname \n')
            sock.send('Ex: @join #group \r\n')

        elif command == 'quitgroup':
            sock.send('\n ~~~~@quitgroup~~~~ \n')
            sock.send('The quitgroup command will remove you from the #group specified (if you are a part of it)\n')
            sock.send('If you are the only person in the group, then quitgroup will remove you and delete the #group\n')
            sock.send('Ex: @quitgroup #group \r\n')

        elif command == 'privatemsg':
            sock.send('\n ~~~~~@privatemsg~~~~~ \n')
            sock.send('Send private message to <user>\n')
            sock.send('Ex: @privatemsg username hello world!\r\n')
            
        elif command == 'groupmsg':
            sock.send('\n ~~~~~~@groupmsg~~~~~ \n')
            sock.send('Send message to a particular group\n')
            sock.send('Ex: @groupmsg #group hello group!\r\n')

        else:
            sock.send('\nSpecified command does not exist.')
            sock.send(' Type @help for list of commands\r\n')


def membersinfo(sock, group):
    """This function: membersinfo displays
    user other users connected to server
    :param sock: socket object
    """

    if group is None:
        # Message
        sock.send('\n Users currently connected to server \r\n')
        #String
        user_list = ", ".join(USERS)

        # send string
        sock.send('%s\r\n' % user_list)

    else:
        users_in_group = []

        # No groups yet
        if len(GROUPS) == 0:
            sock.send('\n No groups currently on server \r\n')

        # groups are present
        else:
            # check if group is in the list
            if group in GROUPS:

                sock.send("\nUsers in %s\r\n" % group)

                # Iterate thru accounts
                for key in accounts:

                    # if group listed in account, store it in array
                    if group in accounts[key]['groups']:
                        users_in_group.append(accounts[key]['username'])

                #Array to String for Display purpose
                users_in_group = ", ".join(users_in_group)

                #Send Clinet the requested information
                sock.send('%s\r\n' % users_in_group)

            # group not in the list
            else:
                sock.send('\nNo group named %s\r\n' % group)


def listgroups(sock):
    """The function: listgroups displays user list of groups on server
    If no groups are currently on the server then the user is prompted
    Otherwise, each group in GROUPS is sent to the user
    :param sock: socket object
    """

    # listgroups is 0 so no groups
    if len(GROUPS) == 0:
        sock.send('\n No groups currently on server \r\n')

    # listgroups is not 0 so send the listgroups
    else:
        # prompt the client
        sock.send('\nList of groups on server\r\n')

        # grab the group list which is an array
        # and turn it a string
        grouplist = ", ".join(GROUPS)

        # send string off to client
        sock.send('%s\r\n' % grouplist)


def userinfo(sock, username):
    """This function user specific information
    :param sock: socket object
    :param username: user to look up
    """

    # check to see if username exists
    if username in USERS:

        # Check Socket associated with Username
        for key in accounts:
            if accounts[key]['username'] == username:
                ip = accounts[key]['ip'] 
                groups = accounts[key]['groups']  # Group info
                break  # break out of for loop

        # check to see if this socket is in any groups
        if len(groups) > 0:
            #Array to String for Display
            grouplist = ",".join(groups)

            # send client the groups
            sock.send('\ngroups: %s\r\n' % grouplist)

        # socket is not in any groups
        else:
            sock.send('\n%s is currently not present in any groups \r\n' % username)

    # Username doesn't exist
    else:
        sock.send('\n%s not currently connected to server\r\n' % username)


def joingroup(sock, group):
    """This function: join 'joins' user to group
    :param sock: socket object
    :param group: group name
    """

    user = accounts[sock]['username']
    num_groups = len(accounts[sock]['groups'])

    if group in GROUPS:
        # make sure group limit not reached
        if num_groups < 10:
            # add group to user's groups
            accounts[sock]['groups'].append(group)
            # make group the user's current group
            accounts[sock]['current'] = group
            # notify client
            sock.send('\nJoined %s\r\n' % group)
            # tell everyone someone has arrived
            broadcast(sock, ('\n%s joined %s\r\n') % (user, group))
        else:
            # notify user that limit reached
            sock.send('\ngroup limit reached\r\n')
    else:
        # make sure group limit not reached
        if num_groups < 10:
            # make sure group starts with # character
            if group.find('#') == 0:
                # create group by adding it to the group list
                GROUPS.append(group)
                # add group to user's groups
                accounts[sock]['groups'].append(group)
                # make group the user's current groups
                accounts[sock]['current'] = group
                # notify client
                sock.send('\nJoined %s\r\n' % group)
                # Notify that someone has joined
                broadcast(sock, ('\n%s joined %s\r\n') % (user, group))
                # for the server logs
                logging.info('New group: %s' % group)
                logging.info('Updated group list: %s' % GROUPS)
            # invalid group name, no bueno
            else:
                sock.send('\nInvalid group name\r\n')
                sock.send('\nSee @help join\r\n')

        else:
            # notify user that limit reached
            sock.send('\n Group limit reached - Only 10 members per group \r\n')


def quitgroupfun(sock, group):
    """This function removes user from group
    :param sock: socket object
    :param group: group to leave
    """

    user = accounts[sock]['username']
    groups = accounts[sock]['groups']

    # See if user is in group
    if group in groups:
        # Notify group that user is leaving
        broadcast(sock, ('\n%s left %s\r\n') % (user, group))
        # user has the group in their group list
        # check to see if its their current group
        if accounts[sock]['current'] == group:
            # reset current group
            accounts[sock]['current'] = ''
            # remove group from user's
            # group list
            accounts[sock]['groups'].remove(group)
            # notify user
            sock.send('\nYou left %s\r\n' % group)
            # update groups variable
            groups = accounts[sock]['groups']
            # update current group by
            # randomly selecting a group from their list
            if len(groups) > 0:
                current = random.choice(groups)
                accounts[sock]['current'] = current
                #sock.send('\nCurrent group is now %s\r\n' % current)

        # not user's current group
        else:
            # remove group from user's
            # group list
            accounts[sock]['groups'].remove(group)
            # notify user
            sock.send('\nYou left %s\r\n' % group)
        count = 0
        # go through the accounts
        for key in accounts:
            # found accounts in group
            if group in accounts[key]['groups']:
                # count em up
                count += 1
        # count is equal to 0 so no one in group
        if count == 0:
            # remove from group list
            GROUPS.remove(group)
            # log info for server
            logging.info('%s removed from group list' % group)
            logging.info('Updated group list: %s' % GROUPS)
    # User isn't in that group
    else:
        sock.send('\nUser must be part of group to leave\r\n')

def privatemsg(sock, msg):
    """This function is to send messages from user to another user privately
    :param sock: socket object
    :param msg: message to send
    """

    sender = accounts[sock]['username']

    #Splitting to grab the user
    user = msg.split()[1]

    # user tried to send a private message
    # to themselves
    if user == sender:

        # notify bad user
        sock.send('\nCan not private message yourself!\r\n')

        # get outta here
        return

    # Splitting to grab the message
    msg2send = msg[13+len(user):]

    # check to see if that username is
    # in the user list
    if user in USERS:

        # go through the accounts
        for key in accounts:

            # find the specified user
            if accounts[key]['username'] == user:

                # try sending the private message
                try:
                    key.send('\n<private message from %s>%s\r\n'
                             % (sender, msg2send))
                    break  # to stop needless iterations

                # otherwise log that socket off
                except:
                    logoff(key)

    # username wasn't in user list
    else:
        sock.send('\nNo such user\r\n')
        
        
def groupmsg(sock, msg):
    """This function is to send messages from user to a particular group
    :param sock: socket object
    :param msg: message to send
    """

    sender = accounts[sock]['username']

    # Splitting to grab the group
    group = msg.split()[1]
    #sock.send("\nUsers in %s\r\n" % group)
    
    # Extract group, and remaining is message
    msg2send = msg[10+len(group):]
    
    # If group is present
    if group in GROUPS:
		if group in accounts[sock]['groups']:
			# go through the accounts
			for key in accounts:

				# find the specified user
				if group in accounts[key]['groups']:
					#if accounts[key]['groups'] == accounts[sock]['groups']:
						# Try sending the group message
						try:
							key.send('\n< Message on the group: %s, from %s>%s\r\n'
									 % (group, sender, msg2send))
							#break  # to stop needless iterations

						# otherwise log that socket off
						except:
							logoff(key)
                #else:
					#sock.send('\n Cannot send mesage to this group: %s, you are not part of it\r\n' % group)
		else:
			sock.send('\n Cannot send mesage to this group: %s, you are not part of it\r\n' % group)

    # No such group exists
    else:
        sock.send('\n No such group exists \r\n')        

def logoff(sock):
    """This function removes user from group, and exits
    :param sock: socket object
    """

    user = accounts[sock]['username']
    groups = accounts[sock]['groups']

    # Notify
    broadcast(sock, '\n%s has gone offline\r\n' % user)
    # Remove user from groups
    for i in xrange(len(groups) - 1, -1, -1):
        quitgroupfun(sock, groups[i])
    # Server logging
    logging.info('%s is offline' % user)
    # remove client from user list
    USERS.remove(user)
    logging.info('Updated user list: %s' % USERS)
    # close the socket
    sock.close()
    # remove socket from connection list
    CONNECTIONS.remove(sock)
    # remove account
    del accounts[sock]


##########################################
######################################################

def signal_handler(signal, frame):
    """Function handles signal interrupt (CTRL-C)
    :param signal: signal caught
    :param frame: current stack frame
    """

    for s in CONNECTIONS:
        if s != server_socket:
            logoff(s)
    server_socket.close()

    logging.info('Server shutting down')
    sys.exit(0)


# initialize signal handler
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    """Main function
    """


    # for logging information on the server
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')

    # to keep track of user information
    accounts = {}
    # list to keep track of usernames
    USERS = []
    # list to keep track of socket descriptors
    CONNECTIONS = []
    # array to keep track of groups
    GROUPS = []
    # receiving buffer size
    BUFFER_RX = 512
    # server port number
    PORT = 8080
    # create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set socket options
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind socket
    server_socket.bind(("0.0.0.0", PORT))
    # start listening with backlog of 10
    server_socket.listen(10)
    # Add server socket to the list of readable connections
    CONNECTIONS.append(server_socket)
    server_ip = socket.gethostbyname(socket.gethostname())
    server_port = str(PORT)

    # information that might be useful to clients
    logging.info('Chat server started [%s:%s]' % (server_ip, server_port))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(
            CONNECTIONS, [], [])

        for sock in read_sockets:

            # New Client connection
            if sock == server_socket:

                # Handle the case in which there is
                # a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()

                # Add to connection list
                CONNECTIONS.append(sockfd)

                # Creating a new account for the user
                accounts[sockfd] = {
                    'username': '',
                    'ip': '',
                    'groups': [],
                    'current': ''
                }

                # Store the new client's username
                name = sockfd.recv(BUFFER_RX)
                # store IP address for new User
                accounts[sockfd]['ip'] = addr[0]

                # Check in User list if User name already exists, if not then add to account list
                if name in USERS:
                    sockfd.send('\n This username already exists \r\n')
                    sockfd.close() #Close the newly opened connection
                    CONNECTIONS.remove(sockfd)
                else:
                    sockfd.send('Hello ')
                    sockfd.send(name)
                    sockfd.send(', Welcome to the Chat Room \r\n')
                    sockfd.send('Lets get started!!\r\n')
                    sockfd.send('\n Type @help for valid command line options \r\n')

                    #Add Username in Account list
                    accounts[sockfd]['username'] = name

                    #Add User to User list
                    USERS.append(name)

                    #Debug informstion on Server side
                    logging.info('Client (%s, %s) connected' % addr)
                    logging.info('Client is know as %s' % name)
                    logging.info('Updated user list: %s' % USERS)

            # Else condition: Not a new connection, but some message that is sent from a client
            else:
                #Client sends data
                try:

                    data = sock.recv(BUFFER_RX).strip()

                    if data:
                        # All commands begin with a @
                        if data.find('@') == 0:
                            # Parse input command 
                            dataparsing(sock, data)
                        else:
                             sock.send('\n Please use @command for any message. Use @help for list of valid commands \r\n')

                except:
                    logoff(sock)
                    continue

