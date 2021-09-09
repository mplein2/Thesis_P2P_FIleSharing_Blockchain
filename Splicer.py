import hashlib
import json


class Splice:
    # Fragment variables
    def __init__(self, fileName, fragmentSize):
        self.fileName = fileName
        self.fragmentSize = fragmentSize
        self.fragmentHashes = []

    def addFragment(self, fragmentHash):
        self.fragmentHashes.append(fragmentHash)

    def toJSON(self):
        return json.dumps(self.__dict__)


def SpliceFile(fileName, fragmentSize):
    s = Splice(fileName, fragmentSize)
    f = open(fileName, "rb")
    Status = True
    fragmentNumber = 0
    while Status:
        fragmentContent = f.read(fragmentSize)
        if fragmentContent == b'':
            Status = False
            continue
        else:
            s.addFragment((fragmentNumber, hashlib.sha1(fragmentContent).hexdigest()))
            fragmentNumber = fragmentNumber + 1
    # Finished With Hashing
    # Create JSON file
    # Split File Name From Extension
    JSONFileName = s.fileName.split('.')[0] + ".json"
    print(JSONFileName)
    jsonFile = open(JSONFileName, "w")
    print(s.fragmentHashes)
    jsonFile.write(s.toJSON())
    jsonFile.close()


def main():
    SpliceFile("Test1.jpg", 4096)


if __name__ == '__main__':
    main()
