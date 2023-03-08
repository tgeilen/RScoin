from txOutput import TxOutput
from ecpy.curves import Point
import random
from Crypto.Hash import keccak
from ellipticCurve import EllipticCurve


class SmartContract:

    G = EllipticCurve.G
    H = EllipticCurve.H
    cv = EllipticCurve.curve

    k = keccak.new(digest_bits=256)


    txOutpus = {}
    __addressList = []
    usedKeyImages = []

    def __init__(self) -> None:
       pass

    def addTx(self, tx:TxOutput, address:Point)->None:
        self.txOutpus[address] = tx
        self.__addressList.append(address)

    def getTx(self, address:Point)-> TxOutput:
        return self.txOutpus[address]

    def getRandomTx(self, n:int)->list:
        print(len(self.__addressList))
        result = []
        for i in range(n):
            address = random.choice(self.__addressList)
            amountCom = self.txOutpus[address].getAmountCommitment()
            result.append({"address":address, "amountCommitment":amountCom})
        return result
    
    def verifyTX(self, sig:tuple, message:str)->bool:

        #for item in sig:
        #    print(item[0])
        #    print(item[1])
        #    print(item[2])

        for i in range(len(sig)):
            keyImage = sig[i][1]
            ring = sig[i][2]
            c = {}
            c[0] = int(sig[i][0][0],16)
            l = 0
            r = []
            k = []


            #print(str(i+1) + " MLSAG: ")
            #print(range(0,len(sig[i][0])-3,2))
            for j in range(1,len(sig[i][0])-2,2):

                r1 = int(sig[i][0][j],16)
                r2 = int(sig[i][0][j+1],16)
                r.append((r1,r2))

                K1 = ring[l][0]
                K2 = ring[l][1]
                k.append((K1,K2))
                #print(j)
                #print(l)
                #print(ring[l])

                """
                print("Ich werde ausgeführt")
                print(j)
                print(l)
                print(c[l])

                print(ring[l][0])
                print(ring[l][1])
                """
                
                #print("k1 in smart c")
                #print(type(K1))
                #print(K1)


                c[l+1] = self.hash2Hex(message
                    + self.point2String(self.G.mul(r1).add((K1).mul(c[l])))
                    + self.point2String((self.hash2Point(K1).mul(r1)).add(keyImage.mul(c[l])))
                    + self.point2String(self.G.mul(r2).add((K2.mul(c[l]))))
                    #+ self.point2String((self.hash2Point(K2).mul(r2)))
                )

                l+=1

                

            j = len(sig[i][0])-2
            #print(j)
            r1 = int(sig[i][0][j],16)
            r2 = int(sig[i][0][j+1], 16)
            #print(ring)
            #print(len(ring))
            #print(l)
            K1 = ring[l][0]
            K2 = ring[l][1] #changed to 1 from 0
            r.append((r1,r2))
            k.append((K1,K2))
            
            calcC = self.hash2Hex(message
                    + self.point2String(self.G.mul(r1).add((K1).mul(c[l])))
                    + self.point2String((self.hash2Point(K1).mul(r1)).add(keyImage.mul(c[l])))
                    + self.point2String(self.G.mul(r2).add((K2.mul(c[l]))))
                    #+ self.point2String((self.hash2Point(K2).mul(r2)))
                )
            
            print()
            print("--------"*2)
            print()

            for key in c.keys():
                print(str(key) + ". sc C:  " + str(hex(c[key])))

            print("--------")

            for i in range(len(r)):
                print(str(i) + ". sc R1: " + str(hex(r[i][0])))
                print(str(i) + ". sc R2: " + str(hex(r[i][1])))
            print("--------")
            for i in range(len(k)):
                print(str(i) + ". sc K1: " + str((k[i][0])))
                print(str(i) + ". sc K2: " + str((k[i][1])))

        
            
            print()
            print(hex(calcC))
            print(hex(c[0]))

            if (calcC != c[0]):
                return False

                #print(str(j) + ": " + str(sig[i][0][j]))
            #print("KeyImage: " + str(sig[i][1]))
            #print()    

        return True







    def point2String(self, point:Point):
        return str(point)


    def hash(self, message:str)->str:  
        k = keccak.new(digest_bits=256)
        k.update(message.encode('UTF-8') )
        return k.hexdigest()

    def hash2Hex(self, message:str)->int:
        k = keccak.new(digest_bits=256)  
        k.update(message.encode('UTF-8') )
        return int(k.hexdigest(),16)

    def hash2Point(self, message:str) -> Point: 
        message = str(message)
        k = keccak.new(digest_bits=256) 
        k.update(message.encode('UTF-8') )
        return self.G.mul(int(k.hexdigest(),16))



    
    