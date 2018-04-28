from __future__ import print_function, division
from hashlib import sha1
import random
from collections import OrderedDict
import ast
import string
from time import sleep
import P2P_network
from threading import Thread


class Blockchain(object):
    """
    Main blockchain handler.
    This class is initiated only once for each machine.
    It is responsible for the entire blockchain arcitecture:
            - it creates Block objects in a factory-like manner
            - keeps track for the total number of blocks in blockchain
            - it uses the Networking(to be defined) module to communicate with peers
            - it pulls new blocks and creates the objects for them
            - it pushes (by Networking) the new blocks if it creates one
            - it recieves the payload (by Networking) and adds it to the block
    """

    def __init__(self):
        self.block_count = 0  # total number of blocks in this blockchain
        self.chain = dict()
        self.avaliable_blocks = dict()
        self.last_block_hash = None
        self.last_block_difficulty = None
        self.current_block = None
        self.transactions = {"21": 22, "22": 22, "23": 22}
        self.block_discovered_flag = [False]
        self.remotely_discovered_block = None

    def add_block_to_chain(self, block):

        self.avaliable_blocks[str(block.block_number)] = block.current_hash
        self.chain[str(block.block_number)] = block.dump()
        self.block_count += 1
        self.last_block_hash = block.current_hash
        self.last_block_difficulty = block.difficulty

    def get_transactions(self):
        """
        This method have to recieve transactions over the networking object.
        For now it's a mock returning random string
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2096))

    def main(self):
        # first check is there blocks on the network
        networking = P2P_network.PeerFunct(7569, blockchain=self)
        n = Thread(target=networking.main)
        n.setDaemon(True)
        n.start()
        print("The networking module is initiated")
        #peers = networking.peers
        #print(" this")
        block_tuple = networking.getlistofblocks()
        print(block_tuple)
        if block_tuple:
            peer_ip, peer_port, external_blocks = block_tuple
            print("There are {} external blocks found".format(max(external_blocks)))
        else:
            external_blocks = None
            print("There are no external blocks found on the network")
        # There are peers avaliable:

        if external_blocks:
            print("Strarting downloading the external blocks...")
            # add them to blockchain and validate
            for _bloc_number in external_blocks:
                print("Downloading the block number {}".format(_bloc_number))
                _block_dict = networking.getBlock(peer_ip, _bloc_number)

                block = Block(**_block_dict, discovered_remotely=self.block_discovered_flag)
                print(block.__dict__)
                self.current_block = block
                block.discovered_remotely[0] = True
                print(block.nonce)
                if block.nonce == '00000':
                    self.add_block_to_chain(block)
                    self.block_count += 1
                    self.block_discovered_flag[0] = False
                elif block.validate():
                    self.add_block_to_chain(block)
                    self.block_count += 1
                    self.block_discovered_flag[0] = False
                    print("Validated remotely discovered block number {0}.\nContinue...".format(
                        _bloc_number))
                else:
                    print("Remotely discovered block number {0} is not valid.\nDiscarding the block.\nContinue mining.".format(
                        _bloc_number))
                    break

        else:
            # there are no blocks on the network, meaning we build our genesis
            # block
            block = GenesisBlock()
            print("Created the Genesis block")
            self.add_block_to_chain(block)
            print("Added the Genesis Block to blockchain")
            networking.broadcastlock(block.block_number)
            print("Broadcasted the genesis block")

        # then we continue by adding transactions to payload and creating new
        # blocks. For now, I limited the number of blocks for testing purposes
        # At production, the condition on block count would be deleted.
        while True:
            # for now, min amount of transactions is 3, can be modified
            if len(self.transactions) >= 3:
                print("Creating the new block")
                # if there are enought transactions
                # create new block and add it to blockchain
                block = Block(self.block_count + 1,
                              self.last_block_hash,
                              self.transactions,
                              self.last_block_difficulty,
                              discovered_remotely=self.block_discovered_flag)
                self.current_block = block
                block.validate()
                if block.discovered_remotely[0]:
                    peer_ip, peer_port, external_blocks = networking.getlistofblocks()

                    for block_number in range(self.block_count, max(external_blocks) + 1):

                        _block_dict = networking.getBlock(
                            peer_ip, block_number)
                        block = Block(**_block_dict, discovered_remotely=self.block_discovered_flag)
                        self.current_block = block
                        block.discovered_remotely[0] = True

                        if block.validate():
                            self.add_block_to_chain(block)
                            self.block_count += 1
                            print("Validated remote block number {0}.".format(
                                self.block_count))

                        else:
                            print(
                                "Remotely discovered block is not valid.\nContinue")
                            break
                else:
                    print("Validated the block number {}.".format(
                        block.block_number))
                    self.add_block_to_chain(block)
                    print("Validated the block number {} to blockchain.".format(
                        block.block_number))
                    networking.broadcastlock(block.block_number)
                    print("Broadcasted the block number {} to blockchain.".format(
                        block.block_number))
            else:
                sleep(1)


class GenesisBlock(object):

    def __init__(self):

        self.block_number = 1
        self.previous_hash = "Genesis"
        self.payload = "Genesis"
        self.current_hash = "Genesis"
        self.nonce = "00000"
        self.difficulty = 5
        self.validated = True
        self.discovered_remotely = None

    def dump(self):
        """
        Converts block to dict
        """
        _dump = self.__dict__
        _dump.pop("discovered_remotely", None)
        _dump.pop("validated", None)

        return _dump


class Block(object):
    """
    This is a block object. The object is generated for each individual block.
    Blocks are generated and checked for each existing or future block.

    """

    def __init__(self, block_number, previous_hash, payload, difficulty, nonce=0, current_hash=None, discovered_remotely=False):
        """
        Arguments: 
        block_number : int, number of this block
        previous_hash : string, the hash of previous block
        payload : string, any data to be put in blockchain
        difficulty : int, number of zeros in the beginning of valid hash
        nunce : int, optional, the

        """
        self.block_number = block_number
        self.previous_hash = previous_hash
        self.payload = payload
        self.current_hash = current_hash
        self.nonce = nonce
        # TODO Create a mechanism of increasing difficulty. Can be based on
        # nonce value.
        self.difficulty = difficulty
        self.validated = False
        self.discovered_remotely = discovered_remotely

    def check_difficulty(self):
        """
        Checks if content/nonce hash has k zeros in the beginning
        """
        for k in range(self.difficulty):
            if self.current_hash[k] != "0":
                return False
        return True

    def generate_hash(self, data):
        """
        Generates sha1 hash of data

        data: string
        """
        sha = sha1()
        sha.update((data + str(self.nonce)).encode("utf-8"))
        self.current_hash = sha.hexdigest()

    def validate(self):
        """
        Iteraratively tries to generate hash with corresponding difficuty. 
        If current hash does not pass, increments nonce by 1 and tries again until 
        satisfactory hash not foud.
        Once found, clame block as valid.

        return: self
        """
        block_content = str(self.block_number) + "\n" + str(self.previous_hash) + "\n" + str(self.difficulty) + \
            "\n" + str(self.payload)

        if self.current_hash == None:
            self.generate_hash(block_content)

        if self.discovered_remotely[0]:
            return self.check_difficulty()

        while not self.validated and not self.discovered_remotely[0]:

            if self.check_difficulty():

                self.validated = True
                print("Hash is found after {0} iterations".format(self.nonce))
                print("Winning hash:\n{0}".format(self.current_hash))
                print("Winning nonce\n{0}".format(self.nonce))
                break

            else:
                self.nonce += 1
                if self.nonce % 100000 == 0:
                    print("Searching the valid nonce. Current iteration is {}kk".format(
                        int(self.nonce / 100000)))

                self.generate_hash(block_content)

    def dump(self):
        """
        Converts block to dict
        Drops Flags variables
        """
        _dump = self.__dict__
        _dump.pop("discovered_remotely", None)
        _dump.pop("validated", None)

        return _dump

if __name__ == "__main__":
    Blockchain().main()
