import os


class Blockchain:
    #TODO how many signatures are required for an action to be valid among peers
    blockchain_difficulty = 2


    def __init__(self,path):
        self.BLOCKCHAIN_PATH = path
        if not os.path.exists(self.BLOCKCHAIN_PATH):
            #If Path dosent Exist Create it
            os.makedirs(self.BLOCKCHAIN_PATH)

        if os.path.exists(self.BLOCKCHAIN_PATH):
            self.unconfirmed_transactions = []
            self.chain = []

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)



class Block:
    def __init__(self):
        self.index = index
        self.transaction = transaction
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()