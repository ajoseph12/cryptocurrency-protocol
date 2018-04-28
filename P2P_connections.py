import struct
import socket
import ast  # use to convert string to dictionary
import sys


class PeerComm:

    def __init__(self, host, port, sock=None, debug=False):
        """
        The class 'PeerComm' allows for messages to be extracted from the 
        socket object passed as an argument to the __init__ method - on instantiating 
        the class - and put together a fitting response if required. 

        """

        self.s = sock
        self.debug = debug
        if not self.s:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.settimeout(5)
                self.s.connect((host, int(port)))
            except:
                print("Error: ", sys.exc_info()[0])
                print("Was not able to connect remote server {} {}".format(host, port))

        self.sd = self.s.makefile('rwb', 0)

    def __makemsg(self, msgtype, msgdata):
        """
        This method takes a message to be sent to another pper, and then 
        packs and encodes it 
        """

        msglen = len(msgdata)
        msg = struct.pack()

    def send(self, msg):
        """
        This method deals with sending the packed message to a 
        fellow peer.
        """
        try:
            self.s.sendall(str.encode(msg))

        except KeyboardInterrupt:
            raise

        except:
            if self.debug:
                traceback.print_exc()
                return False

        return True

    def recv(self):
        """
        Receives message from peer
        """

        data = self.s.recv(4096)
        data = data.decode('utf-8')
        print("Printing the message content")
        print(data)
        msg = (ast.literal_eval(data))

        typ = next(iter(msg))
        data = next(iter(msg.values()))
        return typ, data

    def close(self):
        """
        """

        self.s.close()
