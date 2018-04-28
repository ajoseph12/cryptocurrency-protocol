The mining of the blocks works, and peers can connect to each other in order to communicate the discovery of new blocks, and request information when first connecting to the network. There are some problems with broadcasting the discovery of blocks, where after discovering a new block, the miner is able to mine several more blocks before the peers receive the message that the first block was mined. This is a problem since lots of computational power would be wasted on mining orphaned blocks. This may be due to the difficulty of the mining being set at a too low difficulty, causing blocks to be mined far too easily compared to the network speeds. The difficulty should therefore be tuned according to the network speed as well as the computing power of the network.

Our initial objective was to get a fully functioning model of a block chain network up and running. But with time and while getting to understand the complexity a blockchain network entail we had to settle for realizing only blockchain functionality without implementing transactions. So all the methods except for the ones pertaining to effectuating transactions were realized. With of course a few bugs in the final model.

On an average each member put in around 3-6 hours per week:
 - Allwyn : 40 hours
 - Yevhein : 40 hours
 - Nisal : 25 hours
 - Josh	: 25 hours 

Tasks for the project were assigned as follows:
 - Allwyn - P2P network
 - Yevhein - Transactions
 - Nisal - Tracker and assistance with P2P network
 - Josh  - Transactions 

Evaluation on Good Development Practices 
(1-3 : 1- completely, 3 -not at all)
 
 - write your documentation in markdown : 1
 - commit only source and configuration : 1
 - use .gitignore file(s) : 1
 - do not use git just to store a zip of your projec : 1
 - commit/push often, so you don't fear making changes : 2
 - provide good commit messages : 2
 - use English for all commit messages : 1
 - mention in the message who contributed to the commit : 3
 - write your code in English : 1
 - indent/format your code properly : 1
 - avoid mixing spaces and tabs : 1
 - keep your code clean : 2 
 - test a lot and often : 2
 - have automated tests : 2
 - have stress tests : 2
 - have tests for "bad" behaviors from other peers : 2
 - document how to use, compile, test and start your project : 2
 - document how to understand and continue your project : 2




