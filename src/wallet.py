import web3


class Wallet:

    w3 = 0

    viewAccount = 0
    signAccount = 0

    publicViewKey = 0
    publicSignKey = 0

    privateViewKey = 0
    privateSignKey = 0

    def __init__(self, w3:web3, privateViewKey, privateSignKey) -> None:
        
        self.w3 = w3

        self.privateViewKey = privateViewKey
        self.privateSignKey = privateSignKey

        self.viewAccount = w3.eth.account.privateKeyToAccount(self.privateViewKey)
        self.signAccount = w3.eth.account.privateKeyToAccount(self.privateSignKey)

        self.publicViewKey = self.viewAccount.address
        self.publicSignKey = self.signAccount.address


    def getViewKey(self):
        return self.publicViewKey

    def getSignKey(self):
        return self.publicSignKey

    def getViewAccount(self):
        return self.viewAccount

    def getSignAccount(self):
        return self.signAccount