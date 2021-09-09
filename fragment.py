# File for the class of the file fragment
import base64
import json


class Fragment:
    # Fragment variables
    def __init__(self, fileName, fileFragment, fragmentSize):
        self.fileName = fileName
        self.fileFragment = fileFragment
        f = open(fileName, "rb")
        f.seek(fileFragment * fragmentSize)
        self.fragmentContent = base64.b64encode(f.read(fragmentSize)).decode()
        f.close()
        self.fragmentSize = fragmentSize

    def toJSON(self):
        return json.dumps(self.__dict__)
