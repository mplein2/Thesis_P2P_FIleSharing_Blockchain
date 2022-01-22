import p2pV2
import customRequests
userInput = input("Give Name of bundle:")
myrequest = customRequests.requestSearchBundle(userInput)
p2pV2.sendRequest('127.0.0.1', 6900, myrequest)
myrequest = customRequests.requestBundlePieces(userInput, 5)
p2pV2.sendRequest('127.0.0.1', 6900, myrequest)
