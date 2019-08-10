import socket   
import select   
import signal   
import sys      


def signal_handler(signal, frame):
    """Function handles signal interrupt (CTRL-C)
    :param signal: signal caught
    :param frame: current stack frame
    """
    s.send('/exit')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    """Main function
    """

    # Invalid length of args
    if(len(sys.argv) < 4):
        print 'Usage : python chat_client.py hostname port username'
        sys.exit()
    # get the IRC server address
    host = sys.argv[1]
    # get the IRC server port
    port = int(sys.argv[2])
    # get user's name
    username = sys.argv[3]
    # Username no longer than 9 chars
    if len(username) > 9:
        print 'Username is too long. Max is 9 characters'
        sys.exit()

    # create TCP Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set timeout to 2 seconds
    s.settimeout(2)
    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print 'Unable to connect'
        sys.exit()
    print 'Connected to IRC server'

    # Send user's name to server
    try:
        s.send(username)
    except:
        print 'Unable to authenticate username'
        sys.exit()

    while 1:
        socket_list = [sys.stdin, s]
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(
            socket_list, [], [])

        for sock in read_sockets:

            # incoming message from remote server
            if sock == s:
                # receive up to 512 bytes of data
                data = sock.recv(512)
                # If no data, then time out
                if not data:
                    print '\nDisconnected from chat server'
                    sock.close()
                    sys.exit()
                # Data present
                else:

                    # End of line by Enter
                    if data.find('\r\n') > -1:
                        print data

            # User message
            else:
                msg = sys.stdin.readline(510)
                # Terminate message with Carriage Return
                msg += '\r\n'
                # Send message
                s.send(msg)

