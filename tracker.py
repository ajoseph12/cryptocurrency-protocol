import threading
import socket
from P2P_network import PeerFunct
from tracker_P2P_conn import PeerCommTracker
import sqlite3
from sqlite3 import Error
import socket
import struct
import threading
import time
import traceback
from P2P_connections import *
from queue import Queue
import operator
import ast  # use to convert strings of sorts to dictionary/list
#from tracker import *





q = Queue()


def btdebug(msg):
    """
    Prints a message to the screen with the name of the current thread
    """

    print("[%s] %s" % (str(threading.currentThread().getName()), msg))

    """
    Implements the core functionality of peers within a P2P network
    """

class PeerFunctTracker(object):

    def __init__(self, serverport, blockchain=None, myid=None, serverhost=None):
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


        if serverhost:
            self.serverhost = serverhost
        else:
            self.__initserverhost()

        if myid:
            self.myid = myid
        else:
            self.myid = '%s:%d' % (self.serverhost, self.serverport)

        self.peerlock = threading.Lock()
        self.shutdown = False
        self.handlers = {"GETADDR": self.addr}

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
        clientsock object, which return the IP and port of the client peer.
        Then the 'peerconn' object is used to instantiate the 'P2Pconn' class
        with IP, port and clientsock as arguments.


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
        print(clientsock)
        peercomm = PeerComm(host, port, clientsock, debug=False)

        try:
            msgtype, msgdata = peercomm.recv()

            if msgtype not in self.handlers:
                self.__debug('Not handled: %s' % (msgtype))
            else:
                self.__debug('Handing peer msg: %s' % (msgtype))
                # calls the self.msgdata method from the handlers dict
                self.handlers[msgtype](peercomm)
                hostpeer, addrpeer = peercomm.s.getpeername()
                #print("Sent Data Nisal:" + str(msgdata))
                self.__update_peer_as_active_or_add_new_peer(hostpeer, addrpeer, str(msgdata))

        except KeyboardInterrupt:
            raise

        except:
            if self.debug:
                traceback.print_exc()

        self.__debug('disconnecting' + str(clientsock.getpeername()))
        peercomm.close()

        #clientsock.send(str.encode('Welcome, type your info\n'))

    def create_connection(self):
        try:
            conn = sqlite3.connect("peers.sqlite3")
            return conn
        except Error as e:
            print("Error Establishing Connection with Database")

        return conn

    def check_for_active_peers(self):
        threading.Timer(5, self.check_for_active_peers).start()
        print("Sending Pings to all hosts...")
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT IP,Port FROM Peers;")
            rows = cur.fetchall()
            for row in rows:
                self.send_ping_2_peer( row[0], row[1])

        conn.close()

    def send_ping_2_peer(self, serverhost, serverport):
        """
        This method send a message to a select peer
        """
        try:
            dict_gb = {'HELLO': None}
            peercomm = PeerComm(serverhost, serverport)
            peercomm.send(str(dict_gb))
            str_recv = peercomm.s.recv(2048)
            str_recv = str_recv.decode('utf-8')
            s.close()
        except:
            print("Peer with IP:" + serverhost + " and port:" + serverport + " was not active!")

    def __update_peer_as_active_or_add_new_peer(self, peerip, peerport, listening_port):
        # check if peer is in database and update
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            print("Connected Peer details:" + str(peerip) + "/" + str(peerport))
            query1 = "SELECT IP,Port FROM Peers WHERE IP=\'" + str(peerip) + "\' AND Port=\'" + str(listening_port) + "\';"
            #print(query1)
            cur.execute(query1)

            rows = cur.fetchall()

            if len(rows) > 0:
                print("Peer is already in list, updated dates")
                query2 = "UPDATE Peers SET LastUpdated=datetime() WHERE IP=\'" + str(peerip) + "\' AND Port=\'" + str(listening_port) + "\';"
                cur.execute(query2)
                conn.commit()
            else:
                database2 = "peers.sqlite3"
                print("New Peer, added to List")
                iquery = "INSERT INTO Peers (IP, Port, LastUpdated) VALUES (\'" + str(peerip) + "\', \'" + str(listening_port) + "\', datetime());"
                #print(iquery)
                cur.execute(iquery)
                conn.commit()

        conn.close()

    def addr(self, peercomm, data=None):
        peer_list = []
        conn = self.create_connection()
        with conn:
            peer_list = self.return_all_active_peers()
            host, addr = peercomm.s.getpeername()
            peer_list_dic = dict()
            for item in peer_list:
                peer_list_dic[item[0]+":"+item[1]] = (item[0], int(item[1]))

            peercomm.s.sendto(bytes(str(peer_list_dic), 'utf-8'), (host, addr))
            peercomm.s.close()
        conn.close()

    def ping(self, peercomm):
        host, addr = peercomm.s.getpeername()
        peercomm.s.sendto(bytes("ping", 'utf-8'), (host, addr))


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

    def return_all_active_peers(self):
        list_of_peers = []
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            query4 = "SELECT IP,Port FROM Peers WHERE LastUpdated > datetime('now','-10 minutes') LIMIT 20;"
            cur.execute(query4)
            rows = cur.fetchall()
            #print("fuck: {}".format(rows))
            for row in rows:
                list_of_peers.append(row)
                print("Returned Peers: " + str(list_of_peers))
        conn.close()
        return list_of_peers

    def main(self):
        self.check_for_active_peers()
        s = self.makeserversocket(self.serverport)
        # s.settimeout(2)
        self.__debug(' Tracker Server started: %s (%s:%d)' %
                     (self.myid, self.serverhost, self.serverport))
        print(type(self.myid))

        while not self.shutdown:

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



if __name__ == '__main__':
    pft = PeerFunctTracker(5009)
    pft.main()

