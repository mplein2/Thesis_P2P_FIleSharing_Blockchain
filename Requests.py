import json
class Request:
    def __init__(self,type):
        self.type = type

    def toJSON(self):
        return json.dumps(self.__dict__)

class JoinRequest(Request):
    def __init__(self,name,timestamp):
        super().__init__(1)
        self.name = name
        self.timestamp = timestamp
