import os
import json
from os import listdir
import rsa
import time
from time import sleep
import threading
from hashlib import sha256
import copy
from pickle import dumps, loads



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
        if hasattr(mycopy, 'hash'):
            del mycopy.hash
        block_string = json.dumps(mycopy.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class UnconfirmedTransaction:
    def __init__(self,transaction,signatures=[]):
        self.transaction = transaction
        self.signatures = signatures


class GenesisTransaction:
    def __init__(self, ip, publicKey):
        # Type of Transaction
        self.type = 0
        self.ip = ip
        self.publicKey = publicKey


class InviteTransaction:
    def __init__(self,ip):
        self.type = 1
        self.ip = ip


class Blockchain:
    def __init__(self, path, groupPeers,groupId):
        self.BLOCKCHAIN_PATH = path
        self.TRANSACTION_PATH = self.BLOCKCHAIN_PATH + "\\Transactions\\"
        self.unconfirmed_transactions = []
        self.chain = []
        self.peers = groupPeers
        self.groupId = groupId
        if not os.path.exists(self.BLOCKCHAIN_PATH):
            # If Path dosent Exist Create it
            os.makedirs(self.BLOCKCHAIN_PATH)
            # Load Unconfirmed Transactions
        if not os.path.exists(self.TRANSACTION_PATH):
            # If Path dosent Exist Create it
            os.makedirs(self.TRANSACTION_PATH)


        self.loadTransactions()

        # print(self.unconfirmed_transactions)
        # Load Blocks here
        blockFiles = [f for f in listdir(self.BLOCKCHAIN_PATH) if os.path.isfile(os.path.join(self.BLOCKCHAIN_PATH, f))]
        for blockFile in blockFiles:
            self.loadBlock(blockFile)

        # Start Casual Operations.
        # Thread This.
        miner = threading.Thread(target=self.mine, args=[])
        miner.start()
        # print(self.unconfirmed_transactions)
        # for block in self.chain:
        #     print(block)

    def getDifficulty(self):
        # Diffuculty of blockchain will be dependent on the users participating
        # TODO refactor this for join ban unban
        if len(self.peers) == 0:
            return 1
        else:
            return len(self.peers)

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

    def loadTransactions(self):
        filePath = self.TRANSACTION_PATH + "Transactions.json"
        if os.path.exists(filePath):
            try:
                file = open(filePath)
                # print(file)
                json_load_group = json.load(file)
                file.close()
            except Exception as e:
                print("Error Opening Transaction file :", e)
            for x in json_load_group:
                transaction = UnconfirmedTransaction(x["transaction"], x["signatures"])
                # print(transaction)
                self.unconfirmed_transactions.append(transaction)
            # print(self.unconfirmed_transactions)

    def loadBlock(self, blockFiles):
        # print(blockFiles)
        filePath = self.BLOCKCHAIN_PATH + "\\" + blockFiles
        file = open(filePath)
        # print(file)
        block = json.load(file)
        file.close()
        # # print(block)
        # transaction = json.loads(block["transaction"])
        # # print(transaction)
        # # print(transaction.__class__)
        # # Make transaction here
        # if transaction["type"] == 0:
        #     # print("Genesis block")
        #     transactionObj = GenesisTransaction(transaction["ip"], transaction["publicKey"])
        #     transactionStr = json.dumps(transactionObj.__dict__)
        blockObj = Block(block["index"], block["transaction"], block["timestamp"], block["previous_hash"],
                             block["signatures"])
        blockObj.hash = block["hash"]
        #TODO Add all transactions here

        # elif transaction["type"] == 1:
        #     # print("Genesis block")
        #     # print(transaction)
        #     transactionObj = InviteTransaction(transaction["ip"])
        #     transactionStr = json.dumps(transactionObj.__dict__)
        #     blockObj = Block(block["index"], transactionStr, block["timestamp"], block["previous_hash"],
        #                      block["signatures"])
        #     blockObj.hash = block["hash"]

        self.chain.append(blockObj)
            # print(blockObj.__dict__)

    def add_new_transaction(self, transaction : str):
        newUnconfirmedTransaction = UnconfirmedTransaction(transaction)
        self.unconfirmed_transactions.append(newUnconfirmedTransaction)
        self.save_unconfirmed_transactions()

    def updateBlockchain(self):
        responses = []
        for peer in self.peers:
            # print("Peer to ask for update:",peer)
            updateBlockchainReq = Networking.UpdateBlockchainRequest(self.groupId)
            res = Networking.sendRequest(peer[0], 6700, dumps(updateBlockchainReq))
            print(res)
            if res is not False:
                 responses.append(res)
        if len(responses):
            for x in res:
                print(x.answer)
            #Someone answered.
            # update from responded peers until you have max blockchain thing .

    def mine(self):
        #Load my public key.
        keyLoc = self.BLOCKCHAIN_PATH+"\\..\\..\\..\\PRIVATEKEY.json"
        # print(f"key location = {keyLoc}")
        f = open(keyLoc, "rb")
        data = f.read()
        privateKey = rsa.PrivateKey.load_pkcs1(data)
        # print(publicKey)
        f.close()
        while True:
                #Update Blockchain.
                self.updateBlockchain()

                if not self.unconfirmed_transactions:
                    #If No Transaction sleep and check again soon.
                    sleep(30)
                else:
                    diff = self.getDifficulty()
                    print(f"Blockchain Difficulty :{diff}")
                    print(f"Unconfirmed Transactions:{len(self.unconfirmed_transactions)}")
                    for transaction in self.unconfirmed_transactions:
                        transaction :UnconfirmedTransaction
                        #For Each Transaction if signatures < difficulty collect transactions
                        if diff>len(transaction.signatures):
                            if not len(transaction.signatures):
                                # No Signatures add my signature
                                signature = rsa.sign(transaction.transaction.encode(),privateKey, 'SHA-1')
                                transaction.signatures.append(str(signature))
                                self.save_unconfirmed_transactions()
                            else:
                                #Get Signatures from other persons.
                                pass
                        else:
                            #We have the signatures number procede to make block and share.
                            print(f"Signature {transaction} ready to be made block.")
                            # Bytes
                            lastBlock = self.getLastBlock()
                            print(lastBlock)
                            lastBlock : Block
                            print(f"Last Block Index :{lastBlock.index}")
                            newBlock = Block(lastBlock.index+1, transaction.transaction, str(time.time()), lastBlock.compute_hash(),transaction.signatures)
                            newBlock.hash = newBlock.compute_hash()
                            self.unconfirmed_transactions.remove(transaction)
                            self.save_unconfirmed_transactions()
                            self.saveBlock(newBlock)
                            self.chain.append(newBlock)
                    sleep(30)

    def getLastBlock(self):
        lastBlockIndex = self.chain[0].index
        #Find last Block and return it
        lastBlock = self.chain[0]
        for block in self.chain:
            print(block.index)
            if block.index > lastBlockIndex:
                lastBlock = block
                lastBlockIndex = block.index
        return lastBlock


    def save_unconfirmed_transactions(self):
        # print(self.TRANSACTION_PATH)
        if not os.path.exists(self.TRANSACTION_PATH):
            # Create a new directory because it does not exist
            # print("Blockchain Folder")
            os.makedirs(self.TRANSACTION_PATH)
        json_file = open(self.TRANSACTION_PATH + "Transactions"+ ".json", "w")
        json_file.write((json.dumps([ob.__dict__ for ob in self.unconfirmed_transactions])))
        json_file.close()

    def isUserAllowed(self,ip):
        for block in self.chain:
            block : Block
            transaction = json.loads(block.transaction)
            if transaction["type"]==1:
                if transaction["ip"]==ip:
                    return True
        return False



import Networking