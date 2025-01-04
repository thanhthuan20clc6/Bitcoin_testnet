# P2PKH Script
import os
from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress

# Cấu hình mạng Testnet
SelectParams('testnet')

# Tạo một private key ngẫu nhiên
private_key = CBitcoinSecret.from_secret_bytes(os.urandom(32))

# Tạo public key và địa chỉ Bitcoin
public_key = private_key.pub
address = P2PKHBitcoinAddress.from_pubkey(public_key)

print("Private Key:", private_key)
print("Public Key:", public_key.hex())
print("Bitcoin Address:", address)
