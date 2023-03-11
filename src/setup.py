from web3 import Web3
from accounts import Accounts
from wallet import Wallet
from ellipticCurve import EllipticCurve
from txOutput import TxOutput
from smartContract import SmartContract
import os
import json

#connect to local blockchain
#w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:7545'))
w3 = None

#create set of test accounts
sc = SmartContract()
accounts = Accounts(w3, sc)
wallet1 = accounts.getWallet(0)
wallet2 = accounts.getWallet(1)
wallet3 = accounts.getWallet(2)

sc = SmartContract()

listR = []
listBF = []


for i in range(10):
    r = EllipticCurve.randomInt256()
    bf = EllipticCurve.randomInt256()
    tmpAddress = wallet2.createInitalOutputAdress(r,i)
    tx = TxOutput(10,bf,r, i, tmpAddress)
    sc.addTx(tx, tmpAddress)
    listR.append(r)
    listBF.append(bf)

os.system("clear")

amount = 10

for i in range(10):
    bf = EllipticCurve.randomInt256()
    r = EllipticCurve.randomInt256()
    address = wallet1.createInitalOutputAdress(r,i)
    print("Adress in Setup:")
    print(address)
    
    txo = TxOutput(amount=amount, blindingFactor=bf, rPubkey=r, transactionIndex=i, address = address)

    wallet1.receiveTx(txo, bf, amount,address)

os.system("clear")

receivers = {(wallet3.getViewKey(), wallet3.getSignKey()): 10}


message , sig, outputs , sMLSAGS = (wallet1.createTransaction(receivers))

'''
for i in range(len(sig)):
    print(str(i+1) + " MLSAG: ")
    for j in range(len(sig[i][0])):
        print(str(j) + ": " + str(sig[i][0][j]))
    print("KeyImage: " + str(sig[i][1]))
    print()

'''

print(sc.verifyTX(sig, message))


web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545', request_kwargs={'timeout': 600}))

with open('src/abi.json', 'r') as f:
    contract_abi = json.load(f)

contract_address = '0x4A8f937dfdCAd6393037714E512771917cEbcDC8'

sender_adress = "0x74cb53366c85F4b1ccFB61f6E25aA79cd6468782"

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

result = contract.functions.getInfo().call()

print(result)

#result = contract.functions.receiveTransaction(int(message,16), tuple(sMLSAGS[0]), tuple(outputs[0])).transact()
print(result)

result = contract.functions.returnNum((16)).call()

print(sMLSAGS)

print(result)

result = contract.functions.returnArr((1,2)).call()

print(result)

result = contract.functions.returnStruct({"test":(1,2)})

print(result)

print(sMLSAGS[0]["rFactors"])


'''result = contract.functions.receiveTransaction(
    int(message), 
    sMLSAGS[0]["c1"],
    sMLSAGS[0]["keyImage"],
    sMLSAGS[0]["rFactors"],
    sMLSAGS[0]["inputs"],
    0,
    [1,2],
    1
    ).call()
print (result)'''


"""tx_hash = contract.functions.receiveTransaction(
    int(message),  
    1,
    sMLSAGS[0]["keyImage"],
    sMLSAGS[0]["rFactors"],
    sMLSAGS[0]["inputs"],
    0,
    [1,2],
    1
    ).transact({'from': sender_adress})"""

tx_hash = contract.functions.receiveTransaction(
    int(message), 
    sMLSAGS[0]["c1"],
    sMLSAGS[0]["keyImage"],
    sMLSAGS[0]["rFactors"],
    sMLSAGS[0]["inputs"],
    0,
    [1,2],
    1
    ).transact({'from': sender_adress})

tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print(tx_receipt)

result = contract.functions.returnKeyImage().call()

print(result)



