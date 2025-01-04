# ----------------------------------------------------------
# 1) IMPORT CÁC THÀNH PHẦN CẦN THIẾT
# ----------------------------------------------------------
import sys

# Thư viện chính liên quan đến Bitcoin
import bitcoin
import bitcoin.core
import bitcoin.core.script
import bitcoin.core.scripteval
import bitcoin.wallet
from bitcoin import SelectParams
from bitcoin.core import (
    b2x,
    lx,
    COIN,
    COutPoint,
    Hash160,
    CMutableTransaction,
    CMutableTxIn,
    CMutableTxOut
)
from bitcoin.core.script import (
    CScript,
    SignatureHash,
    SIGHASH_ALL,
    OP_DUP,
    OP_HASH160,
    OP_EQUALVERIFY,
    OP_CHECKSIG,
    OP_0,
    OP_2,
    OP_CHECKMULTISIG
)
from bitcoin.wallet import (
    CBitcoinSecret,
    P2SHBitcoinAddress
)

# ----------------------------------------------------------
# 2) CHỌN TESTNET
# ----------------------------------------------------------
SelectParams("testnet")


# ----------------------------------------------------------
# 3) HÀM HỖ TRỢ: TẠO ĐỊA CHỈ MULTISIG (2-of-2)
# ----------------------------------------------------------
def create_multisig_2of2(key_wif1: str, key_wif2: str):
    """
    Tạo P2SH 2-of-2 multisig address từ 2 private key (WIF).
    Trả về:
      - Đối tượng bitcoin.wallet.CBitcoinSecret cho từng khóa
      - Redeem Script
      - Địa chỉ P2SH
    """
    secretA = CBitcoinSecret(key_wif1)
    secretB = CBitcoinSecret(key_wif2)
    pubA = secretA.pub
    pubB = secretB.pub

    # Xây dựng redeem script (2-of-2)
    redeem_script_2of2 = CScript([OP_2, pubA, pubB, OP_2, OP_CHECKMULTISIG])

    # Sinh ra địa chỉ P2SH
    addr_2of2 = P2SHBitcoinAddress.from_redeemScript(redeem_script_2of2)
    return secretA, secretB, redeem_script_2of2, addr_2of2


# ----------------------------------------------------------
# 4) TẠO 2 ĐỊA CHỈ MULTISIG ĐỂ LÀM NGUỒN & TIỀN THỐI
# ----------------------------------------------------------
# Bộ đôi private key để tạo địa chỉ multisig 2-of-2 (nguồn)
keyA_wif = "cPQQh6ieMGZqqpAer5XTgSiY9ycoQX82c5bCW1TPNBqXCSDVMoyF"
keyB_wif = "cPzTwndsuwsy5aNJFADvwoZHtwjjr66mKWWi8BJYg7VUrKZyBnvu"
keyA, keyB, redeemScriptSrc, addrMultiSrc = create_multisig_2of2(keyA_wif, keyB_wif)

# Bộ đôi private key để tạo địa chỉ multisig 2-of-2 (change)
keyC_wif = "cQxmBHEaKW79JoMoZBy6A895VPQT1RTybaBtXTAMf3vv9QyqNpSL"
keyD_wif = "cV2eR7jtfwUXmf8BN75qJ4ZjEMev1PrcFjqXCDfDxsvEgZhWGcVs"
keyC, keyD, redeemScriptChg, addrMultiChg = create_multisig_2of2(keyC_wif, keyD_wif)

print(">>> Multisig-Source Address:", addrMultiSrc)
print(">>> Multisig-Change Address:", addrMultiChg)


# ----------------------------------------------------------
# 5) THIẾT LẬP THÔNG TIN UTXO CẦN CHI TIÊU TỪ MULTISIG-SOURCE
# ----------------------------------------------------------
# Chuỗi txid (hex) mà bạn có UTXO ở đầu ra
rawTxidString = "f4526a2df5d565f220ad0d68100ccba85920fb87de2d8de5c260b65769f748aa"
txid_bytes = lx(rawTxidString)  # đảo thứ tự byte

# Vị trí (vout) của UTXO
index_vout = 0

# Số BTC trong UTXO (để tính fee, tiền thừa, v.v.)
utxo_amount_btc = 0.00027659

# ----------------------------------------------------------
# 6) XÂY DỰNG CÁC OUTPUT (GỒM NGƯỜI NHẬN VÀ "TIỀN THỐI")
# ----------------------------------------------------------
from bitcoin.wallet import P2PKHBitcoinAddress
address_recipient = P2PKHBitcoinAddress("n1CK2qDvF4WMnqAaVjBJZfHw6C8TJjRJdt")
amount_recipient_btc = 0.00002  # BTC muốn gửi

# Phí giao dịch (BTC)
tx_fee_btc = 0.00025

# Tính tiền thừa
change_btc = utxo_amount_btc - amount_recipient_btc - tx_fee_btc
if change_btc < 0:
    print("Số dư không đủ")
    sys.exit(1)

print(">>> Amount to recipient:", amount_recipient_btc)
print(">>> Fee:", tx_fee_btc)
print(">>> Change leftover:", change_btc)

# Xây dựng TxOut cho người nhận
txOutRecipient = CMutableTxOut(
    int(amount_recipient_btc * COIN),
    address_recipient.to_scriptPubKey()
)

# Xây dựng TxOut cho tiền thối (gửi về multisig-change)
txOutChange = CMutableTxOut(
    int(change_btc * COIN),
    addrMultiChg.to_scriptPubKey()
)


# ----------------------------------------------------------
# 7) TẠO VÀ KÝ GIAO DỊCH
# ----------------------------------------------------------
# 7.1) Tạo TxIn (trỏ đến UTXO multisig-source)
txInput = CMutableTxIn(COutPoint(txid_bytes, index_vout))

# 7.2) Gộp thành transaction
finalTx = CMutableTransaction()
finalTx.nVersion = 2
finalTx.vin = [txInput]
finalTx.vout = [txOutRecipient, txOutChange]

# 7.3) Tạo scriptPubKey "đa chữ ký" (dùng cho VerifyScript & tính sigHash)
scriptPubKeySrc = redeemScriptSrc  # chính là redeemScript 2-of-2

# 7.4) Tính SigHash
sigHashValue = SignatureHash(scriptPubKeySrc, finalTx, inIdx=0, hashtype=SIGHASH_ALL)

# 7.5) Ký bằng cả 2 private key (2-of-2)
sigKeyA = keyA.sign(sigHashValue) + bytes([SIGHASH_ALL])
sigKeyB = keyB.sign(sigHashValue) + bytes([SIGHASH_ALL])

# 7.6) Đưa chữ ký + redeem script vào scriptSig
# Lưu ý OP_0 để "né" bug CHECKMULTISIG (đếm key).
finalTx.vin[0].scriptSig = CScript([OP_0, sigKeyA, sigKeyB, redeemScriptSrc])


# ----------------------------------------------------------
# 8) IN RA GIAO DỊCH (HEX) CUỐI CÙNG
# ----------------------------------------------------------
hex_tx = b2x(finalTx.serialize())
print(">>> FINAL SIGNED TRANSACTION (HEX):\n", hex_tx)
