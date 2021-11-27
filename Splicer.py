import hashlib
import os
import json
import time
from json import JSONEncoder

# Size Constants


SPLICE_1K = 1024
SPLICE_2K = 2048
SPLICE_4K = 4096
SPLICE_8K = 8192
SPLICE_16K = 16384
SPLICE_32K = 32768
SPLICE_64K = 65536


class FileEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Bundle:
    def __init__(self, bundleName, startDirectory, fragmentSize):
        self.bundleName = bundleName
        # TODO dynamic when sharing a bundle
        self.owner = "8.8.8.8"
        self.timestamp = time.time()
        self.startDirectory = startDirectory
        self.fragmentSize = fragmentSize
        self.files = []
        self.parse()
        self.createJSON()

    def parse(self):
        for (root, dirs, files) in os.walk(self.startDirectory, topdown=True):
            for x in files:
                self.files.append(File(x, root, self.fragmentSize))

    def toJSON(self):
        del self.startDirectory
        return json.dumps(self.__dict__, indent=4, cls=FileEncoder)

    def createJSON(self):
        JSONFileName = self.bundleName + ".json"
        jsonFile = open(JSONFileName, "w")
        jsonFile.write(self.toJSON())
        jsonFile.close()


class File:
    def __init__(self, fileName, directory, fragmentSize):
        self.fileName = fileName
        if len(directory.split('\\')) > 1:
            dir = directory.split('\\')
            dir.pop(0)
            self.directory = '/'.join(dir)
        else:
            self.directory = "/"
        self.hash = 0
        f = open(directory + "/" + fileName, "rb")
        file = f.read(fragmentSize)
        f.close()
        self.hash = hashlib.sha1(file).hexdigest()
        self.slices = []
        with open(directory + "/" + fileName, "rb") as f:
            count = 0
            while True:
                data = f.read(fragmentSize)
                if not data:
                    break
                self.slices.append((count, hashlib.sha1(data).hexdigest()))
                count = count + 1


def main():
    Bundle("TestBundle", "C:/Users/Ftoy/Desktop/bundleTesting", SPLICE_64K)


if __name__ == '__main__':
    main()
