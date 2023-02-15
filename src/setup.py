import web3
from accounts import Accounts

#connect to local blockchain
w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:7545'))

#create set of test accounts
accounts = Accounts(w3)


