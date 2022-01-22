import json


class request:
    def __init__(self, requestType):
        self.requestType = requestType

    def toJSON(self):
        return json.dumps(self.__dict__)


# Search for a bundle name.
class requestSearchBundle(request):
    def __init__(self, bundleName):
        super().__init__(1)
        self.bundleName = bundleName



class requestBundlePieces(request):
    def __init__(self, bundleName, pieces):
        super().__init__(2)
        self.bundleName = bundleName

