import os
import json
from os import listdir
import rsa
import time
from time import sleep
import threading
from hashlib import sha256
import copy


class Block:
    def __init__(self, index, transaction, timestamp, previous_hash, signatures):
        self.index = index

        self.transaction = transaction

        self.timestamp = timestamp

        self.previous_hash = previous_hash

        self.signatures = signatures

    def compute_hash(self):
        mycopy = copy.copy(self)
        del mycopy.signatures
        # print(mycopy.__dict__)
        block_string = json.dumps(mycopy.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class GenesisTransaction:
    def __init__(self, ip, publicKey):
        # Type of Transaction
        self.type = 0
        self.ip = ip
        self.publicKey = publicKey


class Blockchain:
    # TODO how many signatures are required for an action to be valid among peers
    def __init__(self, path, groupPeers):
        self.BLOCKCHAIN_PATH = path
        self.TRANSACTION_PATH = self.BLOCKCHAIN_PATH + "\\Transactions\\"
        self.unconfirmed_transactions = []
        self.chain = []
        self.peers = groupPeers
        if not os.path.exists(self.BLOCKCHAIN_PATH):
            # If Path dosent Exist Create it
            os.makedirs(self.BLOCKCHAIN_PATH)
            # Load Unconfirmed Transactions
        if not os.path.exists(self.TRANSACTION_PATH):
            # If Path dosent Exist Create it
            os.makedirs(self.TRANSACTION_PATH)

        # Load Transactions if any
        transactionFiles = [transactionFile for transactionFile in listdir(self.TRANSACTION_PATH)]
        for transactionFile in transactionFiles:
            self.loadTransaction(transactionFile)

        # print(self.unconfirmed_transactions)
        # Load Blocks here
        blockFiles = [f for f in listdir(self.BLOCKCHAIN_PATH) if os.path.isfile(os.path.join(self.BLOCKCHAIN_PATH, f))]
        for blockFile in blockFiles:
            # print(blockFile)
            self.loadBlock(blockFile)

        # Start Casual Operations.
        # Thread This.
        # miner = threading.Thread(target=self.mine(), args=[])
        # miner.start()

    def getDifficulty(self):
        peers = []
        # Diffuculty of blockchain will be dependent on the users participating
        # TODO refactor this for join ban unban
        if len(peers) == 0:
            return 1
        else:
            return len(peers)

    def create_genesis_block(self, client):
        transaction = GenesisTransaction(client.publicIP, client.publicKey.save_pkcs1(format='PEM').decode("utf-8"))
        transactionStr = json.dumps(transaction.__dict__)
        # this is string json format
        # print(transactionStr)
        # print(transactionStr.__class__)
        # Genereate signature for Transaction

        signature = rsa.sign(transactionStr.encode(), client.privateKey, 'SHA-1')

        # Bytes
        # print(signature)
        # print(signature.__class__)

        genesis_block = Block(0, transactionStr, str(time.time()), "0", [str(signature)])

        genesis_block.hash = genesis_block.compute_hash()
        self.saveBlock(genesis_block)
        self.chain.append(genesis_block)


    def saveBlock(self, block):
        if not os.path.exists(self.BLOCKCHAIN_PATH):
            # Create a new directory because it does not exist
            # print("Creating Blockchain Folder")
            os.makedirs(self.BLOCKCHAIN_PATH)
        blockFile = open(self.BLOCKCHAIN_PATH + "\\Block" + str(block.index) + ".json", "w")
        # print(block.__dict__)
        blockFile.write(json.dumps(block.__dict__))
        blockFile.close()

    def loadTransaction(self, fileName):
        filePath = self.TRANSACTION_PATH + fileName
        try:
            file = open(filePath)
            # print(file)
            json_load_group = json.load(file)
            file.close()
        except Exception as e:
            print("Error Opening Transaction file :", e)
        # Make transaction here
        # print(json_load_group)
        if json_load_group["type"] == 0:
            publicKey = rsa.PublicKey.load_pkcs1(json_load_group["publicKey"])
            transaction = GenesisTransaction(json_load_group["ip"], publicKey, json_load_group["signatures"])
        self.unconfirmed_transactions.append(transaction)

    def loadBlock(self, blockFiles):
        # print(blockFiles)
        filePath = self.BLOCKCHAIN_PATH +"\\"+ blockFiles
        file = open(filePath)
        # print(file)
        block = json.load(file)
        file.close()
        # print(block)
        transaction = json.loads(block["transaction"])
        # print(transaction)
        # print(transaction.__class__)
        # Make transaction here
        if transaction["type"] == 0:
            print("Genesis block")
            transactionObj = GenesisTransaction(transaction["ip"],transaction["publicKey"])
            transactionStr = json.dumps(transactionObj.__dict__)
            blockObj = Block(block["index"],transactionStr,block["timestamp"],block["previous_hash"],block["signatures"])
            self.chain.append(blockObj)
            # print(blockObj.__dict__)


    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        self.save_unconfirmed_transactions()
        self.mine()

    def mine(self):
        while True:
            try:
                if not self.unconfirmed_transactions:
                    # TODO SLEEP
                    sleep(30)
                else:

                    diff = self.getDifficulty()
                    # print(f"Blockchain Difficulty :{diff}")
                    # print(f"Unconfirmed Transactions:{len(self.unconfirmed_transactions)}")
                    for transaction in self.unconfirmed_transactions:
                        pass
            except KeyboardInterrupt as e:
                print("Exception Keyboard")
                pass

    def save_unconfirmed_transactions(self):
        print(self.TRANSACTION_PATH)
        if not os.path.exists(self.TRANSACTION_PATH):
            # Create a new directory because it does not exist
            print("Blockchain Folder")
            os.makedirs(self.TRANSACTION_PATH)
        counter = 0
        for transaction in self.unconfirmed_transactions:
            json_file = open(self.TRANSACTION_PATH + "Transaction_" + str(counter) + ".json", "w")
            json_file.write(json.dumps(transaction.toJSON()))
            json_file.close()
            counter = counter + 1
