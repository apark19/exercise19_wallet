import sys
import os
import subprocess
import json
import traceback
import web3
from web3.middleware import geth_poa_middleware
from web3 import Web3
from eth_account import Account
import getopt
from hexbytes import HexBytes

import bit
from bit.network import NetworkAPI

# User
import constants


def priv_key_to_account(token_type, key):
    if (token_type=="" or token_type==None):
        raise Exception("token_type is not valid, token_type="+str(token_type))
    if (key=="" or key==None):
        raise Exception("key is not valid, key="+str(key))

    if token_type==constants.ETH:
        return Account.from_key(key)
    elif token_type==constants.BTC_TEST:
        return bit.PrivateKeyTestnet(key) 
    else:
        raise Exception("token_type not supported. Must be ETH, BTC, or BTC_TEST, token_type="+str(token_type))

def create_tx(token_type, account, recipient, amount):
    if (token_type=="" or token_type==None):
        raise Exception("token_type is not valid, token_type="+str(token_type))
    if (recipient=="" or recipient==None):
        raise Exception("recipient is not valid, recipient="+str(recipient))
    if (amount<=0 or amount==None):
        raise Exception("amount is not valid, amount="+str(amount))

    if token_type==constants.ETH:
        nonce=w3.eth.getTransactionCount(account.address)
        tx={ 
            'nonce':nonce,
            'to':recipient,
            'value':w3.toWei(amount,'ether'),
            'gas':200000,
            'gasPrice':w3.toWei('50','gwei')
        }
        return tx
    elif token_type==constants.BTC_TEST:
        return account.create_transaction([(str(recipient),amount,'btc')])
    else:
        return -1

def send_tx(token_type, account, recipient, amount): 
    if (token_type=="" or token_type==None):
        raise Exception("token_type is not valid, token_type="+str(token_type))
    if (recipient=="" or recipient==None):
        raise Exception("recipient is not valid, recipient="+str(recipient))
    if (amount<=0 or amount==None):
        raise Exception("amount is not valid, amount="+str(amount))

    if token_type==constants.ETH:
        return -1
    elif token_type==constants.BTC_TEST:
        tx_hash=create_tx('btc-test',account,recipient,amount)
        result=NetworkAPI.broadcast_tx_testnet(tx_hash)
        return result
    else:
        return -1

def gen_keyset(token, key):
    cur_dir=str(os.getcwd())
    cmd=[cur_dir+"/hd-wallet-derive/hd-wallet-derive.php",
        "--mnemonic='"+str(key)+"'",
        "--coin="+str(token),
        "--numderive=10",
        "--format=json",
        "--cols=path,address,privkey,pubkey",
        "--includeroot",
        "-g"]

    try:
        p=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout,stderr)=p.communicate()

        data=json.loads(stdout)
        return data
    except:
        traceback.print_exc()
        pass

def conf_init(config):
    try:
        with open(config,'r') as file:
            data=file.read()        

        conf=json.loads(data)
        return (conf)
    except:
        traceback.print_exc()
        pass

    return None

def get_keys(seed):
    if (seed=="" or seed==None):
        raise Exception("seed is not valid, seed="+str(seed))
    
    result=dict()
    tmp=gen_keyset('BTC',seed)
    result['btc']=tmp
    
    tmp=gen_keyset('ETH',seed)
    result['eth']=tmp

    tmp=gen_keyset('BTC-test',seed)
    result['btc_test']=tmp

    if len(result)>0:
        return result
    else:
        return None

def usage():
    print('''Usage: python wallet.py -c config -t token_type -i index''')


def main(argv):
    try:
        (opts,args)=getopt.getopt(argv,"hc:t:i:a:")

        config=""
        token_type=""
        index=-1
        amount=-1.0

        for opt,arg in opts:
            if opt=="-c":
                config=str(arg)
            elif opt=="-t":
                token_type=str(arg)
            elif opt=="-i":
                index=int(arg)
            elif opt=="-a":
                amount=float(arg)
            else:
                usage()
        
        if (config=="" or config==None):
            raise Exception("config is not valid, config="+str(config))
        if (token_type=="" or token_type==None):
            raise Exception("token type is not valid, token_type="+str(token_type))
        if (index<0 or index>9):
            raise Exception("index is not valid, index="+str(index))
        if (amount<0.0):
            raise Exception("amount is not valid, amount="+str(amount))        

        conf=conf_init(config)    
        keys=get_keys(conf['seed'][0])
        print(keys)

        if token_type==constants.BTC_TEST:
            acc=priv_key_to_account('btc-test',conf['btc_test_key'])
            print("\n"+str(acc.get_balance('btc'))) 
            print(keys['btc_test'][0]['address']) 
            result=send_tx('btc-test',acc,keys['btc_test'][0]['address'],amount)
        elif token_type==constants.ETH:
            w3=Web3(Web3.HTTPProvider("http://127.0.0.1:7001"))
            w3.middleware_onion.inject(geth_poa_middleware,layer=0)

            acc1="0xa039C2f9997d8978B1B85A02FB6FcFf58429d748"
            acc2="0x34BF41B6269B41A07d97603b6B4Ea5C6069eAf79"
            private_key="2aad86bfd8d83c18f4a372b429d80da806fafbe705f1c208ac423e0ad8c0c0b3"
            nonce=w3.eth.getTransactionCount(acc1)
            print(nonce)

            nonce=w3.eth.getTransactionCount(acc1)
            tx={ 
                'nonce':nonce,
                'to':acc2,
                'value':w3.toWei(amount,'ether'),
                'gas':200000,
                'gasPrice':w3.toWei('50','gwei')
            }
     
            signed=w3.eth.account.signTransaction(tx,private_key)
            tx_hash=w3.eth.sendRawTransaction(signed.rawTransaction)
            print(w3.toHex(tx_hash))          
        else:
            print("error, exiting....")
            return 1       
    except:
        traceback.print_exc() 
        pass

if __name__=="__main__":
    main(sys.argv[1:])

