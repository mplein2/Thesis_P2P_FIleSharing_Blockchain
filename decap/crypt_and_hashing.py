import rsa
import base64
# https://stuvel.eu/python-rsa-doc/usage.html
peer1pub, peer1prv = rsa.newkeys(512)
peer2pub, peer2prv = rsa.newkeys(512)
peer3pub, peer3prv = rsa.newkeys(512)

message = "Verify".encode("utf8")

crypto = rsa.encrypt(message, peer1pub)
# print(crypto)
message = rsa.decrypt(crypto, peer1prv)
# print(message.decode('utf8'))


hash = rsa.compute_hash(message, 'SHA-1')

peer1signature = rsa.sign_hash(hash, peer1prv, 'SHA-1')
peer2signature = rsa.sign_hash(hash, peer2prv, 'SHA-1')
peer3signature = rsa.sign_hash(hash, peer3prv, 'SHA-1')
print(peer3signature.encode())

# print(rsa.verify(message, peer1signature, peer1pub))
# print(rsa.verify(message, peer2signature, peer2pub))
#
# message = 'Go right at the blue tree'.encode()
# rsa.verify(message, signature, pubkey)
