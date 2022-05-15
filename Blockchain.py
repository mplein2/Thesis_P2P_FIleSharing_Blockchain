import copy
import json
import math
import os
import threading
import time
from hashlib import sha256
from os import listdir
from pickle import dumps
from time import sleep

import rsa


class Block:
    def __init__(self, index, transaction, timestamp, previous_hash, signatures):
        self.index = index

        self.transaction = transaction

        self.timestamp = timestamp

        self.previous_hash = previous_hash

        self.signatures = signatures

    def computeHash(self):
        mycopy = copy.copy(self)
        del mycopy.signatures
        # print(mycopy.__dict__)
        if hasattr(mycopy, 'hash'):
            del mycopy.hash
        block_string = json.dumps(mycopy.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class UnconfirmedTransaction:
    def __init__(self, transaction, signatures=[]):
        self.transaction = transaction
        self.signatures = signatures


class GenesisTransaction:
    def __init__(self, ip, publicKey):
        # Type of Transaction
        self.type = 0
        self.ip = ip
        self.publicKey = publicKey


class InviteTransaction:
    def __init__(self, ip):
        self.type = 1
        self.ip = ip


class JoinTransaction:
    def __init__(self, ip, publicKey):
        # Type of Transaction
        self.type = 2
        self.ip = ip
        self.publicKey = publicKey


class BanTransaction:
    def __init__(self, ip):
        self.type = 3
        self.ip = ip


class UnbanTransaction:
    def __init__(self, ip):
        self.type = 4
        self.ip = ip


class AddAdminTransaction:
    def __init__(self, ip):
        self.type = 5
        self.ip = ip


class RemoveAdminTransaction:
    def __init__(self, ip):
        self.type = 6
        self.ip = ip


class Blockchain:
    def __init__(self, path, groupPeers, groupAdmins, groupId, client):
        self.BLOCKCHAIN_PATH = path
        self.TRANSACTION_PATH = self.BLOCKCHAIN_PATH + "\\Transactions\\"
        self.unconfirmed_transactions = []
        self.chain = []
        self.peers = groupPeers
        self.groupId = groupId
        self.groupAdmins = groupAdmins
        self.client = client
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
        miner = threading.Thread(target=self.mine, args=[client])
        miner.start()
        # print(self.unconfirmed_transactions)
        # for block in self.chain:
        #     print(block)

    def getDifficulty(self):
        # Diffuculty of blockchain will be dependent on the users participating in  --->log2(peers)
        if len(self.peers) == 0:
            return 1
        else:
            peers, bans, admins, owner = self.parseBlockchain()
            return math.floor(math.log2(len(peers)))

    def createGenesisBlock(self, client):
        transaction = GenesisTransaction(client.publicIP, client.publicKey.save_pkcs1(format='PEM').decode("utf-8"))
        transactionStr = json.dumps(transaction.__dict__)
        # this is string json format
        # print(transactionStr)
        # print(transactionStr.__class__)
        # Genereate signature for Transaction
        signature = rsa.sign(transactionStr.encode(), client.privateKey, 'SHA-1')
        genesis_block = Block(0, transactionStr, str(time.time()), "0", [client.publicIP, signature.hex()])
        genesis_block.hash = genesis_block.computeHash()
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

    def addNewTransaction(self, transaction: str):
        newUnconfirmedTransaction = UnconfirmedTransaction(transaction)
        self.unconfirmed_transactions.append(newUnconfirmedTransaction)
        self.saveUnconfirmedTransactions()

    def updateBlockchain(self, client):
        for peer in self.peers:
            # Dont send to self
            if peer[0] != client.publicIP:
                # For each peer ask their max index of blockchain
                updateBlockchainReq = Networking.UpdateBlockchainRequest(self.groupId)
                res = Networking.sendRequest(peer[0], 6700, dumps(updateBlockchainReq))
                if res is not False:
                    # if the response is bigger than me ask him for his block until we are at the same.
                    if res.answer > self.getLastBlockIndex():
                        # print(self.getLastBlockIndex().__class__, res.answer.__class__)
                        while self.getLastBlockIndex() < res.answer:
                            # Get block
                            getBlockReq = Networking.GetBlockRequest(self.groupId, self.getLastBlockIndex() + 1)
                            blockRes = Networking.sendRequest(peer[0], 6700, dumps(getBlockReq))
                            if blockRes is not False:
                                # print(f"Update BC Response:{blockRes}")
                                # print(blockRes.answer)
                                block = blockRes.answer
                                block: Block
                                # print(block.index, block.transaction, block.signatures, block.timestamp,
                                #       block.previous_hash, block.hash)
                                newBlock = Block(block.index, block.transaction, block.timestamp, block.previous_hash,
                                                 block.signatures)
                                newBlock.hash = block.hash
                                if self.validateNewBlock(newBlock):
                                    self.saveBlock(newBlock)
                                    self.chain.append(newBlock)
                            else:
                                break
                    else:
                        # print(id(self.peers))
                        peers, bans, admins, owner = self.parseBlockchain()
                        # self.peers = peers
                        # self.groupAdmins = admins
                        # print(id(self.peers))
                        # print("Blockchain Updated And Parsed")
                        # print("Up-to-date.")
                        pass

        # Update Group Peers And Admins
        peers, bans, admins, owner = self.parseBlockchain()
        for ip in admins:
            inside = False
            for admin in self.groupAdmins:
                if admin[0] == ip:
                    inside = True
            if not inside:
                self.groupAdmins.append([ip])

        for ip in peers:
            inside = False
            for peer in self.peers:
                if peer[0] == ip:
                    inside = True
            if not inside:
                self.peers.append([ip])

    def getBlockWithIndex(self, index):
        for block in self.chain:
            block: Block
            if block.index == index:
                return block
        return False

    def validateNewBlock(self, newBlock):
        """This function is for new blocks that come from peers returns true if blocks checks out."""
        newBlock: Block

        # If hash ok.
        if newBlock.computeHash() == newBlock.hash:
            # Validation for genesis block
            if newBlock.index == 0:
                if self.getLastBlockIndex() == -1:
                    # No other blocks accept it.
                    return True
                else:
                    return False
            else:
                # Check if new block is made with the same previous block.
                if newBlock.previous_hash == self.getLastBlock().computeHash():
                    # check difficulty based on blockchain etc.
                    if len(newBlock.signatures) >= self.getDifficulty():
                        signok = True
                        for sign in newBlock.signatures:
                            # print(f"Signature: {sign}")
                            signature = bytes.fromhex(sign[1])
                            print(sign[1])
                            key = rsa.PublicKey.load_pkcs1(self.getRSAKey(sign[0]))
                            # print(f"VERYFING BLOCK")
                            # print(newBlock.transaction)
                            # print(signature)
                            # print(key)
                            signok = True
                            try :
                                if rsa.verify(newBlock.transaction.encode(), signature, key) != 'SHA-1':
                                    signok = False
                            except Exception as e:
                                pass
                        if signok:
                            return True
                        else:
                            return False
                    else:
                        return False

    def mine(self, client):
        while True:
            # Update Blockchain.
            self.updateBlockchain(client)
            # print("Updating BLockchain")
            if not self.unconfirmed_transactions:
                # If No Transaction sleep and check again soon.
                sleep(120)
            else:
                diff = self.getDifficulty()
                # print(f"Blockchain Difficulty :{diff}")
                # print(f"Unconfirmed Transactions:{len(self.unconfirmed_transactions)}")
                for transaction in self.unconfirmed_transactions:
                    transaction: UnconfirmedTransaction
                    # For Each Transaction if signatures < difficulty collect transactions
                    if diff > len(transaction.signatures):
                        if not len(transaction.signatures):
                            # No Signatures add my signature
                            signature = rsa.sign(transaction.transaction.encode(), client.privateKey, 'SHA-1')
                            transaction.signatures.append([str(client.publicIP), signature.hex()])
                            self.saveUnconfirmedTransactions()
                        else:
                            # print("TRYING TO MINE FROM PEERS")
                            for peer in self.peers:
                                if peer[0] != client.publicIP:
                                    # print(f"Trying to get signatures from :{peer[0]}")
                                    # print(transaction.transaction)
                                    # Send Transaction get signature.
                                    signReq = Networking.GetSignatureRequest(self.groupId, self.getLastBlockIndex(),
                                                                             transaction.transaction)
                                    res = Networking.sendRequest(peer[0], 6700, dumps(signReq))
                                    if res is not False:
                                        if res.answer != 0 and res.answer != 1:
                                            # Verified.
                                            signature = bytes.fromhex(res.answer)
                                            key = rsa.PublicKey.load_pkcs1(self.getRSAKey(peer[0]))
                                            if rsa.verify(transaction.transaction.encode(), signature, key) == 'SHA-1':
                                                # Append the signature.
                                                # print(signature.hex().__class__)
                                                transaction.signatures.append([peer[0], signature.hex()])
                                                if diff > len(transaction.signatures):
                                                    # max signatures not reached
                                                    pass
                                                else:
                                                    # max signatures reached
                                                    break
                                    else:
                                        # Peer Dead Try From Others.
                                        print("No Response from", peer[0])
                                        pass

                            pass
                    else:
                        # We have the signatures number procede to make block and share.
                        # print(f"Signature {transaction} ready to be made block.")
                        # Bytes

                        lastBlock = self.getLastBlock()
                        # print(lastBlock)
                        lastBlock: Block
                        # print(f"Last Block Index :{lastBlock.index}")
                        newBlock = Block(lastBlock.index + 1, transaction.transaction, str(time.time()),
                                         lastBlock.computeHash(), transaction.signatures)
                        newBlock.hash = newBlock.computeHash()
                        self.unconfirmed_transactions.remove(transaction)
                        self.saveUnconfirmedTransactions()
                        self.saveBlock(newBlock)
                        self.chain.append(newBlock)
                        print(f"Block_{newBlock.index} mined.")
                sleep(30)

    def getLastBlock(self) -> Block:
        lastBlockIndex = self.chain[0].index
        # Find last Block and return it
        lastBlock = self.chain[0]
        for block in self.chain:
            # print(block.index)
            if block.index > lastBlockIndex:
                lastBlock = block
                lastBlockIndex = block.index
        return lastBlock

    def getRSAKey(self, ip):
        """Use only with peers in group so key always exists one way or another."""
        for block in self.chain:
            block: Block
            transaction = json.loads(block.transaction)
            if transaction["type"] == 0:
                if transaction["ip"] == ip:
                    return transaction["publicKey"]

            # From Invite
            elif transaction["type"] == 2:
                if transaction["ip"] == ip:
                    return transaction["publicKey"]

    def getLastBlockIndex(self):
        if len(self.chain) == 0:
            return -1
        else:
            lastBlockIndex = self.chain[0].index
            # Find last Block and return it
            lastBlock = self.chain[0]
            for block in self.chain:
                # print(block.index)
                if block.index > lastBlockIndex:
                    lastBlock = block
                    lastBlockIndex = block.index
            return lastBlock.index

    def saveUnconfirmedTransactions(self):
        # print(self.TRANSACTION_PATH)
        if not os.path.exists(self.TRANSACTION_PATH):
            # Create a new directory because it does not exist
            # print("Blockchain Folder")
            os.makedirs(self.TRANSACTION_PATH)
        json_file = open(self.TRANSACTION_PATH + "Transactions" + ".json", "w")
        json_file.write((json.dumps([ob.__dict__ for ob in self.unconfirmed_transactions])))
        json_file.close()

    def isUserAllowed(self, ip):
        for block in self.chain:
            block: Block
            transaction = json.loads(block.transaction)
            # From Create Genesis Block
            if transaction["type"] == 0:
                if transaction["ip"] == ip:
                    return True
            # From Invite
            if transaction["type"] == 1:
                if transaction["ip"] == ip:
                    return True
        # Didndt find user
        return False

    def getOwner(self):
        for block in self.chain:
            transaction = json.loads(block.transaction)
            if transaction["type"] == 0:
                return transaction["ip"]

    def parseBlockchain(self):
        """
        Parses Blockchain and returns 5 list of user types.
        Peers that are in the blockchain and allowed.
        Banned peers, Invites ,Admins and, Owner . All are lists.
        """
        peers = []
        bans = []
        admins = []
        invites = []
        owner = []

        for block in self.chain:
            transaction = json.loads(block.transaction)

            # GenesisTransactio
            if transaction["type"] == 0:

                owner.append(transaction["ip"])
                admins.append(transaction["ip"])
                peers.append(transaction["ip"])

            # InviteTransaction
            elif transaction["type"] == 1:
                invites.append(transaction["ip"])

            # JoinTransaction
            elif transaction["type"] == 2:
                peers.append(transaction["ip"])
                invites.remove(transaction["ip"])

            # BanTransaction
            elif transaction["type"] == 3:
                peers.remove(transaction["ip"])
                bans.append(transaction["ip"])

            # UnbanTransaction
            elif transaction["type"] == 4:
                bans.remove(transaction["ip"])

                # AddAdminTransaction
            elif transaction["type"] == 5:
                admins.append(transaction["ip"])

            # RemoveAdminTransaction
            elif transaction["type"] == 6:
                admins.remove(transaction["ip"])

        # print(f"Peers:{peers},Bans:{bans},Admins:{admins},Owners:{owner}")
        return peers, bans, admins, owner


import Networking
