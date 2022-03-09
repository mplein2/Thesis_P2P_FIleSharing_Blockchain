from os import listdir
from os.path import isfile, join
import os

class BundleManager:
    def __init__(self):
        bundles = []
        pass

    def createBundle(self,path):
        bundle = Bundle(path)
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file = File(os.path.join(root, name))
        self.bundles.append(bundle)




class Bundle:
    def __init__(self,path):
        self.root = root
        self.files = []
    def addFile(self,file):
        self.files.append(file)


class File:
    def __init__(self,path):
        pass