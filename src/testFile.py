#import ecpy.curves as ECCurve
from Crypto.Hash import keccak
import random
from  ellipticCurve import EllipticCurve
from ecpy.curves import Curve, Point

from txOutput import TxOutput

import ellipticCurve

from web3 import Web3

import json

def point2String(point:Point):
        return (str(point.x) + str(point.y)) 


'''web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

with open('src/abi.json', 'r') as f:
    contract_abi = json.load(f)

contract_address = '0x25677548F4e1C472aB7D2bFDFf9FbA0f5a5b28ad'

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

result = contract.functions.getInfo().call()

print(result)

#print(ECCurve.Curve.get_curve_names())

#cv = ECCurve.Curve.get_curve('secp256k1')

k = keccak.new(digest_bits=256)
message = str(11)
k.update(message.encode('UTF-8') )
print(int(k.hexdigest(),16))

r = random.getrandbits(256)
print(r)
print(type(r))


print(len([1,1,1,1]))

print(ellipticCurve.EllipticCurve.L)

p = 7
n = 10



for i in range(n-1):

    j = (i+p+1) % n 
    l = (j+1) % n

    print((i,j, l))

amount = 50
bf = ellipticCurve.EllipticCurve.randomInt256()
r = ellipticCurve.EllipticCurve.randomInt256()

#txo = TxOutput(amount=amount, blindingFactor=bf, r=r)

print((random.getrandbits(256)))

""""
XY 
XY 
XY
XY
XY

c1 X Y X Y X Y X Y X Y



"""
'''
print(-0xdf97fb4960e7e35bf0414e71cc08e4982a672e8af95e46caafd356d0f429471e1e37210b50724b5214e4b64d22b7f2b88a7cc8008b43ae430cf262edb62f2ce2 % EllipticCurve.L )

G3 = point2String(ellipticCurve.EllipticCurve.G.mul(3))
H3 = point2String(ellipticCurve.EllipticCurve.H.mul(3))

addT = point2String(ellipticCurve.EllipticCurve.G.mul(3).add(ellipticCurve.EllipticCurve.H.mul(3)))
print(G3)
print(H3)
print(addT)

for i in range(1,4):
        print(i)



