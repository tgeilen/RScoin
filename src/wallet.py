import web3
from ellipticCurve import EllipticCurve
from Crypto.Hash import keccak
import random
from ecpy.curves import Curve, Point
from txOutput import TxOutput
from smartContract import SmartContract
 


class Wallet:

    w3 = 0

    viewAccount = 0
    signAccount = 0

    publicViewKey = 0
    publicSignKey = 0

    privateViewKey = 0
    privateSignKey = 0


    #placeholder
    

    #G = None
    #H = None
    #cv = None

    G = EllipticCurve.G
    H = EllipticCurve.H
    cv = EllipticCurve.curve

    k = keccak.new(digest_bits=256)

    def __init__(self, w3:web3, privateViewKey:str, privateSignKey:str, smartContract:SmartContract) -> None:
        
        self.w3 = w3

        self.privateViewKey = int(privateViewKey,16)
        self.privateSignKey = int(privateSignKey,16)


        #not useful - it is necessary to use another hash function 
        #self.viewAccount = w3.eth.account.privateKeyToAccount(self.privateViewKey)
        #self.signAccount = w3.eth.account.privateKeyToAccount(self.privateSignKey)

        #self.publicViewKey = self.viewAccount.address
        #self.publicSignKey = self.signAccount.address

        self.publicViewKey = self.G.mul(self.privateViewKey)
        self.publicSignKey = self.G.mul(self.privateSignKey)



        G = EllipticCurve.G
        H = EllipticCurve.H
        cv = EllipticCurve.curve

        self.ownedOutputs = []

        

        self.smartContract = smartContract


 

    def createTransaction(self, receiverAmounts:dict):

        #dict {(RKV, RKS): amount}

        totalTransactionAmount = 0
        for key in receiverAmounts.keys():
            if(receiverAmounts[key] <= 0):
                receiverAmounts.pop(key)
            else:
                totalTransactionAmount += receiverAmounts[key]
        

        inputList = []
        sumOfUsedInputs = 0

        #get inputs that will be used in the transaction
        while(sumOfUsedInputs < totalTransactionAmount):
            input =  self.ownedOutputs.pop(0)
            sumOfUsedInputs += input["amount"]
            inputList.append(input)
        
        #add sender as receiver if inputs don't exactly equal totalTransactionAmount
        if(sumOfUsedInputs > totalTransactionAmount):
            keys = (self.getViewKey() , self.getSignKey())
            receiverAmounts[keys] = sumOfUsedInputs - totalTransactionAmount

        
        ##receivers and amounts have been checked and sender added to dict
        t = 0

        outputs = []

        r = EllipticCurve.randomInt256() #rG is transaction PubKey

        #create output address and amountCommitments
        for keys in receiverAmounts.keys():
            
            y = EllipticCurve.randomInt256()
            print("x"*31)
            print(keys)
            print(t)
            
            
            outputAddress = self.createOutputAdress(r=r,t=t,keys=keys)
            amountCommitment = self.createAmountCommitment(y=y, a=receiverAmounts[keys])

            outputInfo = {"outputAddress" : outputAddress,
                          "amountCommitment" : amountCommitment,
                          "r" : r,
                          "blindingFactor" : y,
                          "receiver" : keys,
                          "transactionIndex" : t}

            outputs.append(outputInfo)
            print(outputInfo)
            print("x"*31)
            t+=1
        
        #create pseudo commitments
        sumR = 0
        sumY = 0
        commitments = {}
        for input in inputList:
            if input != inputList[-1]:
                y = input["blindingFactor"]
                a = input["amount"]
                tmp = self.createPseudoCommitment(y=y,a=a)
                sumY += y
                sumR += tmp[1]
            
            #special case for last value
            else:
                y = input["blindingFactor"]
                a = input["amount"]
                sumY +=y
                tmp = self.createPseudoCommitment(y=y,a=a, sumR=sumR, sumY=sumY)
            
            commitments[frozenset(input)] = {
                "oAC" : input["amountCommitment"],
                "nAC" : tmp[0],
                "z"   : tmp[2]
                }
            
        v = 5 #number can be set to random value
        message = "Hello World"
        

        ringList = []
        mlsags = []
        for input in inputList:
            p = random.randint(0, v-1)
            i = 0
            ring = []
            fakeMembers = self.getFakeRingMembers(v=v)
            oAC = commitments[frozenset(input)]["oAC"]
            print("# of fake members: " + str(len(fakeMembers)))
            for member in fakeMembers:
                if (i==p) :
                    #add original input into ring at random postion p
                    nAC = commitments[frozenset(input)]["nAC"]
                    
                    diff = nAC.sub(oAC) 
                   
                    ring.append((input["outputAddress"],diff))
                    print("Added original input")

                #add fake members to ring
                nAC = member["amountCommitment"]
                
                diff = nAC.sub(oAC) 
                
                ring.append((member["address"],diff))
                i+=1
                
            ringList.append(ring)

            #hier input checken
            keyImage, k0 = self.createKeyImage(inputAdress=input["outputAddress"], r=input["r"], t=input["transactionIndex"])

            
            r = input["r"]
            t = input["transactionIndex"]

            #k0 = self.hash2Hex(self.point2String(self.publicViewKey.mul(r))+str(t)) + self.privateSignKey

            z = commitments[frozenset(input)]["z"]

            MLSAG = self.createMLSAG(message, ring, p, keyImage, k0, z)

            print("--------")
            for i in range(len(ring)):
                print(str(i) + ". og K1: " + str((ring[i][0])))
                print(str(i) + ". og K2: " + str((ring[i][1])))

            mlsags.append((MLSAG, keyImage, ring))

        ##START OF MLSAG


        return (message, mlsags)
       

    def createOutputAdress(self, r:int, t:int, keys:tuple)->Point:

        #Hash(r * RKV, t) * G + RKS | Monero 4.2.1

        hash = self.hash2Hex(self.point2String(keys[0].mul(r)) + str(t))
        
        
        return self.G.mul(hash).add(keys[1])

    def createInitalOutputAdress(self, r:int)->Point:
        #used to create new Outputs to this wallet
        #Hash(r * RKV, t) * G + RKS | Monero 4.2.1
        keys = (self.publicViewKey, self.publicSignKey)
        #print(str(r*keys[0]) + str(0))
        hash = self.hash2Hex(str(r*keys[0]) + str(0))
        
        
        return self.G.mul(hash).add(keys[1])


    def createAmountCommitment(self, y:int, a:int)->Point:
        # Commitment = y*G + a*H | Monero 5.3
        #y = random blinding factor
        #a = amount

        return self.G.mul(y).add(self.H.mul(a))

    def createPseudoCommitment(self, y:int, a:int, sumR:int = None, sumY:int = None )->Point:
        # Monero 5.4
        if sumR == None and sumR == None:
            r = EllipticCurve.randomInt256()
               
        else:
            #if last value, find r to create equal difference of sums
            r = sumY - sumR

        pseudoCommitment = self.G.mul(r).add(self.H.mul(a))
        z = y - r
        return(pseudoCommitment, r, z)



    def getFakeRingMembers(self, v:int)->list:
            #num of ring members

            #some smart contract read function

            #return list of v tuple (one-time address, amountCommitment)

            return self.smartContract.getRandomTx(v)

    def createKeyImage(self, r:int, t:int, inputAdress:Point):
        #r and t specified by input
        k0 = self.hash2Hex(
            self.point2String(
                self.publicViewKey.mul(r)
                ) + str(t)
                ) + self.privateSignKey
 
        inputAdressStr = self.point2String(inputAdress)
        return (self.hash2Point(inputAdressStr).mul(k0), k0)

    def createMLSAG(self, message:str, ring:list, p:int, keyImage:Point, k0:int, z:int)->list:

        alpha1 = EllipticCurve.randomInt256()
        alpha2 = EllipticCurve.randomInt256()

        r = {}
        for i in range(len(ring)):
            if i != p:
                tmp = [EllipticCurve.randomInt256(), EllipticCurve.randomInt256()]
                r[i] = tmp
                

        c = {}
        #print("_"*11)
        print("Ring length: " + str(len(ring)))
        #print(p)
        #print((ring[p][1]))

        tmp = (p+1) % len(ring)

        c[tmp] = self.hash2Hex(message
                + self.point2String(self.G.mul(alpha1))
                + self.point2String(ring[p][0]) 
                + self.point2String(self.G.mul(alpha2))
                + self.point2String(self.hash2Point(ring[p][1]).mul(alpha2))
        )
        print()
        print("P: " + str(p))
        print()

        print(str(tmp) + ". od C:  " + str(hex(c[tmp])))
        for i in range(len(ring)-1):

            #zu 100% wahrscheinlich nicht ganz richtig - viel Spaß bei debuggen :D
            j = (i+p+1) % len(ring)
            l = (j+1) % len(ring)

            #print(tmp)
            #print(j)
            #print(ring[j])
            #print("ring j 0 in wallet")
            #print(type(ring[j][0]))
            #print(ring[j][0])

            #testing only, kann gelöscht werden /TODO

            r1 = r[j][0]
            r2 = r[j][1] #changed ring[j][0] to ring[j][1] in last row of

            K1 = ring[j][0]
            K2 = ring[j][1]
            

            c[l] = self.hash2Hex(message
                + self.point2String(self.G.mul(r1).add((K1).mul(c[j])))
                + self.point2String((self.hash2Point(K1).mul(r1)).add(keyImage.mul(c[j])))
                + self.point2String(self.G.mul(r2).add((K2.mul(c[j]))))
                + self.point2String((self.hash2Point(K2).mul(r2))) #changed ring[j][0] to ring[j][1]
            )

            
            print(str(l) + ". od C:  " + str(hex(c[l])))



        ### hier ist ein fehler
        #r[p] = ((alpha1 - k0 * c[p]) % EllipticCurve.P, (alpha2 - z * c[p]) % EllipticCurve.P)        #og
        r[p] = ((alpha1 - k0 * c[p]) % EllipticCurve.P, (alpha2 - z * c[p]) % EllipticCurve.P)
        ### 
        
       
        
        
        print("--------")
        for i in range(len(c)):
            print(("  " if (i>p) else "") + str(i) + ". og C:  " + str(hex(c[i])))
            
                

        print("--------")
        for i in range(len(r)):
            print(str(i) + ". og R1: " + str(hex(r[i][0])))
            print(str(i) + ". og R2: " + str(hex(r[i][1])))
        
       
        signature = [hex(c[0])]
        for i in range(len(r)):
            for j in (0,1):
                signature.append(hex(r[i][j]))

        return tuple(signature)

        


    def recieveTx(self, tx: TxOutput, blindingFactor:int, amount: int, address:Point):

        transactionDetails = {"outputAddress" : address,
                          "amountCommitment" : tx.getAmountCommitment(),
                          "r" : tx.getRPubKey(),
                          "blindingFactor" : blindingFactor,
                          "amount": amount,
                          "transactionIndex" : tx.getTransactionIndex()
        }
        self.ownedOutputs.append(transactionDetails)

    def point2String(self, point:Point):
        return (str(point.x) + str(point.y))


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


    def getViewKey(self) -> Point:
        return self.publicViewKey

    def getSignKey(self) -> Point:
        return self.publicSignKey

    def getViewAccount(self):
        return self.viewAccount

    def getSignAccount(self):
        return self.signAccount