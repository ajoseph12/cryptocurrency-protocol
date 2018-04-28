# P2P Cryptocurrency network communication protocol.
###### The protocol is inspired by Bitcoin network

## General Message Structure
Each message transmitted over the network will be in the form of a dictionary. It must obey the following structure:

 - Method Name: This will be the first half of the dictionary (key). It will be a string with the method name.
 - Payload :The body will be the second half of the dictionary (value). It will contain data sent in the response, or in the event of a request to a tracker, the listening port of that member.

 Every request that does not obey this specification should be rejected by the host.

 ## Method types

  - **HELLO** : Exchange block count when connecting first
  - **HEY** : Sent in response to "hello" to acknowledge connection
  - **GETADDR** : Request the subset of IP:ports of avaliable peers on the network
  - **ADDR** : List of IP:ports sent in response to Getaddr
  - **BROADCASTBLOCK** : Notification that new block was discovered. Contains block number.
  - **GETBLOCK** : Single block request
  - **GETLISTOFBLOCKS** : Request list of all blocks avaliable
  - **LISTOFBLOCKS** : Contains list of blocks. Not the blocks itself. Sent in response to GetListOfBlocks.
  - **BLOCK** : Send a block. Sent in response to GetBlock method.
  - **PUSHTRANSACTION** : Send a transaction or pack of transactions.
  - **BROADCASTTRANSACTION** : Notification that new transaction is avaliable. Contains the transaction identifier.

## Interaction/Exchange

- *Communication* :  To connect to a member a ‘HELLO’ method should first be used which would in the header contain block count and current time. The remote member will reply with a ‘HEY’ and “HELLO” method to acknowledge connection. The member that initialised this exchange should then reply with a “hey” method to accept a connection from the member it tried connecting with. 
- *Relaying blocks/transactions* : When a member sends a transaction, it relays a “GETLISTOFBLOCKS” method to all of its peers. The peers can then request the full transaction using “GETBLOCK”. And on receiving the transaction if they are able validate it, each of the peers further relays a “GETLISTOFBLOCKS” method to their connected peers. If a peer already has knowledge of this transaction, it will never rebroadcast this list. The same goes for relaying blocks.
- *Updating* : On a timely basis, peers will relay their  and port numbers to other peers to update or add any newcomers into their lists. For this the “ADDR” method is used.
 - *Genesis Block* : When a new member enters the network and after the communication cycle (as seen in the first point) a “GETLISTOFBLOCKS” method is relayed containing the number of the latest block it knows about. If its peer doesn’t think that this is the latest block a “GETLISTOFBLOCKS” method is relayed back. Further on, to get each block the new member ought to use the “GETBLOCK” method and slowly build the blockchain up to its current height/sequence number.  

- *Tracker* : The tracker will send periodical ‘HELLO’ requests to all active members in the network and check if they are active. The tracker will also respond to ‘GETADDR’ requests from members.


