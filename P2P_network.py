import socket
import struct
import threading
import time
import traceback
from P2P_connections import *
from queue import Queue
import operator
import ast
import sys

# use to convert strings of sorts to dictionary/list
#from tracker import *


q = Queue()


def btdebug(msg):
    """
    Prints a message to the screen with the name of the current thread
    """

    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class PeerFunct(object):

    """
    Implements the core functionality of peers within a P2P network
    """

    def __init__(self, serverport, blockchain, myid=None, serverhost=None):
        """
        When an instance of the 'PeerFunct' class is created this special 
        method is called, initialising a peer. The peer will have the ability
        to catalog up to 'maxpeers' number of peers and will listen on a 
        given server port with a defined peer name (id) and host address (IP).
        If the host address is not supplied, it'll be determined by trying and
        connecting to an internet host.

        Arguements:
        self -- instantiated variable
        maxpeers --  maximum number of peers catalogued 
        serverport -- port on which the peer will listen for requests
        serverhost -- IP address of the peer
        myid -- unique peer identifier (tuple of (IP:port) in absence of an id)

        Attributes:
        self.peerlock -- allows for regulated access of common variables of incomming requests
        self.peers -- dictionary of peers {peerid : (IP,port)} 
        self.handlers -- dictionary of methods 
        self.shutdown -- used to terminate main loop
        """
        self.blockchain = blockchain
        self.debug = 1
        self.serverport = int(serverport)
        self.tracker_host = "172.20.10.6"
        self.tracker_port = 5009

        if serverhost:
            self.serverhost = serverhost
        else:
            self.__initserverhost()

        if myid:
            self.myid = myid
        else:
            self.myid = '%s:%d' % (self.serverhost, self.serverport)

        self.peerlock = threading.Lock()
        self.peers = self.getAddr()
        _rm = self.serverhost + ":" + str(self.serverport)
        self.peers.pop(_rm, None)
        self.shutdown = False
        self.handlers = {"GETLISTOFBLOCKS": self.listofblocks,
                         "GETBLOCK": self.block, "BROADCASTBLOCK": self.getbroadcastblock,
                         "HELLO": self.hello}

    def __initserverhost(self):
        """
        Attempts to connect to an Internet host inorder to determine the local
        machine's IP address.

        - The arguments used with socket method allows communication using 
        IPv4 protocol with a TCP connection.
        - s.getsockname delivers (IP,port)

        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("www.google.com", 80))
        self.serverhost = s.getsockname()[0]
        s.close()

    def __debug(self, msg):
        """
        If self.debug is greater than 0 the 'btdebug' function call is made with 
        'msg' as the argument.

        Argument:
        msg -- the error message to be relayed as an argument to 'btdebug'
        """

        if self.debug:
            btdebug(msg)

    def __handlepeer(self, clientsock):
        """
        The thread started in the the main method calls this function with
        clientsock as the argument. The method starts by a method call on the 
        clientsock object, which returns the IP and port of the client peer.
        Then the 'peerconn' object is used to instantiate the 'P2Pconn' class
        with IP, port and clientsock as arguments. Instance of this class will
        be responsible for receiving, decoding, encoding and sending messages 
        from the connecting peer. 
        Further the message type and data of the connecting peer is d



        #clientsock.send(str.encode('Welcome, type your info'))
        #print("The socket is\n")
        #print(clientsock)
        #data = clientsock.recv(2048)
        #reply = 'Your method is :' + data.decode('utf-8')
        #print(reply)

        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #s.connect('localhost',5777)
        #s.sendall(str.encode(reply))
        #print("\nSent")

        """
        self.__debug('New child' + str(threading.currentThread().getName()))
        self.__debug('Connected' + str(clientsock.getpeername()))
        host, port = clientsock.getpeername()
        peercomm = PeerComm(host, port, clientsock, debug=False)

        try:
            msgtype, msgdata = peercomm.recv()

            if msgtype not in self.handlers:
                self.__debug('Not handled: %s' % (msgtype))
            else:
                self.__debug('Handing peer msg: %s' % (msgtype))
                # calls the self.msgdata method from the handlers dict
                self.handlers[msgtype](peercomm, msgdata)

        except KeyboardInterrupt:
            raise

        except:
            if self.debug:
                traceback.print_exc()

        self.__debug('disconnecting' + str(clientsock.getpeername()))
        peercomm.close()

        #clientsock.send(str.encode('Welcome, type your info\n'))

    def makeserversocket(self, port, backlog=5):
        """
        This method constructs a socket for the peer to communicate with other
        peers. It begins by creating a socket object 's', followed by using the 
        'setsockopt' method which allows for disconnected peers to reconnect to 
        the peer on re-entry into the network (if this command is not used ,the host 
        peer might flag that partiuclar port where the communicating peer was 
        once connected to). Further on, the object 's' is bound to a port of the 
        host peer. The IP of the peer need not be stated, as it's implicitly the
        localhost. The IP will only be required by the connecting peer. The method
        is terminated with a socket listen command and the socket object is returned.
        The object can later be used to accept incoming connections.

        The backlog argument indicates how many incomming connections should be
        queued up. Albeit a value of 5 is used, this might be rendered useless
        with a multithreaded server. 
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        print("Listening")
        s.listen(backlog)
        return s

    def send2peer(self, serverhost, serverport):
        """
        This method send a message to a select peer
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverhost, serverport))
        s.sendall(b'getlistofblocks')
        str_recv = s.recv(2048)
        print(str(str_recv.decode('utf-8')))
        s.close()

        #s.sendall(str.encode('\nsup dickheads\n my life is shit\n how about yours'))

    def hello(self, peercomm, data=None):
        """""

        This method is called when the peer recieves a hello

        """""
        host, addr = peercomm.s.getpeername()
        data = "HEY"
        # add my ip and port to the message content
        #not complete
        peercomm.s.sendto(bytes(data, 'utf-8'), (host, addr))

    def gethello(self, host):
        """""
        This method is when the peer needs to send hello to another peer.
        Eugiene, If the hey response is recieved it will be returned, otherwise nohello is returned to you.
        """""
        addr = None

        for key in self.peers.items():
            if key[1][0] == host:
                addr = key[1][1]

        peercomm = PeerComm(host, addr)
        peercomm.send("HELLO")

        str_recv = peercomm.s.recv(2048)
        str_recv = str_recv.decode('utf-8')
        str_recv = ast.literal_eval(str_recv)
        if str_recv.upper() == "HEY":
            return str_recv
        else:
            return "NOHELLO"

    def listofblocks(self, peercomm, data):
        """
        A method in response to  by a newcommer peer's getlistofblocks request.
        The method gets called from the self.handlers dictionary as and when a 
        peer is handled within in the _handlepeer method. When the method call
        is made the PeerComm class instance is passed as an argument. This 
        instance is the later used pack and send the message. 

        ls_blocks = stores list of blocks by calling blockchain class


        """
        host, addr = peercomm.s.getpeername()

        block_range = []
        for ls_blocks in self.blockchain.avaliable_blocks.items():
            block_range.append(ls_blocks[0])

        block_range = str(block_range)
        peercomm.s.sendto(str.encode(block_range, 'utf-8'), (host, addr))

    def getlistofblocks(self):
        """
        When the blockchain class calls this method, this method
        should initiate connections to multiple peers sending them
        each a message to get a list of blocks.
        The peer then receives lists from each of the peer wihtin 
        its list of peers and returns only the longest list of blocks 
        to the blockchain class.   

        Variables: 
        ls_blk -- a list of tupels (host, port,len(of list))

        """
        ls_blk = []
        dict_glb = {'GETLISTOFBLOCKS': None}

        if not self.peers:
            print("There are no peers on the network")
            return None

        def get():

            while True:
                try:
                    peer = q.get()
                    host = peer[0]
                    port = peer[1]
                    peercomm = PeerComm(host, port, debug=False)
                    peercomm.send(str(dict_glb))
                    str_recv = peercomm.s.recv(2048)
                    str_recv = str_recv.decode('utf-8')
                    str_recv = ast.literal_eval(str_recv)

                    with self.peerlock:
                        ls_blk.append((host, port, str_recv))

                    q.task_done()  # indicates that a particular task has been handled, reducing the queue count
                    peercomm.close()
                except:
                    print("Were not able to connect the peer on {}".format(host, port))
                    q.task_done()
                    peercomm.close()

                    pass

        for i in range(len(self.peers)):
            threading.Thread(target=get).start()

        for peer in self.peers.items():
            q.put(peer[1])

        # Blocks until all items in the queue have been gotten and processed.
        q.join()
        if ls_blk:
            print(max(ls_blk, key=operator.itemgetter(2)))

            # needs to return that peer with longest chain
            return max(ls_blk, key=operator.itemgetter(2))
        else:
            return None

    def block(self, peercomm, data):
        """
        Eugene, I'll send you the block id (data) and you have to send me that
        block. This block will be saved in blk_rec.
        """

        host, addr = peercomm.s.getpeername()

        peercomm.s.sendto(str.encode(str(self.blockchain.chain[
                          str(data)]), 'utf-8'), (host, addr))

    def getBlock(self, host, block_num, get_block_id=None):
        """
        Eugene is supposed to give me the following:
            - IP of the peer (host)
            - required block number (block_num)

        """

        dict_gb = {'GETBLOCK': block_num}
        addr = None

        for key in self.peers.items():
            if key[1][0] == host:
                addr = key[1][1]

        peercomm = PeerComm(host, addr)
        peercomm.send(str(dict_gb))

        str_recv = peercomm.s.recv(2048)
        str_recv = str_recv.decode('utf-8')
        str_recv = ast.literal_eval(str_recv)

        return str_recv

    def getbroadcastblock(self, peercomm, data):
        """
        You will receive the ip, port and the newly mined block number,
        (host, addr, block_num). Keep track of the ip because if you need
        the newly mined block you'll have to make the getblock method call
        with ip and block number as agruments.
        """

        #host, addr = peercomm.s.getpeername()
        block_num = data
        #block_num = block_num.decode('utf-8')
        if block_num not in self.blockchain.avaliable_blocks.keys() and self.blockchain.block_count == block_num:
            self.
            blockchain.block_discovered_flag[0] = True
        else:
            pass
        # return (host, addr, block_num)

    def broadcastlock(self, block_num):
        """
        Eugene, you need to give me the block number (block_num) you just finished mining.

        """
        braod_blk = dict()
        braod_blk = {"BROADCASTBLOCK": block_num}

        def sendall():

            while True:

                peer = q.get()
                host = peer[0]
                port = peer[1]
                peercomm = PeerComm(host, port, debug=False)
                peercomm.send(str(braod_blk))

                q.task_done()  # indicates that a particular task has been handled, reducing the queue count
                peercomm.close()
        if self.peers:
            for i in range(len(self.peers)):
                threading.Thread(target=sendall).start()

            for peer in self.peers.items():
                q.put(peer[1])

            q.join()
        else:
            print("There are no peers to broadcast to.")

    def gettracker(self):
        return tracker_host, tracker_port

    def getAddr(self):
        try:
            host = self.tracker_host
            addr = self.tracker_port
            data = {"GETADDR": self.serverport}
            # add my ip and port to the message content
            # not complete
            #peercomm.s.sendto(bytes(data, 'utf-8'), (host, addr))
            peercomm = PeerComm(host, addr)
            print("This is happenign ")
            peercomm.send(str(data))

            str_recv = peercomm.s.recv(2048)
            str_recv = str_recv.decode('utf-8')
            print("Recieved:")
            print(str_recv)
            str_recv = ast.literal_eval(str_recv)
            return str_recv
        except TimeoutError:
            print("Tracker connection timeout.")
            sys.exit("Was not able to connect to server, aborting.")
        except PermissionError:
            print("Got PermissionError while trying to connect to the server")
            sys.exit("Was not able to connect to server, aborting")
        except:
            sys.exit("Was not able to connect to tracker server, aborting.")

    def update(self):

        while True:

            try:

                self.peers = self.getAddr()
                rm_self = self.serverhost + ":" + str(self.serverport)
                self.peers.pop(rm_self, None)
                time.sleep(20)

            except KeyboardInterrupt:
                print("KeyboardInterrupt: Breaking loop")
                pass

    def main(self):
        """
        The main method first makes a call to the 'makeserversocket' method 
        obtaining the socket object. The socket is then set to timeout every
        2 seconds so as to ensure that connections are nicely terminated. An 
        infinite loop is started to listen for incoming peer requests and using
        the 'accept' object the client address and socket is accepted. The contents
        of which are described below. A thread is then assigned to this request with
        the socket as the argument to the '__self.handlpeer' method which is then 
        assigned to the target. This is followed by thread activation. 

        clientsock content:
        <socket.socket fd = 4, family = Address.AF_INET, 
         type = SocketKind.SOCK_STREAM, proto = 0, 
         laddr = (IP,port), raddr = (IP,port)>

        clientaddr content: (IP,port) - of client peer
        """
        threading.Thread(target=self.update).start()

        s = self.makeserversocket(self.serverport)
        # s.settimeout(2)
        self.__debug('Server started: %s (%s:%d)' %
                     (self.myid, self.serverhost, self.serverport))
        print(type(self.myid))

        while not self.shutdown:
            #print("I am listening")
            try:
                self.__debug('Listening for connections...')
                clientsock, clientaddr = s.accept()
                # clientsock.settimeout(None)

                t = threading.Thread(target=self.__handlepeer,
                                     args=[clientsock])
                t.start()

            except KeyboardInterrupt:
                print('KeyboardInterrupt : terminating main')
                self.shutdown = True
                continue

            except:
                if self.debug:
                    traceback.print_exc()
                    continue

        self.__debug('Exiting main loop')

        s.close()
