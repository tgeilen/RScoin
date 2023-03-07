#import ecpy.curves as ECCurve
from Crypto.Hash import keccak
import random

from txOutput import TxOutput

import ellipticCurve


#print(ECCurve.Curve.get_curve_names())

#cv = ECCurve.Curve.get_curve('secp256k1')

k = keccak.new(digest_bits=256)
message = "test"
k.update(message.encode('UTF-8') )
print(int(k.hexdigest(),16))

r = random.getrandbits(256)
print(r)
print(type(r))


print(len([1,1,1,1]))

print(ellipticCurve.EllipticCurve.P)

p = 7
n = 10



for i in range(n-1):

    j = (i+p+1) % n 
    l = (j+1) % n

    print((i,j, l))

amount = 50
bf = ellipticCurve.EllipticCurve.randomInt256()
r = ellipticCurve.EllipticCurve.randomInt256()

txo = TxOutput(amount=amount, blindingFactor=bf, r=r)

print((random.getrandbits(256)))

""""
XY 
XY 
XY
XY
XY

c1 X Y X Y X Y X Y X Y



"""