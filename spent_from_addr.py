import bitcoin
from bitcoin import SelectParams
from bitcoin.core import (
    b2x, lx, COIN, COutPoint, Hash160,
    CMutableTransaction, CMutableTxIn, CMutableTxOut
)
from bitcoin.core.script import (
    CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
)

from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinSecret, CBitcoinAddress, P2PKHBitcoinAddress

# select network
SelectParams("testnet")

# source address
WIF_source = "cTykYWBtXDBTpE16g5t7WgfmiTG53zWethsWux6sDyGmZVEgg9kb" #the private key that you were generated;
privateKey_source = CBitcoinSecret(WIF_source)
publicKey_source = privateKey_source.pub
address_source = P2PKHBitcoinAddress.from_pubkey(publicKey_source)

## change address
WIF_source = "cUGzSMWw24p4G6ei98KCfRw5A31BYa6L2f1bSPukhF7gLtbJdZLP" #the private key that you were generated;
privateKey_source = CBitcoinSecret(WIF_source)
publicKey_source = privateKey_source.pub
address_change = P2PKHBitcoinAddress.from_pubkey(publicKey_source)

print("The Source Address:", address_source)
print("The Change Address:", address_change)


# UTXO info 
txid_str = "6d2f4d11fb3a14c931c3261278ed10c4d8ea707701c2edf90794604a3d62478d" #your txid on web testnet
txid = lx(txid_str)
vout = 1
input_amount = 0.0002765

# create TxIn
txin = CMutableTxIn(COutPoint(txid, vout))

# scriptPubKey for our UTXO
txin_scriptPubKey = CScript([OP_DUP, OP_HASH160, Hash160(publicKey_source), OP_EQUALVERIFY, OP_CHECKSIG])

# recipient address & amount
address_destination = CBitcoinAddress("mpM8FnLScLCQSBzEbETw1Xeb8Q8QTL9EJL") #replace with your bitcoin address
amount_to_send = 0.00005  # BTC

fee = 0.00002

change_amount = input_amount - amount_to_send - fee
if change_amount < 0:
    raise ValueError("The balance is not enough to pay the shipping fee + fees!")

txout_send = CMutableTxOut(int(amount_to_send * COIN), address_destination.to_scriptPubKey())
txout_change = CMutableTxOut(int(change_amount * COIN), address_change.to_scriptPubKey())

# create transaction
tx = CMutableTransaction()
tx.nVersion = 2
tx.vin = [txin]
tx.vout = [txout_send, txout_change]

# sign
sighash = SignatureHash(txin_scriptPubKey, tx, inIdx=0, hashtype=SIGHASH_ALL)
sig = privateKey_source.sign(sighash) + bytes([SIGHASH_ALL])

# attach signature
tx.vin[0].scriptSig = CScript([sig, publicKey_source])

# verify
try:
    VerifyScript(
        tx.vin[0].scriptSig,   
        txin_scriptPubKey,     
        tx,                    
        0,                     
        (SCRIPT_VERIFY_P2SH,)
    )
    print("VerifyScript: SUCCESS")
except Exception as e:
    print("VerifyScript: FAILED -", e)
    exit(1)

# print signed TX (hex)
signed_tx_hex = b2x(tx.serialize())
print("Signed TX (hex):", signed_tx_hex)
