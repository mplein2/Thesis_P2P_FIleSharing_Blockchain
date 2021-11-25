import rsa

# https://stuvel.eu/python-rsa-doc/usage.html
# https://stuvel.eu/python-rsa-doc/usage.html
a = pubkey, privkey = rsa.newkeys(256)

message = "Test".encode("utf8")
print(message)
crypto = rsa.encrypt(message, pubkey)
print(crypto)
message = rsa.decrypt(crypto, privkey)
print(message.decode('utf8'))