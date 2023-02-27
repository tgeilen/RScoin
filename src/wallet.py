import web3
from ellipticCurve import EllipticCurve
from Crypto.Hash import keccak
import random
from ecpy.curves import Curve, Point
 


class Wallet:

    w3 = 0

    viewAccount = 0
    signAccount = 0

    publicViewKey = 0
    publicSignKey = 0

    privateViewKey = 0
    privateSignKey = 0


    #placeholder
    ownedOutputs = [{"outputAddress" : "outputAddress",
                          "amountCommitment" : "amountCommitment",
                          "r" : "rFromTransactionData",
                          "y" : "yToldBySender",
                          "amount": "amountToldBySender"
    }]

    #G = None
    #H = None
    #cv = None

    G = EllipticCurve.G
    H = EllipticCurve.H
    cv = EllipticCurve.curve

    k = None

    def __init__(self, w3:web3, privateViewKey, privateSignKey) -> None:
        
        self.w3 = w3

        self.privateViewKey = privateViewKey
        self.privateSignKey = privateSignKey


        #not useful - it is necessary to use another hash function 
        #self.viewAccount = w3.eth.account.privateKeyToAccount(self.privateViewKey)
        #self.signAccount = w3.eth.account.privateKeyToAccount(self.privateSignKey)

        #self.publicViewKey = self.viewAccount.address
        #self.publicSignKey = self.signAccount.address

        self.publicViewKey = self.G.mul(privateViewKey)
        self.publicSignKey = self.G.mul(privateSignKey)



        G = EllipticCurve.G
        H = EllipticCurve.H
        cv = EllipticCurve.curve

        k = keccak.new(digest_bits=256)
 

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
            receiverAmounts[self.publicViewKey] = sumOfUsedInputs - totalTransactionAmount

        
        ##receivers and amounts have been checked and sender added to dict
        t = 0

        outputs = []

        #create output address and amountCommitments
        for keys in receiverAmounts.keys():
            r = random.getrandbits(256)
            y = random.getrandbits(256)
            outputAddress = self.createOutputAdress(r=r,t=t,keys=keys)
            amountCommitment = self.createAmountCommitment(y=y, a=receiverAmounts[keys])

            outputInfo = {"outputAddress" : outputAddress,
                          "amountCommitment" : amountCommitment,
                          "r" : r,
                          "y" : y,
                          "receiver" : keys}

            outputs.append(outputInfo)
            t+=1
        
        #create pseudo commitments
        sumR = 0
        sumY = 0
        commitments = {}
        for input in inputList:
            if input != inputList[-1]:
                y = input["y"]
                a = input["amount"]
                tmp = self.createPseudoCommitment(y=y,a=a)
                sumY += y
                sumR += tmp[1]
            
            #special case for last value
            else:
                y = input["y"]
                a = input["amount"]
                tmp = self.createPseudoCommitment(y=y,a=a, sumR=sumR, sumY=sumY)
            
            commitments[input] = {
                "oAC" : input["amountCommitment"],
                "nAC" : tmp[0],
                "z"   : tmp[2]
                }
            
        v = 2 #number can be set to random value
        

        ringList = []
        p = random.randint(0, v)
        for input in inputList:
            i = 0
            ring = []
            fakeMembers = self.getFakeRingMembers(v=v)
            oAC = commitments[input]["oAC"]
            for member in fakeMembers:
                if(i==p):
                    #add original input into ring as random postion p
                    nAC = commitments[input]["nAC"]
                    ################
                    diff = EllipticCurve.G.add(nAC).sub(oAC).sub(EllipticCurve.G) #TODO sehr unschön, muss auch anders gehen
                    ################
                    ring.append((input["outputAddress"],diff))

                #add fake members to ring
                nAC = commitments[member]["amountCommitment"]
                ################
                diff = EllipticCurve.G.add(nAC).sub(oAC).sub(EllipticCurve.G) #TODO sehr unschön, muss auch anders gehen
                ################
                ring.append((member["outputAddress"],diff))
                
            ringList.append(ring)



        

        return True

    def createOutputAdress(self, r:int, t:int, keys:tuple)->Point:

        #Hash(r * RKV, t) * G + RKS | Monero 4.2.1

        hexHash = self.hash(str(r*keys[0]) + str(t))
        hashBase10 = int(hexHash,16)
        
        return self.G.mul(hashBase10).add(keys[1])


    def createAmountCommitment(self, y:int, a:int)->Point:
        # Commitment = y*G + a*H | Monero 5.3
        #y = random blinding factor
        #a = amount

        return self.G.mul(y).add(self.H.mul(a))

    def createPseudoCommitment(self, y:int, a:int, sumR:int = None, sumY:int = None )->Point:
        # Monero 5.4
        if sumR == None and sumR == None:
            r = random.getrandbits(256)
               
        else:
            #if last value, find r to create equal difference of sums
            r = sum(sumY) - sum(sumR)

        pseudoCommitment = self.G.mul(r).add(self.H.mul(a))
        z = y - r
        return(pseudoCommitment, r, z)



    def getFakeRingMembers(self, v:int):
            #num of ring members

            #some smart contract read function

            #return list of v tuple (one-time address, amountCommitment)

            return None




    def hash(self, message:str):  
        self.k.update(message.encode('UTF-8') )
        return self.k.hexdigest()


    def getViewKey(self):
        return self.publicViewKey

    def getSignKey(self):
        return self.publicSignKey

    def getViewAccount(self):
        return self.viewAccount

    def getSignAccount(self):
        return self.signAccount