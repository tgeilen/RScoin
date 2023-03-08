import web3
from accounts import Accounts
from wallet import Wallet
from ellipticCurve import EllipticCurve
from txOutput import TxOutput
from smartContract import SmartContract
import os

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

amount = 3

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


message , sig = (wallet1.createTransaction(receivers))

'''
for i in range(len(sig)):
    print(str(i+1) + " MLSAG: ")
    for j in range(len(sig[i][0])):
        print(str(j) + ": " + str(sig[i][0][j]))
    print("KeyImage: " + str(sig[i][1]))
    print()

'''

print(sc.verifyTX(sig, message))




