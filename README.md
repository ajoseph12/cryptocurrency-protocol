@Zotkin , @ajoseph12 , @nisalup , @anotherk1nd
# Computer Networks: Blockchain Practical Project

The goal of this project is to build a Peer-to-Peer networking system capable of sharing the common data over the network in a decentralized manner. The data shared by all peers are supposed to be cryptocurrency blocks, which are validated by the members of the network.

## Instructions on how to run the project.

The blockchain requires the tracker host to be online all the time. If the tracker is unavailable, the blockchain won't run.

1. On one of the machines run the [tracker.py](tracker.py). The implementation allows being the tracker and peer on the same machine. 
2. The tracker address must be hardcoded in the [P2P_network.py](P2P_network.py). Go to line 58 and 59 of the [P2P_network.py](P2P_network.py): 
```python
self.tracker_host = "172.20.10.7" #tracker IP address as a string
self.tracker_port = 5009 #tracker port as integer
```
Change the 2 variables as described above to your corresponding tracker IP and port.

3. Run  [Blockchain.py](Blockchain.py). It will check for the peers on the network and download available blocks, then start mining.

## Application architecture
The are 3 main blocks in the architecture of this P2P application. They are represented by the following packages: 

* `Blockchain.py` - The main module of the application. It contains all the logic related to the Blockchain and mining part. There are 3 classes in the package:
  * `Block()` - An basic class for block creation. An instance is created for each new block.
  * `GenesisBlock()` - A bare-bones copy of Block() class. Created only once where genesis block created. Has the same attributes as Block(), but hardcoded.
  * `Blockchain()` - The main class of the application. Controls the logic behind the blockchain. Communicate with the network via `P2P_network.py` package.
* `P2P_network.py` - Controls all the network communications. Used both as a stand-alone application to communicate with the network and to make on-demand requests from the `Blockchain.py`. Contains one class `PeerFunct()` which is responsible for all networking communication. `PeerFunct()` use the helper package `P2P_connections.py` to establish the connection with remote server.

* `tracker.py` - The tracker class. It recieves the request from peers and sends back the adreses and listening ports of all active peers. Acrive peers are stored in `SQLite` database. Tracker ping peridically each peer to check if it is still active. If not, peer is deleted from the database.

## Apllication Logic and Interactions

The Tracker is the standalone program which runs on one of the machines. Tracker does not interact with any other applications exept by means of networking. 

When we first run the `Blockchain.py`, the following theps happening:

We intitialize `Blockchain()` class and call `main()` mathod on it. After initialisation, the `main()` initialize the instance of the `PeerFunct()` class, and therefore networking module. We pass our listening port, and an instance of `Blockchain()` class as a parameters. Then we run `main()` method on it in a new Thread. Therefore `PeerFunct()` class have an access to `Blockchain()` instance and vice versa. This allows from the `Blockchain()` perspective to be able to use all networking methods, ask for the list of blocks on the netwotk, ask to download the block, brodcast the news that new block was validated. From `PeerFunct()` perspective it allows to efficiently respond to all incoming request for blocks and list of blocks by directly accessing `Blockchain()` instance variables which hold those parameters. When the new block is mined, the `PeerFunct()` class recieve this over the network, assigns this to the correct handler based on message content, then change the instance variable of the `Networking()` class. This change is then propagated within the mining logic. Client stops mining and download the new block, validate it, and starts new block again. 

All the blocks are stored in-memory, once the last peer leaves the network the blockchain is gone.





