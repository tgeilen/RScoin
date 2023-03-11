from ecpy.curves import Curve, Point
import random
from eccPoint import eccPoint


class EllipticCurve:

    #initalize curve
    curve = Curve.get_curve("secp256k1")

    #taken from ecpy test in curves.py (maybe double check)
    G = Point(0x6fb13b7e8ab1c7d191d16197c1bf7f8dc7992412e1266155b3fb3ac8b30f3ed8,
            0x2e1eb77bd89505113819600b395e0475d102c4788a3280a583d9d82625ed8533,
            curve)
    H = Point(0x07cd9ee748a0b26773d9d29361f75594964106d13e1cad67cfe2df503ee3e90e,
            0xd209f7c16cdb6d3559bea88c7d920f8ff077406c615da8adfecdeef604cb40a6,
            curve)

    L = int(0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141)

    


    def randomInt256():
        return random.getrandbits(256) % EllipticCurve.L

    def getG(self):
        return self.G

    def getH(self):
        return self.H