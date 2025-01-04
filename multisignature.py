import bitcoin
from bitcoin import SelectParams
from bitcoin.core import (
    b2x, lx, COIN, COutPoint, Hash160,
    CMutableTransaction, CMutableTxIn, CMutableTxOut
)
from bitcoin.core.script import (
    CScript,
    OP_DUP,
    OP_HASH160,
    OP_EQUALVERIFY,
    OP_CHECKSIG,
    SignatureHash,
    SIGHASH_ALL,
    OP_0,
    OP_2,
    OP_CHECKMULTISIG
)
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinSecret, CBitcoinAddress, P2PKHBitcoinAddress, P2SHBitcoinAddress
import os

SelectParams("testnet")

# Generate two random private keys
private_key1 = CBitcoinSecret("cTykYWBtXDBTpE16g5t7WgfmiTG53zWethsWux6sDyGmZVEgg9kb")
private_key2 = CBitcoinSecret("cUGzSMWw24p4G6ei98KCfRw5A31BYa6L2f1bSPukhF7gLtbJdZLP")
public_key1 = private_key1.pub
public_key2 = private_key2.pub
redeem_script = CScript([OP_2, public_key1, public_key2, OP_2, OP_CHECKMULTISIG])
# Create a P2SH address from the redeem script
addr_source = P2SHBitcoinAddress.from_redeemScript(redeem_script)

# Generate another addresses to get exchange
private_key3 = CBitcoinSecret("cPHJQTeTp6f9ZkkGPmkum38jPCi5g3j7ggFAnMo9GtpBtYH9Dfc8")
private_key4 = CBitcoinSecret("cSGnBmdsDodJAFffhT6ACCmbtfPzYDPC8ddvoeoFfsiSqhvmd6CW")
public_key3 = private_key3.pub
public_key4 = private_key4.pub
redeem_script2 = CScript([OP_2, public_key3, public_key4, OP_2, OP_CHECKMULTISIG])
# Create a P2SH address from the redeem script
addr_change = P2SHBitcoinAddress.from_redeemScript(redeem_script2)

# Print out
print("Multisig Address Source:", addr_source)
print("Multisig Address Change:", addr_change)

# Spend from the multisig address
# UTXO info
txid_str = "0eccdfe7e3117539c3338a8a23d6397ae9c039fec028bc6fdf2028875ee57d87"
txid = lx(txid_str)  # Đảo byte
vout = 0
input_amount = 0.00027659

# Create transaction input
txin = CMutableTxIn(COutPoint(txid, vout))

# scriptPubKey for our UTXO
txin_scriptPubKey = CScript([OP_2, public_key1, public_key2, OP_2, OP_CHECKMULTISIG])

# recipient address & amount
addr_dest = P2SHBitcoinAddress("2NCDcZTwiijfeVsyqZjU1j1DGTx1fbAwuiF") # Replace with your address
amount_to_send = 0.00002  # BTC

fee = 0.00024

change_amount = input_amount - amount_to_send - fee
if change_amount < 0:
    raise ValueError("Insufficient balance to cover send + fee!")
else:
    print("Change amount:", change_amount)
    print("Amount to send:", amount_to_send)
    print("Fee:", fee)



txout_send = CMutableTxOut(int(amount_to_send * COIN), addr_dest.to_scriptPubKey())
txout_change = CMutableTxOut(int(change_amount * COIN), addr_change.to_scriptPubKey())

# # create transaction
tx = CMutableTransaction()
tx.nVersion = 2
tx.vin = [txin]
tx.vout = [txout_send, txout_change]

## sign transaction
sighash = SignatureHash(txin_scriptPubKey, tx, inIdx=0, hashtype=SIGHASH_ALL)
sig1 = private_key1.sign(sighash) + bytes([SIGHASH_ALL])
sig2 = private_key2.sign(sighash) + bytes([SIGHASH_ALL])

## set scriptSig
txin.scriptSig = CScript([OP_0, sig1, sig2, redeem_script])

# # Done! Print the transaction
print(b2x(tx.serialize()))


