from os import listdir
from os.path import isfile, join
import os
import json
from functools import partial
import hashlib
import time
class BundleManager:
    def __init__(self):
        self.bundles = []

    def createBundle(self,name,desc,path):
        bundle = Bundle(name,desc,path=path)
        self.bundles.append(bundle)
        return bundle

class Bundle:
    def __init__(self,name,desc,id=None,timestamp=None,root=None,pieceSize=49152,files=[],path=None):
        if path is None:
            #Load From File
            self.name=name
            self.description=desc
            self.id = id
            self.timestamp = time
            self.root = root
            self.pieceSize = pieceSize
            self.files = files
        else:
            #Create
            self.name=name
            self.description=desc
            self.root = path
            self.timestamp = time.time()
            self.id =  self.id = hashlib.sha256((name+desc+str(self.timestamp)).encode('utf-8')).hexdigest()
            self.pieceSize = 49152
            self.files = []
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    #For Each file found
                    print(root,name)
                    print(os.path.join(root, name))
                    pieceCounter = 0
                    file = {"path": os.path.join(root, name).replace(path,'')}
                    pieces = []
                    with open(os.path.join(root, name), 'rb') as openfileobject:
                        for chunk in iter(partial(openfileobject.read, 49152), b''):
                            pieces.append([pieceCounter,hashlib.sha1(chunk).hexdigest()])
                            pieceCounter = pieceCounter + 1
                    file["pieces"]=pieces
                    self.files.append(file)

    def toJSON(self):
        return self.__dict__



