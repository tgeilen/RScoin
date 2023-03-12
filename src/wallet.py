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

    def __init__(self, contract, privateViewKey:str, privateSignKey:str, smartContract:SmartContract) -> None:
        
        self.contract = contract

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
        publicOutputs = []

        r = EllipticCurve.randomInt256() #rG is transaction PubKey

        #create output address and amountCommitments

        sumOutputBF = 0
        for keys in receiverAmounts.keys():
            
            y = EllipticCurve.randomInt256()
            print("x"*31)
            print(keys)
            print(t)
            
            
            txAddress = self.createOutputAdress(r=r,t=t,keys=keys)
            amountCommitment = self.createAmountCommitment(y=y, a=receiverAmounts[keys])

            outputInfo = {"txAddress" : txAddress,
                          "amountCommitment" : amountCommitment,
                          "rPubKey" : r,
                          "blindingFactor" : y,
                          "receiver" : keys,
                          "transactionIndex" : t}
            
            publicOutput = {"txAddress" : txAddress,
                            "rPubKey" : r,
                            "amountCommitment" : amountCommitment,
                            "transactionIndex":t
            }

            outputs.append(outputInfo)
            publicOutputs.append(publicOutput)
            sumOutputBF += y
            t+=1
        
        #create pseudo commitments
        sumPseudoBF = 0
        sumY = 0
        commitments = {}
        for input in inputList:
            if input != inputList[-1]:
                ogBF = input["blindingFactor"]
                ogAmount = input["amount"]
                tmp = self.createPseudoCommitment(ogBF=ogBF,ogAmount=ogAmount)
                #sumY += y
                sumPseudoBF += tmp[1]
            
            #special case for last value to close loop
            else:
                ogBF = input["blindingFactor"]
                ogAmount = input["amount"]
                #sumY +=y
                tmp = self.createPseudoCommitment(ogBF=ogBF,ogAmount=ogAmount, sumPseudoBF=sumPseudoBF, sumOutputBF=sumOutputBF)
            
            commitments[frozenset(input)] = {
                "oAC" : input["amountCommitment"],
                "nAC" : tmp[0],
                "z"   : tmp[2]
                }
            
            print("Old AC: " + str((commitments[frozenset(input)]["oAC"])))
            print("New AC: " + str((commitments[frozenset(input)]["nAC"])))
            
        v = 1 #number can be set to random value / num of fake ring member
        
        

        ringList = []
        mlsags = []
        sendableMLSAGs = []
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
                    
                    diff = nAC.sub(oAC).neg()  #hier inverses damit es funktioniert - aktuell keine ahnung warum /TODO
                   
                    ring.append((input["txAddress"],diff))
                    print("Added original input")

                #add fake members to ring
                nAC = member["amountCommitment"]
                
                diff = nAC.sub(oAC) 
                
                ring.append((member["txAddress"],diff))
                i+=1
                
            ringList.append(ring)

            #hier input checken
            keyImage, k0 = self.createKeyImage(inputAdress=input["txAddress"], r=input["r"], t=input["transactionIndex"])


            message = str(self.hash2Hex(str(ringList)))
            
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

            sendableRing = []
            for point in ring:
                tmp = [self.point2Array(point[0]) , self.point2Array(point[1])]
                sendableRing.append(tmp)

            print("?"*90)
            print(MLSAG[1:])
            print("?"*90)

            for output in publicOutputs:
                output["amountCommitment"] = [output["amountCommitment"].x, output["amountCommitment"].y]
                output["txAddress"] = [output["txAddress"].x, output["txAddress"].y]

            sendableMLSAG = {"c1" : MLSAG[0],
                             "keyImage" : self.point2Array(keyImage),
                             "rFactors" : MLSAG[1:],
                             "inputs" : sendableRing
                             }
            
            sendableMLSAGs.append(sendableMLSAG)


            

        ##START OF MLSAG


        return (message, mlsags, publicOutputs, sendableMLSAGs)
       

    def createOutputAdress(self, r:int, t:int, keys:tuple)->Point:

        #Hash(r * RKV, t) * G + RKS | Monero 4.2.1

        hash = self.hash2Hex(self.point2String(keys[0].mul(r)) + str(t))
        
        
        return self.G.mul(hash).add(keys[1])

    def createInitalOutputAdress(self, r:int, t:int)->Point:
        #used to create new Outputs to this wallet
        #Hash(r * RKV, t) * G + RKS | Monero 4.2.1
        keys = (self.publicViewKey, self.publicSignKey)
        #print(str(r*keys[0]) + str(0))
        hash = self.hash2Hex(self.point2String((keys[0].mul(r))) + str(t))

        k0 = self.hash2Hex(self.point2String(self.publicViewKey.mul(r)) + str(t)) + self.privateSignKey
        
        print("address in creation:")
        print(self.G.mul(hash).add(keys[1]))
        print("r in creation:")
        print(hex(r))
        print("k0 in creation:")
        print(hex(k0))
        print("t in creation")
        print(t)
        
        
        print(hex(k0))
        #print(hex(hash))

        print("self.G.mul(k0) in creation")
        print(self.G.mul(k0))                    #sind beide gleich
        print("self.G.mul(hash).add(keys[1]) in creation")
        print(self.G.mul(hash).add(keys[1]))   #sind beide gleich


        return self.G.mul(hash).add(keys[1])


    def createAmountCommitment(self, y:int, a:int)->Point:
        # Commitment = y*G + a*H | Monero 5.3
        #y = random blinding factor
        #a = amount

        return self.G.mul(y).add(self.H.mul(a))

    def createPseudoCommitment(self, ogBF:int, ogAmount:int, sumPseudoBF:int = None, sumOutputBF:int = None )->Point:
        # Monero 5.4
        if sumPseudoBF == None and sumOutputBF == None:
            pseudoBF = EllipticCurve.randomInt256()
               
        else:
            #if last value, find r to create equal difference of sums
            pseudoBF = sumOutputBF - sumPseudoBF

        pseudoCommitment = self.G.mul(pseudoBF).add(self.H.mul(ogAmount))
        z = ogBF - pseudoBF
        return(pseudoCommitment, pseudoBF, z)

    def getFakeRingMembers(self, v:int)->list:
            #num of ring members

            #some smart contract read function

            #return list of v tuple (one-time address, amountCommitment)

            allTxoutputs = self.contract.functions.getTXoutputs().call()
            result = []
            for i in range(v):
                output = random.choice(allTxoutputs)
                result.append({
                    "rPubKey" : output[0],
                    "amountCommitment" : Point(output[1][0],output[1][1],self.cv),
                    "transactionIndex":output[2],
                    "txAddress": Point(output[3][0],output[3][1],self.cv)
                })

            return result
            #return self.smartContract.getRandomTx(v)

    def createKeyImage(self, r:int, t:int, inputAdress:Point):
        #r and t specified by input
        k0 = self.hash2Hex(
                self.point2String(self.publicViewKey.mul(r)) + str(t)
                ) + self.privateSignKey
 
        inputAdressStr = self.point2String(inputAdress)         #checken warum erst zu string??
        keyImage = self.hash2Point(inputAdressStr).mul(k0)            #anders als monero, aber so bessere ergebnisse
        #keyImage = inputAdress.mul(k0)
        K2 = inputAdress.mul(k0)

        #########
        #Testing

        ktest = k0 - self.privateSignKey


        print("W"*70)
        print("r in keyImage:")
        print(hex(r))
        print("k0 in keyImage:")
        
        print(hex(k0))

        
        '''print("t")
        print(t)
        print("hex(k0)")
        print(hex(k0))
        print("K")
        print(K)
        print("K2")
        print(K2)'''
        print("inputAdress")
        print(inputAdress)
        print("self.G.mul(k0)")
        print(self.G.mul(k0))





        #########
        return (keyImage, k0)

    def createMLSAG(self, message:str, ring:list, p:int, keyImage:Point, k0:int, z:int)->list:

        #z = -z
        #z = z % EllipticCurve.P
    

        alpha1 = EllipticCurve.randomInt256()
        alpha2 = EllipticCurve.randomInt256()

        r = {}
        for i in range(len(ring)):
            if i != p:
                r[i] = [EllipticCurve.randomInt256(), EllipticCurve.randomInt256()]
                
                

        c = {}
        #print("_"*11)
        print("Ring length: " + str(len(ring)))
        #print(p)
        #print((ring[p][1]))

        tmp = (p+1) % len(ring)

        c[tmp] = self.hash2Hex(message
                + self.point2String(self.G.mul(alpha1))
                + self.point2String(self.hash2Point(ring[p][0]).mul(alpha1))
                + self.point2String(self.G.mul(alpha2))
                #+ self.point2String(self.hash2Point(ring[p][1]).mul(alpha2))
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

            

            r1 = r[j][0]
            r2 = r[j][1] #changed ring[j][0] to ring[j][1] in last row of

            K1 = ring[j][0]
            K2 = ring[j][1]
            

            c[l] = self.hash2Hex(message
                + self.point2String(self.G.mul(r1).add((K1).mul(c[j])))
                + self.point2String((self.hash2Point(K1).mul(r1)).add(keyImage.mul(c[j])))
                + self.point2String(self.G.mul(r2).add((K2.mul(c[j]))))
                #+ self.point2String((self.hash2Point(K2).mul(r2))) 
            )

            
            print(str(l) + ". od C:  " + str(hex(c[l])))



        ### hier ist ein fehler
        r[p] = ((alpha1 - k0 * c[p]) % (EllipticCurve.L), (alpha2 - z * c[p]) % (EllipticCurve.L))        #og
        #r[p] = ((alpha1 - (k0 * c[p])), (alpha2 - c[p] * z))
        ### 

        r1 = r[p][0]
        r2 = r[p][1]

        K1 = self.G.mul(k0)
        K2 = self.H.mul(z)


        #hier morgen mittwoch weitermachen
        #fehler bei der subtraktion großer hex zahlen
        # 1&2, 3&4 identisch

        print("--------")
        print("alpha1")
        print("Formel 1")
        print("--")
        print(self.G.mul(r1).add(ring[p][0].mul(c[p])))
        print(self.G.mul((alpha1 - (c[p] * k0))).add(ring[p][0].mul(c[p])))
        print(self.G.mul(alpha1).sub(self.G.mul(c[p] * k0)).add(ring[p][0].mul(c[p])))
        print(self.G.mul(alpha1))
        print("--")
        print(self.G.mul(c[p] * k0).sub(ring[p][0].mul(c[p])))
        #print(self.G.mul((-1 * c[p] * k0)%EllipticCurve.P).add(ring[p][0].mul(c[p])))
        print("--")
        print(self.G.mul(k0)) #k0 * G = K
        print(ring[p][0]) # = K 
        print("--------")
        print("Formel 2")
        print("--")
        print(self.hash2Point(ring[p][0]).mul(r1).add(keyImage.mul(c[p])))
        print(self.hash2Point(ring[p][0]).mul(alpha1 - (c[p] * k0)).add(keyImage.mul(c[p])))
        print(self.hash2Point(ring[p][0]).mul(alpha1))
        print("--")
        print(keyImage.mul(c[p]))                           #keyImage == hash2Point(ring[p][0]).mul(k0)
        print(self.hash2Point(ring[p][0]).mul(k0 * c[p]))
        print(self.hash2Point(ring[p][0]).mul(k0).mul(c[p]))
        print(keyImage.sub(self.hash2Point(ring[p][0]).mul(k0)))
        print(keyImage.mul(c[p]).sub(self.hash2Point(ring[p][0]).mul(k0 * c[p])))
        print("--")
        print(keyImage)
        print(self.hash2Point(ring[p][0]).mul(k0))

        print("--------")

        print("1 "  + str(hex(z)))
        print("2 "  + str(self.G.mul(z)))
        print("3 "  + str(ring[p][1]))
        print("--")
        print("4 "  + str(self.G.mul(c[p] * z)))
        print("5 "  + str(self.G.mul(z).mul(c[p])))
        print("6 "  + str(ring[p][1].mul(c[p])))

        

        print("--------")
        print("alpha2")
        print("Formel 1")
        print("--")
        print("1 "  + str(self.G.mul(r2).add(ring[p][1].mul(c[p]))))
        print("2 "  + str(self.G.mul((alpha2 - (c[p] * z))).add(ring[p][1].mul(c[p]))))
        print("3 "  + str(self.G.mul(alpha2).sub(self.G.mul(c[p] * z)).add(ring[p][1].mul(c[p]))))
        print("4 "  + str(self.G.mul(alpha2)))
        print("--")
        print("5 "  + str(self.G.mul(c[p] * z).sub(ring[p][1].mul(c[p]))))
        print("6 "  + str(self.G.mul(z).sub(ring[p][1])))
        print("--")
        #print(self.G.mul((-1 * c[p] * z)%EllipticCurve.P).add(ring[p][1].mul(c[p])))
        print("7 "  + str(self.G.mul(z))) #k0 * G = K
        print("8 "  + str(ring[p][1])) # = K 
        print("--------")
        '''print("Formel 2")
        print("--")
        print(self.hash2Point(ring[p][1]).mul(r2))
        print(self.hash2Point(ring[p][1]).mul(alpha2 - (c[p] * z)))
        print(self.hash2Point(ring[p][1]).mul(alpha2))
        print("--")
        print(z)
        print(self.hash2Point(ring[p][1]).mul(z))
        '''
        

        
        '''print(hex(alpha1))
        print(hex(k0))
        print(hex(c[p]))
        print(hex(alpha1 - c[p] * k0))
        print(hex((alpha1 - c[p] * k0) % EllipticCurve.P))'''


        print("--------")
        for i in range(len(c)):
            print(("  " if (i>p) else "") + str(i) + ". og C:  " + str(hex(c[i])))
            
                

        print("--------")
        for i in range(len(r)):
            print(str(i) + ". og R1: " + str(hex(r[i][0])))
            print(str(i) + ". og R2: " + str(hex(r[i][1])))
        
       
        signature = [int(c[0])]
        for i in range(len(r)):
            for j in (0,1):
                signature.append(int(r[i][j]))

        return signature

        


    def receiveTx(self, tx: TxOutput, blindingFactor:int, amount: int, txAddress:Point):
        print("adress in receive:")
        print(txAddress)
        transactionDetails = {"txAddress" : txAddress,
                          "amountCommitment" : tx.getAmountCommitment(),
                          "r" : tx.getRPubKey(),
                          "blindingFactor" : blindingFactor,
                          "amount": amount,
                          "transactionIndex" : tx.getTransactionIndex()
        }
        self.ownedOutputs.append(transactionDetails)

    
    def point2Array(self, point:Point):
        return [point.x,point.y]
    
    def point2String(self, point:Point):
        return (str(point.x) + str(point.y)) 


    def hash(self, message:str)->str:  
        k = keccak.new(digest_bits=256)
        k.update(message.encode('UTF-8') )
        return k.hexdigest()

    def hash2Hex(self, message:str)->int:
        k = keccak.new(digest_bits=256)  
        k.update(message.encode('UTF-8') )
        return int(k.hexdigest(),16) % EllipticCurve.L

    def hash2Point(self, message:str) -> Point: 
        if(type(message) == Point):
            message = self.point2String(message)
        else:
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