import web3
from wallet import Wallet
from smartContract import SmartContract

class Accounts:

     # a set of (fake) private keys used to generate accounts
    privateViewKeys = [
    "e757c0129539e5bee57dd173eee8192a4399b5221ece5137c44586ec2573c8cb",
    "8d755b8a4878744e0142d8372342ddd0db95afc53b133e4de50aa58cede169ef",
    "222d8e895584e7469be90a61205d28a4d38717b1194cc09c95fe7028bc9a1eae",
    "f02c2d9b88b5f92ec6b36f72291cb99a8dc499c6d1e6ac2c8e6b317da39c7974",
    "cf546eb8b83d148ce3c671ed74de911b58906db1df8974c5cbbc87303c845db4",
    "0a975b7de8d089bdf6faef6ee213af02f7fe100711c93d754db9eb9527b66513",
    "359ce2442612679e57613af799e69df511b405b8c499bcb691268d10f3a2cbc6",
    "2b62f5be803f62a3760e7001594f12e1610394cc6af6830112f6e0d7f1d39342",
    "743da891f24ea784da3459fefcdfbd390ad87c0eef91d80b9d3aeb3392b134bb",
    "0f114d94ec53c994385d26a94e9eee63caf50e0ad6ab6c0f56ec0630d7085d5f",
    ]

    privateSignKeys = [
    "d10167efb1e0221a9cb81cb58f8e75a42a6d8fc47bbf03baba05edc76560b50f",
    "c684e8bc2be2640dd1a138b591841f8024577e5535ac0f76bcb305f97477bb5b",
    "72c3340899c30c006ecd4014e41334ede6aacf4c3780cbeb307fa25ed36269e8",
    "5505c61fbb5b6bfec30426541737d64ed4beb80e78849027c4502a9e99673a9f",
    "cb38e2b6ab36840330de2ba289ae7945c5f347778ef078bc3ced865ebffab01c",
    "e167ee78cf58e88f1a86bfe8ec5ac5f9119151f171465265759042f26f16d6c5",
    "6fc791490f0bbc1b4670dc577548d74e6376143586ab00d3ee40b51ff72d3228",
    "d0c5e79cff2fcdce5e21d276f96cd34b3bc8f1ea12da9edd19f6b6f7021258c1",
    "12b9fe9444db0be5dda45f07a5c36aa244bed1417ec630d4b410a7f70cc3f236",
    "34e3148cb7adb428a81bb32520da7ae74604527e37b56e629a0669ea57920d99"
    ]

    wallets = []

    w3 = 0

    def  __init__ (self, w3:web3, sc:SmartContract, limit:int = None):

        #adjust number of accounts
        if(limit != None):
            self.privateViewKeys = self.privateViewKeys[:limit]
            self.privateSignKeys = self.privateSignKeys[:limit]

        print("-"*42 + "\nCreating Accounts\n" + "-"*42)

        #create public key for each private key
        for viewKey, signKey in zip(self.privateViewKeys, self.privateSignKeys):
            #store public key in accounts array
            wallet = Wallet(w3, viewKey, signKey, sc)
            self.wallets.append(wallet)
            #print("viewKey: " + wallet.getViewKey())
            #print("signKey: " + wallet.getSignKey())
            #print()
      
        print(("-"*42 + "\n{} Accounts created\n" + "-"*42).format(len(self.wallets)))

    def getPrivateKeys(self):
        return self.privateKeys

    def getWallets(self):
        return self.wallets

    def getWallet(self, accountNumber:int)->Wallet:
        return self.wallets[accountNumber]
