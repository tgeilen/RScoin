from ellipticCurve import EllipticCurve
from ecpy.curves import  Point


class TxOutput:

    def __init__(self, rPubKey:int, amountCommitment:int, transactionIndex:int, address:Point) -> None:
        self.rPubKey =  rPubKey
        self.amountCommitement = amountCommitment
        self.transactionIndex =  transactionIndex
        self.address = address
        

    def __init__(self, amount:int, blindingFactor:int, rPubkey:int, transactionIndex:int, address:Point) -> None:
        #print("___ CREATING FAKE TXOUTPUT ___")
        self.amountCommitement =  EllipticCurve.G.mul(blindingFactor).add(EllipticCurve.H.mul(amount))
        self.rPubKey = rPubkey
        self.transactionIndex = transactionIndex
        self.address = address



    def getAmountCommitment(self)->Point:
        return self.amountCommitement
    
    def getAmmountCommitmentArray(self)->list:
        return [self.amountCommitement.x, self.amountCommitement.y]

    def getRPubKey(self)->int:
        return self.rPubKey

    def getTransactionIndex(self)->int:
        return self.transactionIndex

    