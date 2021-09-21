import rsa

# https://stuvel.eu/python-rsa-doc/usage.html
a = (pubkey, privkey) = rsa.newkeys(512)
print(a)